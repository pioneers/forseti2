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

class Button(LCMNode):

    def __init__(self):
    	self.send_channel = "Button/Press"
        self.button = LCM.Button()
        self.pressed = False
        self.lc = lcm.LCM(settings.LCM_URI)

    def run(self):
    	if (self.button.pressed):
    		self.button = self.button.encode()
    		while True:
				lc.publish(send_channel, self.button)
				self.button.pressed = not self.button.pressed

	def press(self):
		self.button.pressed = True

	def depress(self):
		self.button.pressed = False


class Motor(LCMNode):

    def __init__(self):
    	self.send_channel = "Motor/Activate"
    	self.receive_channel = "Motor/Control"
        self.motor = LCM.Motor()
        self.activated = False
        self.lc = lcm.LCM(settings.LCM_URI)
        self.lc.subscribe(receive_channel, self.handle_control) 
        # subscribe channel same or different from publish?

    def handle_control(self, channel, data):
    	msg = forseti2.TimeControl.decode(data)
        print('Received command', msg.command_name)
        func = {
            'activate': self.activate,
            'deactivate': self.deactivate,
        }[msg.command_name]
        func()

    def run(self):
    	if (self.motor.activated):
    		self.motor = self.motor.encode()
    		while True:
				lc.publish(send_channel, self.motor)
				self.motor.activated = not self.motor.activated

	def deactivate(self):
		self.motor.activated = False

	def activate(self):
		self.motor.activated = True


def main():
	button = Button()
	motor = Motor()
	button.run()
	#motor.run()


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
