# -*- coding: utf-8 -*-
"""
forest_driver.py
Created on Thu Mar 27 05:40:16 2014

@author: ajc
"""

from pyfirmata import ArduinoMega
import pyfirmata
import sys
import re
import lcm
import forseti2
import settings
import time
from LCMNode import Node, LCMNode

class StatusLights(LCMNode):
    def __init__(self, lc, addr, debug=True):
        self.lc = lc
        self.board = None
        self.lights = []

        # 
        # pin 53 used as placeholder because we don't support buzzers yet
        #                  (r,  y,  g,  b )
        self.lights.append((22, 23, 24, 53))
        self.lights.append((25, 26, 27, 53))
        self.lights.append((28, 29, 30, 53))
        self.lights.append((31, 32, 33, 53))
        self.lights.append((34, 35, 36, 53))
        self.lights.append((37, 38, 39, 53))
        self.lights.append((40, 41, 42, 53))
        self.lights.append((43, 44, 45, 53))
        if addr is not None:
            self.board = ArduinoMega(addr)
            for r, y, g, b in self.lights:
                self.board.digital[r].write(1)
                self.board.digital[y].write(1)
                self.board.digital[g].write(1)
                self.board.digital[b].write(1)

        self.debug = debug

        self.lc.subscribe(r"StatusLight([0-9]+)/StatusLight", self.handle_update)
        self.start_thread()

    def handle_update(self, channel, data):
        match = re.match(r"StatusLight([0-9]+)/StatusLight", channel)
        if not match:
            return
        light = int(match.groups()[0])
        if light >= len(self.lights):
            return

        msg = forseti2.StatusLight.decode(data)
        if self.debug:
            print("Received message on channel \"%s\"" % channel)
            print("   red    = %s" % str(msg.red))
            print("   yellow = %s" % str(msg.yellow))
            print("   green  = %s" % str(msg.green))
            print("   buzzer = %s" % str(msg.buzzer))

        r, y, g, b = self.lights[light]
        self.board.digital[r].write(0 if msg.red else 1)
        self.board.digital[y].write(0 if msg.yellow else 1)
        self.board.digital[g].write(0 if msg.green else 1)
        self.board.digital[b].write(0 if msg.buzzer else 1)

if __name__ == '__main__':
    print "starting status_lights.py"
    lc = lcm.LCM(settings.LCM_URI)
    lights = StatusLights(lc, sys.argv[1], False)
    print "Ready to receive commands"
    #sub = lc.subscribe(r"StatusLight([0-9])/StatusLight", f._forest_cmd_handler)

    while True:
        time.sleep(1)
