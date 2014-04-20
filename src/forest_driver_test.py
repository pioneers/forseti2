# -*- coding: utf-8 -*-
"""
forest_driver_test.py
Created on Thu Mar 27 05:52:57 2014

@author: ajc
"""

import lcm
import time
import forseti2 as fs2
import settings

STROBE_ALL = False

lc = lcm.LCM(settings.LCM_URI)

msg = fs2.forest_cmd()

msg.header = fs2.header()
msg.header.seq = 0
msg.header.time = time.time()
for branch in range (8):
    for color in range (3):
        msg.lights[branch][color] = False
    msg.servos[branch] = 0


def send_msg(m):
    m.header.seq+=1
    m.header.time = time.time()
    print('fs2.forest_cmd:')
    print('    header.seq=' + str(m.header.seq))
    print('    header.time=' + str(m.header.time))
    print('    lights=' + str(m.lights))
    print('    servos=' + str(m.servos))
    lc.publish("/forest/cmd", m.encode())

stime = 1
t2 = .05
t3 = .1
while True:
    if STROBE_ALL:
        for branch in range(8):
            for color in range (3):
                msg.lights[branch][color] = False
                time.sleep(t2)
                send_msg(msg)
            msg.servos[branch] = settings.SERVO_HELD
            send_msg(msg)
            time.sleep(t2)
        send_msg(msg)
        time.sleep(stime)
        for branch in range(8):
            for color in range (3):
                msg.lights[branch][color] = True
                time.sleep(t2)
                send_msg(msg)
            msg.servos[branch] = SERVO_RELEASED
            send_msg(msg)
            time.sleep(t2)
        send_msg(msg)
        time.sleep(stime)
    else:
        for color in range (3):
            for branch in range(8):
                msg.lights[branch][color] = True
                time.sleep(t2)
                send_msg(msg)
            send_msg(msg)
            time.sleep(stime)
            for branch in range(8):
                msg.lights[branch][color] = False
                time.sleep(t2)
                send_msg(msg)
            send_msg(msg)
            time.sleep(stime)
        for branch in range(8):
            msg.servos[branch] = settings.SERVO_HELD
            time.sleep(t2)
            send_msg(msg)
        send_msg(msg)
        time.sleep(stime)
        for branch in range(8):
            msg.servos[branch] = settings.SERVO_RELEASED
            time.sleep(t2)
            send_msg(msg)
        send_msg(msg)
        time.sleep(stime)

