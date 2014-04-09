#!/usr/bin/env python2.7
"""
This node tests dispenser by testing all dispensers. 
"""


BLINK_ALL = False
BLINK_EACH = True

import lcm
import time
import forseti2 as fs2
import settings

lc = lcm.LCM(settings.LCM_URI)

msg = fs2.dispenser_cmd()

msg.header = fs2.header()
msg.header.seq = 0
msg.header.time = time.time()
msg.team = fs2.dispenser_cmd.TEAM_GOLD
for i in range(4):
    msg.state[i] = fs2.dispenser_cmd.STATE_HELD

def send_msg(m):
    m.header.seq+=1
    m.header.time = time.time()
    print('fs2.health: state='
        + str(m.state)
        + ', team='
        + str(m.team)
        + ', header.seq='
        + str(m.header.seq)
        + ', header.time='
        + str(m.header.time))
    lc.publish("sprocket/field", m.encode())

sleep_time = 1


while True:
    if BLINK_ALL:
        for team in (fs2.dispenser_cmd.TEAM_GOLD, fs2.dispenser_cmd.TEAM_BLUE):
            msg.team = team
            for i in range(4):
                msg.state[i] = fs2.dispenser_cmd.STATE_RELEASED
            send_msg(msg)
        time.sleep(sleep_time)
        for team in (fs2.dispenser_cmd.TEAM_GOLD, fs2.dispenser_cmd.TEAM_BLUE):
            msg.team = team
            for i in range(4):
                msg.state[i] = fs2.dispenser_cmd.STATE_HELD
            send_msg(msg)
        time.sleep(sleep_time)

    if BLINK_EACH:
        for team in (fs2.dispenser_cmd.TEAM_GOLD, fs2.dispenser_cmd.TEAM_BLUE):
            for i in range(4):
                msg.team = team
                msg.state[i] = fs2.dispenser_cmd.STATE_RELEASED
                send_msg(msg)
                time.sleep(sleep_time)

                msg.state[i] = fs2.dispenser_cmd.STATE_HELD
                send_msg(msg)
                time.sleep(sleep_time)

