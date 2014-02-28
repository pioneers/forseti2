# -*- coding: utf-8 -*-

import time
from pyfirmata import ArduinoMega, util
import pyfirmata

board = ArduinoMega('/dev/ttyUSB1')
board.digital[2].mode = pyfirmata.SERVO
while True:
    for i in (22, 24, 26):
        board.digital[i].write(True)
    board.digital[2].write(0)
    time.sleep(1)
    for i in (22, 24, 26):
        board.digital[i].write(False)
    board.digital[2].write(180)
    time.sleep(1)