#!/usr/bin/env python2.7

import lcm
import time
import forseti2

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

msg = forseti2.health()
msg.header = forseti2.header()
msg.header.seq = 0
msg.header.time = time.time()
msg.uptime = 0

start = time.time()
while True:
    msg.uptime = time.time() - start
    msg.header.seq+=1
    msg.header.time = time.time()
    lc.publish("sprocket/health", msg.encode())
    print('forseti2.health: uptime='
        + str(msg.uptime)
        + ', header.seq='
        + str(msg.header.seq)
        + ', header.time='
        + str(msg.header.time))
    time.sleep(.1)