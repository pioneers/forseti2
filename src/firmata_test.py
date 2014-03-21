# -*- coding: utf-8 -*-

import time
from pyfirmata import ArduinoMega, util
import pyfirmata

board = ArduinoMega('/dev/ttyACM0')

RED=0
ORANGE=1
GREEN=2
SERVO=3

combinations = []
combinations.append((22, 24, 26, 2))
combinations.append((28, 30, 32, 3))
combinations.append((34, 36, 38, 4))
combinations.append((40, 42, 44, 5))
combinations.append((46, 48, 50, 6))
combinations.append((31, 33, 35, 7))
combinations.append((37, 39, 41, 8))
combinations.append((43, 45, 47, 9))

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
