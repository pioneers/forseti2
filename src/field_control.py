from __future__ import print_function
import forseti2
import configurator
import json
import lcm
import threading
import time
import random
import os
import settings
import util
import LCMNode

Node = LCMNode.Node
LCMNode = LCMNode.LCMNode
# changes here go to network_monitor, lighthouse timer 
# lcm channel names are "[Class-name]/[.lcm file name]"
class Game_Button(Node):

    def __init__(self, channel_name): #TODO: give channel_name
    	self.send_channel = channel_name
        self.button = forseti2.Button()
        self.button.pressed = False
        self.lc = lcm.LCM(settings.LCM_URI)
        self.start_thread() #runs overridden loop function from LCMNode.py

    #TODO: check the button
    def checkButton(self):
        return self.button.pressed

    def _loop(self):
		while True:
            time.sleep(0.3)
			self.lc.publish(self.send_channel, self.button.encode())
			self.button.pressed = not self.button.pressed

    def press(self):
        self.button.pressed = True

    def depress(self):
        self.button.pressed = False


class Game_Motor(LCMNode):

    #TODO: if button pressed and time since button press < 5 seconds, motor should be on, should only be on again if timer ends
    def __init__(self, channel_name): #TODO: give send_channels
    	self.send_channel = channel_name
    	self.receive_channel = "Timer/Time"
        self.motor = forseti2.Motor()
        self.motor.activated = False
        self.lc = lcm.LCM(settings.LCM_URI)
        self.lc.subscribe(self.receive_channel, self.handle_control)
        self.counter = None 

    def handle_control(self, channel, data):
    	msg = forseti2.Time.decode(data)
        print('Received command', msg.counter) #TODO: check that the timer has stopped before starting motor
        if msg.counter != self.counter:
            self.motor.activated = True
        else:
            self.motor.activated = False

    def run(self):
        start_time = time.time()
        elapsed_time = 0
        while True and self.motor.activated:
		    while elapsed_time < 5: #TODO: add time set amount for running motor 
                elapsed_time = time.time() - start_time
			    self.lc.publish(self.send_channel, self.motor.encode())

def main():
    button = Game_Button("Game_Button/Button") #automatically starts looping
    motor = Game_Motor("Game_Motor/Motor") 
    motor.run() #runs 

if __name__ == '__main__':
    main()
"""import lcm 
import forseti2
import settings
import time
#CREATE TWO OBJECTS FOR BUTTON AND MOTOR EXTEND LCMNODE 
#PUT CHANNEL NAME AS PROPERTY 
#PUT INFINITE LOOP IN A RUN METHOD
lc = lcm.LCM(settings.LCM_URI)
#creating two packets for different presses
pressed_button = LCM.Button()
pressed_button.pressed = True
pressed_button.encode()

unpressed_button = LCM.Button()
unpressed_button.pressed = False
unpressed_button.encode()

#creating two packets for different motor states
activated_motor = LCM.Motor()
activated_motor.activated = True
activated_motor.encode()

unactivated_motor = LCM.Motor()
unactivated_motor.activated = False
unactivated_motor.encode()

button_state = True
motor_state = True
pressed = True
activate = True

def handle_motor(channel, data):
    pass

lc.subscribe('Motor', self.handle_motor)
while True:
    if button_state:
        lc.publish("Button/Press", pressed_button if pressed else unpressed_button)
        button_state = not button_state
        pressed = not pressed
    else: 
        lc.publish("Motor", activated_motor if activate else unactivated_motor)
        motor_state = not motor_state
        activate = not activate
        """
