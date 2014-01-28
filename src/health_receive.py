#!/usr/bin/env python2.7

import lcm
import time
import forseti2

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

def health_handler(channel, data):
    msg = forseti2.health.decode(data)
    print('forseti2.health:'
        + 'channel='
        + str(channel)
        + ', uptime='
        + str(msg.uptime)
        + ', header.seq='
        + str(msg.header.seq)
        + ', header.time='
        + str(msg.header.time))
sub = lc.subscribe("sprocket/health", health_handler)
while True:
    lc.handle()
