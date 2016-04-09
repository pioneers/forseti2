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
import serial
import pyfirmata
from usb.core import USBError

Node = LCMNode.Node
LCMNode = LCMNode.LCMNode

class Button(Node):

    def __init__(self, lc, index, arduino_path=None, use_arduino=False):
        self.use_arduino = use_arduino
        self.send_channel = "Button%d/Button" % index
        self.button = forseti2.Button()
        self.pressed = False
        self.lc = lc
        if self.use_arduino:
            self.ser = serial.Serial(arduino_path, 9600)
            # self.board = pyfirmata.Arduino(arduino_path)
            # self.pin = self.board.get_pin('d:4:i')
            # self.it = pyfirmata.util.Iterator(self.board)
            # self.it.start()
            #self.pin.enable_reporting()
        self.start_thread()
        self.start_time = time.time()


    def check_button(self):
        if self.use_arduino and self.ser.inWaiting() > 0:
            byte = self.ser.read(self.ser.inWaiting())[-1]
            reading = int(str(byte))
            self.update(1-reading)


    def _loop(self):
        while True:
            time.sleep(0.1)
            self.check_button()
            if time.time() - self.start_time > .1:
                #print(self.pin.read())
                self.start_time = time.time()
                #print(self.pressed)
                self.button.pressed = self.pressed
                # if self.button.pressed:
                #     print("pressed! %d" % random.randint(0, 100))
                self.clear()
                self.lc.publish(self.send_channel, self.button.encode())

    def clear(self):
        self.pressed = False

    def update(self, pressed):
        if pressed:
            self.pressed = True



class Motor(Node):

    def __init__(self, lc, index, grizzly_addr=None, use_grizzly=False):
        self.index = index
        self.send_channel = "Motor%d/Motor" % index
        self.receive_channel = "LighthouseTimer/LighthouseTime"
        self.motor = forseti2.Motor()
        self.motor.activated = False
        self.lc = lc
        self.lc.subscribe(self.receive_channel, self.handle_control)
        self.counter = None 
        self.start_time = time.time()
        self.start_thread(target=self.run)
        self.use_grizzly = use_grizzly
        self.grizzly_addr = grizzly_addr
        if self.grizzly_addr is None:
            self.use_grizzly = False
        if self.use_grizzly:
            self.grizzly = grizzly.Grizzly(self.grizzly_addr)
            self.grizzly.set_mode(grizzly.ControlMode.NO_PID, grizzly.DriveMode.DRIVE_COAST)
            self.grizzly.limit_acceleration(1)
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
            if self.use_grizzly:
                print("target set")
                self.grizzly.set_target(100)
            print(time.strftime('Motor Activated at %l:%M:%S %p'))

    def deactivate(self):
        if self.motor.activated:
            self.motor.activated = False
            if self.use_grizzly:
                self.grizzly.set_target(0)
            print(time.strftime('Motor Deactivated at %l:%M:%S %p'))

    def check(self, timeout=5):
        try:
            if self.motor.activated and time.time() - self.start_time >= timeout:
                self.deactivate()
        except USBError as e:
            print("GRIZZLY %d CRASHED!" % self.grizzly_addr)
            time.sleep(0.4)
            self.grizzly = grizzly.Grizzly(self.grizzly_addr)
            self.grizzly.set_mode(grizzly.ControlMode.NO_PID, grizzly.DriveMode.DRIVE_COAST)
            self.grizzly.limit_acceleration(1)
            self.grizzly.set_target(0)
    def run(self):
        start_time = time.time()
        while True:
            self.check(10)
            #self.lc.publish(self.send_channel, self.motor.encode())
            time.sleep(.03)

class LightHouseStatusLight(Node):

    def __init__(self, lc, index):
        self.index = index
        self.receive_channel = "LighthouseTimer/LighthouseTime"
        self.send_channel = "StatusLight%d/StatusLight" % (index + 4)
        self.lc = lc
        self.lc.subscribe(self.receive_channel, self.handle_lighthouse_time)
        self.lc.subscribe("Button%d/Button" % index, self.handle_button)
        self.counter = None 
        self.start_time = time.time()


        self.red = False
        self.yellow = False
        self.green = False
        self.buzzer = False
        self.green_timeout = 3
        self.start_thread(target=self.run)                        
    # def deactivateStatusLight(self):
    #     if self.statusLight.activated:
    #         self.statusLight.activated = False
    #         self.pin6.write(0)
    #         self.pin7.write(0)
    #         print(time.strftime('Status Light deactivated at %l:%M:%S %p'))
            
    # def activateStatusLight(self):
    #     if not self.statusLight.activated:
    #         self.statusLight.activated = True
    #         self.start_time = time.time()
    #         print(time.strftime('Status Light Activated at %l:%M:%S %p'))
    
    def check_timeout(self, timeout=10):
        if self.green and time.time() - self.start_time >= timeout:
            self.green = False      

    def handle_lighthouse_time(self, channel, data):
        msg = forseti2.LighthouseTime.decode(data)
        if msg.enabled and not msg.available:


            if msg.button_index == self.index:
                if msg.counter != self.counter:
                    self.counter = msg.counter
                    self.green = True
                    self.start_time = time.time()
            else:
                self.green = False
            self.yellow = True
        else:
            self.yellow = False
            self.green = False
        self.update_light()

    def handle_button(self, channel, data):
        msg = forseti2.Button.decode(data)
        if msg.pressed:
            self.red = True
        else:
            self.red = False
        self.update_light()

    def update_light(self):
        msg = forseti2.StatusLight()
        msg.red = self.red
        msg.yellow = self.yellow
        msg.green = self.green
        msg.buzzer = self.buzzer
        self.lc.publish(self.send_channel, msg.encode())

    def run(self):
        start_time = time.time()
        while True:
            #self.check_timeout(self.green_timeout)
            self.update_light()
            time.sleep(.3)


def main():
    lc = lcm.LCM(settings.LCM_URI)

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--button', action='append', nargs='+', metavar=('index', 'arduino_path'), help="create a button with index and arduino serial path")
    parser.add_argument('-m', '--motor', action='append', nargs='+', metavar=('grizzly_id'), help="create a motor with grizzly id")
    parser.add_argument('-l', '--light', action='append', nargs='+', metavar=('index'), help="create a node that sends signals to the status light driver for specified lighthouse")
    args = parser.parse_args()
    if args.button:
        buttons = [Button(lc, int(button[0]), button[1], True) for button in args.button]
    if args.motor:
        motors = [Motor(lc, 0, int(motor[0]), True) for motor in args.motor]
    if args.light:
        lights = [LightHouseStatusLight(lc, int(light[0])) for light in args.light]
    while True:
        lc.handle()
        time.sleep(.01)

    #button0 = Button(0, "/dev/tty.usbmodem1421", True)
    #buttons = [Button(i) for i in range(2)] #automatically starts looping
    #motors = [Motor(0, 0, True), Motor(1, 1, False)]

if __name__ == '__main__':
    main()
