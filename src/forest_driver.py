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

        # green
        #
        self.pins.append((23, 24, 22, 2))
        self.pins.append((26, 27, 25, 3))
        self.pins.append((29, 30, 28, 4))
        self.pins.append((32, 33, 31, 5))
        self.pins.append((35, 36, 34, 6))
        self.pins.append((38, 39, 37, 7))
        self.pins.append((41, 42, 40, 8))
        self.pins.append((44, 45, 43, 9))
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
    f = Forest('/dev/ttyUSB0')
    print "Ready to receive commands"
    sub = lc.subscribe("/forest/cmd", f._forest_cmd_handler)

    while True:
        lc.handle()
