# -*- coding: utf-8 -*-
"""
forest_driver.py
Created on Thu Mar 27 05:40:16 2014

@author: ajc
"""

from pyfirmata import ArduinoMega
import pyfirmata

import lcm
import forseti2 as fs2
import settings

class Forest:
    def __init__(self, addr, debug=True):
        self.board = None
        self.pins = []
        self.pins.append((22, 24, 26, 2))
        self.pins.append((28, 30, 32, 3))
        self.pins.append((34, 36, 38, 4))
        self.pins.append((40, 42, 44, 5))
        self.pins.append((46, 48, 50, 6))
        self.pins.append((31, 33, 35, 7))
        self.pins.append((37, 39, 41, 8))
        self.pins.append((43, 45, 47, 9))
        if addr is not None:
            self.board = ArduinoMega(addr)
            for b in self.pins:
                self.board.digital[b[3]].mode = pyfirmata.SERVO
                for c in range(3):
                    self.board.digital[b[c]].write(True)

        self.debug = debug

    def _forest_cmd_handler(self, channel, data):
        msg = fs2.forest_cmd.decode(data)
        if self.debug:
            print("Received message on channel \"%s\"" % channel)
            print("   header.seq   = %s" % str(msg.header.seq))
            print("   header.time   = %s" % str(msg.header.time))
            print("   lights   = %s" % str(msg.lights))
            print("   servos   = %s" % str(msg.servos))
        for b in range(8):
            for c in range (3):
                self.board.digital[self.pins[b][c]].write(not msg.lights[b][c])
            self.board.digital[self.pins[b][3]].write(msg.servos[b])

if __name__ == '__main__':
    print "starting forest_driver.py"
    lc = lcm.LCM(settings.LCM_URI)
    f = Forest('/dev/ttyACM0')
    sub = lc.subscribe("/forest/cmd", f._forest_cmd_handler)

    while True:
        lc.handle()
