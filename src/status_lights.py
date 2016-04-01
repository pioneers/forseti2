from pyfirmata import ArduinoMega, util
import time
import sys
def blink(board, pin):
    board.digital[pin].write(0)
    time.sleep(1)
    board.digital[pin].write(1)

board = ArduinoMega(sys.argv[1])
for i in range(22, 54):
    board.digital[i].write(1)

reds = [43, 40, 37]
yellows = [44, 41, 38]
greens = [45, 42, 39]
while True:
    for color in (reds, yellows, greens):
        for pin in color:
            board.digital[pin].write(0)
        time.sleep(.3)
    for color in (reds, yellows, greens):
        for pin in color:
            board.digital[pin].write(1)
        time.sleep(.3)
    #blink(board, int(raw_input("pin?")))