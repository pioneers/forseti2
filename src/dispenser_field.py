#!/usr/bin/env python2.7

"""
This node controls the real field elements
"""

import lcm
import forseti2 as fs2
import IPython.display
import pygame
import time
import math
import threading
import serial

def pololu_drive(serial, device, channel, target):
    """ Drives a servo on a maestro using the pololu protocol.
    SERIAL is the serial device the maestro is attached to.
    DEVICE is the maestro device number. (default 12)
    CHANNEL is the servo's channel number [1...6] on micromaestro.
    TARGET is the pulse width in microseconds.
    """
    serial.write(chr(0xAA)) # 0xAA
    serial.write(chr(device))
    serial.write(chr(4))
    serial.write(chr(channel))
    serial.write(chr((target*4) & 0x7F))
    serial.write(chr(((target*4) >> 7) & 0x7F))

class DispenserHW:
    def __init__(self, team, ser):
        self.team = team
        self.ser = ser
        self.debug = True
        
    def _dispenser_cmd_handler(self, channel, data):
        msg = fs2.dispenser_cmd.decode(data)
        if self.debug:
            print("Received message on channel \"%s\"" % channel)
            print("   header.seq   = %s" % str(msg.header.seq))
            print("   header.time   = %s" % str(msg.header.time))
            print("   team   = %s" % str(msg.team))
            print("   state   = %s" % str(msg.state))
        if msg.team == self.team:
            for i in range(4):
                setpoint = 0
                if msg.state[i] is fs2.dispenser_cmd.STATE_HELD:
                    setpoint = 2300
                else:
                    setpoint = 500
                pololu_drive(self.ser, 12, i, setpoint)

        
if __name__ == '__main__':
    try:
        lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
        serial = serial.Serial("/dev/ttyUSB0", baudrate=250000)
        dd = DispenserHW(fs2.dispenser_cmd.TEAM_GOLD,
            serial)
        sub = lc.subscribe("sprocket/field", dd._dispenser_cmd_handler)
        while True:
            lc.handle()

    except KeyboardInterrupt:
        raise
    except :
        raise

