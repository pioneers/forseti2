#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
timer.py
Created on Wed Apr 24 12:00:00 2013

@author: RJ


"""
from __future__ import print_function

import forseti2
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


#TODO: Subscribe to Peter's two button channels. Publish which team pushed button
class LighthouseTimer(LCMNode):
    def __init__(self, lc):
        self.lc = lc
        self.lc.subscribe(r"LiveScore/ScoreDelta", self.handle_delta)
        self.start_thread()

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
