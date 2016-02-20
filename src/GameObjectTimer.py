#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
timer.py
Created on Wed Apr 24 12:00:00 2013

@author: kyle


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
import LCMNode

Node = LCMNode.Node
LCMNode = LCMNode.LCMNode

class Timer(object):

    def __init__(self):
        self.start_time = time.time()
        self.current_time = self.start_time
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


class LighthouseTimer(LCMNode):
    def __init__(self, lc):
        self.lc = lc
        self.timer = Timer()
        self.stage_name = ""
        self.lc.subscribe("Button/Button", self.handle_control)
        self.lc.subscribe("Timer/Time", self.handle_time)
        self.button_pressed = True

    def run(self):
        while 1:
            time.sleep(0.3)
            if self.stage_name == "Paused" or self.stage_name == "End":
                return
            msg = forseti2.LighthouseTime()
            if self.button_pressed:
                self.timer.start()
            lighthouse_time = int(self.timer.time())
            if lighthouse_time > 10:
                msg.lighthouse_on_time = 0
                msg.is_lighthouse_on = "Lighthouse is available"
                self.lc.publish('GameObjectTimer/LighthouseTime', msg.encode())
                self.timer.pause()
            else:
                msg.lighthouse_on_time = lighthouse_time * 1000
                msg.is_lighthouse_on = "Lighthouse is unavailable"
                self.lc.publish('GameObjectTimer/LighthouseTime', msg.encode())
         

    def handle_control(self, channel, data):
        msg = forseti2.Button.decode(data)
        self.button_pressed = msg.pressed 

    def handle_time(self,channel,data):
        msg = forseti2.Time.decode(data)
        self.stage_name = msg.stage_name

def main():
    lc = lcm.LCM(settings.LCM_URI)
    timer = LighthouseTimer(lc)
    timer.run()


if __name__ == '__main__':
    main()
