# -*- coding: utf-8 -*-

import time
from pyfirmata import ArduinoMega, util
import pyfirmata

board = ArduinoMega('/dev/ttyUSB0')

RED=0
ORANGE=1
GREEN=2
SERVO=3

combinations = []
combinations.append((22, 23, 24, 2))
combinations.append((25, 26, 27, 3))
combinations.append((28, 29, 30, 4))
combinations.append((31, 32, 33, 5))
combinations.append((34, 35, 36, 6))
combinations.append((37, 38, 39, 7))
combinations.append((40, 41, 42, 8))
combinations.append((43, 44, 45, 9))

stime=.5
for combo in combinations:
    board.digital[combo[SERVO]].mode = pyfirmata.SERVO
while True:
    for i in range(3):
        for combo in combinations:
            board.digital[combo[i]].write(False)
            board.digital[combo[SERVO]].write(0)
        time.sleep(stime)
        for combo in combinations:
            board.digital[combo[i]].write(True)
            board.digital[combo[SERVO]].write(180)
        time.sleep(stime)
