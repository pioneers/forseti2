#!/usr/bin/env python2.7

import lcm
import time
import forseti2
import settings

lc = lcm.LCM(settings.LCM_URI)

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
