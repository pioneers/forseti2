#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
timer.py
Created on Wed Apr 24 12:00:00 2013

@author: RJ


"""
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
import re
import LCMNode

Node = LCMNode.Node
LCMNode = LCMNode.LCMNode

class Timer(object):

    def __init__(self):
        self.start_time = time.time()
        self.current_time = 0
        self.running = False

    def time(self):
        if self.running:
            self.current_time = time.time() - self.start_time
        return self.current_time

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
        return self

    def pause(self):
        if not self.running:
            return self.current_time
        self.running = False
        self.current_time = time.time() - self.start_time
        return self

#TODO: Subscribe to Peter's two button channels. Publish which team pushed button
class LighthouseTimer(LCMNode):
    def __init__(self, lc):
        self.lc = lc
        self.timer = Timer()
        self.stage_name = "Setup"
        self.buttons = [False, False]
        self.lc.subscribe(r"Button[0-9]/Button", self.handle_control)
        self.lc.subscribe("Timer/Time", self.handle_time)
        self.start_thread()
        self.counter = random.randint(0, 1000000)

    def run(self):
        while 1:
            time.sleep(0.3)
            msg = forseti2.LighthouseTime()

            if self.stage_name in ["Setup", "Paused", "End"]:
                self.timer.pause()
                msg.enabled = False
                msg.available = False
                msg.counter = self.counter
                msg.time_left = 0
                self.lc.publish('LighthouseTimer/LighthouseTime', msg.encode())
                self.clear()
                continue
                
            if self.buttons[0]:
                self.buttons[0] = False
                if not self.timer.running:
                    self.counter += 1
                    self.timer.start()
                    msg.button_index = 0

            if self.buttons[1]:
                self.buttons[1] = False
                if not self.timer.running:
                    self.counter += 1
                    self.timer.start()
                    msg.button_index = 1
            self.clear()

            lighthouse_time = self.timer.time()
            time_left = 10*1000 - lighthouse_time*1000
            if time_left <= 0:
                self.timer.pause()
            
            msg.enabled = True
            msg.counter = self.counter
            if not self.timer.running:
                msg.time_left = 10*1000
                msg.available = True
                self.lc.publish('LighthouseTimer/LighthouseTime', msg.encode())
            else:
                msg.time_left = time_left
                msg.available = False
                self.lc.publish('LighthouseTimer/LighthouseTime', msg.encode())

    def press(self, index, pressed):
        if pressed:
            self.buttons[index] = True

    def clear(self):
        self.buttons = [False, False]

    def handle_control(self, channel, data):
        msg = forseti2.Button.decode(data)
        match = re.match(r"Button([0-9])/Button", channel)
        if match:
            self.press(int(match.groups()[0]), msg.pressed)

    def handle_time(self, channel, data):
        msg = forseti2.Time.decode(data)
        self.stage_name = msg.stage_name

def main():
    lc = lcm.LCM(settings.LCM_URI)
    timer = LighthouseTimer(lc)
    timer.run()


if __name__ == '__main__':
    main()
