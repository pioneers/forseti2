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
class Button(Node):

    def __init__(self, index): #TODO: give channel_name
        self.send_channel = "Button%d/Button" % index
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
            #self.button.pressed = not self.button.pressed

    def press(self):
        self.button.pressed = True

    def depress(self):
        self.button.pressed = False


class Motor(LCMNode):

    #TODO: if button pressed and time since button press < 5 seconds, motor should be on, should only be on again if timer ends
    def __init__(self, index): #TODO: give send_channels
        self.index = index
        self.send_channel = "Motor%d/Motor" % index
        self.receive_channel = "LighthouseTimer/LighthouseTime"
        self.motor = forseti2.Motor()
        self.motor.activated = False
        self.lc = lcm.LCM(settings.LCM_URI)
        self.lc.subscribe(self.receive_channel, self.handle_control)
        self.counter = None 
        self.start_time = time.time()
        self.start_thread()
        self.start_thread(target=self.run())

    def handle_control(self, channel, data):
        msg = forseti2.LighthouseTime.decode(data)
        print('Received command', msg.counter) #TODO: check that the timer has stopped before starting motor
        if msg.activated and msg.counter != self.counter and msg.button_index == self.index:
            self.counter = msg.counter
            self.activate()
        else:
            self.deactivate()

    def activate():
        if not self.motor.activated:
            self.motor.activated = True
            self.start_time = time.time()
            print("Motor Activated")

    def deactivate():
        if self.motor.activated:
            self.motor.activated = False
            print("Motor Deactivated")

    def check(self, timeout=5):
        if self.motor.activated and time.time() - self.start_time >= 5:
            self.deactivate()

    def run(self):
        start_time = time.time()
        while True:
            self.check()
            self.lc.publish(self.send_channel, self.motor.encode())
            time.sleep(.03)

def main():
    buttons = [Button(i) for i in range(2)] #automatically starts looping
    motor = [Motor(i)  for i in range(2)]

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
