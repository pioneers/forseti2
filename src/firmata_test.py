# -*- coding: utf-8 -*-

import time
from pyfirmata import ArduinoMega, util
import pyfirmata

board = ArduinoMega('/dev/ttyUSB0')
board.digital[2].mode = pyfirmata.SERVO
stime=.05
while True:
    for i in (26, 24, 22):
        board.digital[i].write(False)
        time.sleep(stime)
        board.digital[i].write(True)
        time.sleep(stime)

    # for i in (24):
    board.digital[24].write(False)
    time.sleep(stime)
    board.digital[24].write(True)
    time.sleep(stime)
    

    # board.digital[2].write(0)
    #time.sleep(.05)
    #for i in (22, 24, 26):

    # board.digital[2].write(180)
   