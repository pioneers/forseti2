from __future__ import print_function
import argparse
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
import grizzly
import pyfirmata

Node = LCMNode.Node
LCMNode = LCMNode.LCMNode

class Button(Node):

    def __init__(self, index, arduino_path=None, use_arduino=False):
        self.use_arduino = use_arduino
        self.send_channel = "Button%d/Button" % index
        self.button = forseti2.Button()
        self.pressed = False
        self.lc = lcm.LCM(settings.LCM_URI)
        if self.use_arduino:
            self.board = pyfirmata.Arduino(arduino_path)
            self.pin = self.board.get_pin('d:4:i')
            self.it = pyfirmata.util.Iterator(self.board)
            self.it.start()
            self.pin.enable_reporting()
        self.start_thread()
        self.start_time = time.time()


    def check_button(self):
        if self.use_arduino:
            self.update(self.pin.read())

    def _loop(self):
        while True:
            time.sleep(0.05)
            self.check_button()
            if time.time() - self.start_time > .3:
                self.start_time = time.time()
                #print(self.pressed)
                self.button.pressed = self.pressed
                self.clear()
                self.lc.publish(self.send_channel, self.button.encode())

    def clear(self):
        self.pressed = False

    def update(self, pressed):
        if pressed:
            self.pressed = True



class Motor(LCMNode):

    def __init__(self, index, grizzly_addr=None, use_grizzly=False):
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
        if use_grizzly:
            self.grizzly = grizzly.Grizzly(grizzly_addr)
            self.grizzly.set_mode(ControlMode.NO_PID, DriveMode.DRIVE_BRAKE)
            self.grizzly.set_target(0)

    def handle_control(self, channel, data):
        msg = forseti2.LighthouseTime.decode(data)
        # turns out there's only one shooter for now, so we can bypass this check
        if msg.button_index == self.index or True:
            if msg.enabled and not msg.available: 
                if msg.counter != self.counter:
                    self.counter = msg.counter
                    self.activate()
            else:
                self.deactivate()

    def activate(self):
        if not self.motor.activated:
            self.motor.activated = True
            self.start_time = time.time()
            if use_grizzly:
                self.grizzly.set_target(100)
            print(time.strftime('Motor Activated at %l:%M:%S %p'))

    def deactivate(self):
        if self.motor.activated:
            self.motor.activated = False
            if use_grizzly:
                self.grizzly.set_target(0)
            print(time.strftime('Motor Deactivated at %l:%M:%S %p'))

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
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--button', action='append', nargs='+', metavar=('index', 'arduino_path'), help="create a button with optional arduino location")
    parser.add_argument('-m', '--motor', action='append', nargs='+', metavar=('index', 'grizzly_id'), help="create a motor with optional grizzly id")
    args = parser.parse_args()
    if args.button:
        buttons = [Button(int(button[0]), button[1], True) if len(button) > 1 else Button(int(button[0])) for button in args.button]
    if args.motor:
        motors = [Motor(int(motor[0]), motor[1], True) if len(motor) > 1 else Motor(int(motor[0])) for motor in args.motor]
    #button0 = Button(0, "/dev/tty.usbmodem1421", True)
    #buttons = [Button(i) for i in range(2)] #automatically starts looping
    #motors = [Motor(0, 0, True), Motor(1, 1, False)]

if __name__ == '__main__':
    main()
