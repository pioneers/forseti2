#!/usr/bin/env python2.7
"""
This node simulates a robot sending field commands.
the test sequentially tries 1 key on all dispensers every second.
"""
import sys
import lcm
import time
import forseti2 as fs2
import settings

print 'starting piemos_dispenser_cmd_test'

lc = lcm.LCM(settings.LCM_URI)

msg = fs2.piemos_field_cmd()
msg.key = 195
msg.dispenser_id = 1
msg.team = fs2.dispenser_cmd.TEAM_GOLD

msg.header = fs2.header()
msg.header.seq = 0
msg.header.time = time.time()

def printall(*arg):
    for a in arg:
        sys.stdout.write(str(a) + '\t')
    sys.stdout.write('\n')

def send_msg(m):
    m.header.seq+=1
    m.header.time = time.time()
    printall('fs2.piemos_field_cmd',
        m.key, 
        m.dispenser_id,
        m.team,
        m.header.seq,
        m.header.time)
    lc.publish("piemos0/field_cmd", m.encode())

sleep_time = 1


while True:
    msg.key+=1
    for team in (fs2.dispenser_cmd.TEAM_GOLD, fs2.dispenser_cmd.TEAM_BLUE):
        for i in range(4):
            msg.team = team
            msg.dispenser_id = i
            send_msg(msg)
    time.sleep(sleep_time)


