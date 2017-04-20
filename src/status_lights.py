from __future__ import print_function
import argparse
import forseti2
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

# NEW CLASS For sending messages to drivers
class DriverStatusLight(Node):

    def __init__(self, lc, index):
        self.index = index
        self.lc = lc
        self.receive_channel = "Robot%d/RobotStatus" % (index)
        self.lc.subscribe(self.receive_channel, self.handle_robot)
        self.send_channel = "StatusLight%d/StatusLight" % (index)
        self.red = True
        self.green = False
        self.yellow = False
        self.buzzer = False
        self.start_thread(target=self.run)

    def handle_robot(self, channel, data):
        msg = forseti2.RobotState.decode(data)
        print (msg)
        if msg.connected != "Disconnected":
            self.red = False
            self.green = True
            self.update_light()

    def update_light(self):
        msg = forseti2.StatusLight()
        msg.red = self.red
        msg.yellow = self.yellow
        msg.green = self.green
        msg.buzzer = self.buzzer
        self.lc.publish(self.send_channel, msg.encode())

    def run(self):
        while True:
            self.update_light()
            time.sleep(.3)

#END CHANGES

def main():
    lc = lcm.LCM(settings.LCM_URI)

    #lighthouse_lights = [LightHouseStatusLight(lc, 0), LightHouseStatusLight(lc, 1)]
    dsl = [DriverStatusLight(lc, 0)]
    while True:
        lc.handle()
        time.sleep(.01)


if __name__ == '__main__':
    main()
