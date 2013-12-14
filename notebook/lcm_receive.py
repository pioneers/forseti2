# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import lcm
import forseti2

# <codecell>

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

# <codecell>

def health_handler(channel, data):
    msg = forseti2.health.decode(data)
    print("Received message on channel \"%s\"" % channel)
    print("   uptime   = %s" % str(msg.uptime))

# <codecell>

sub = lc.subscribe("sprocket/health", health_handler)

# <codecell>

try:
    while True:
        lc.handle()
except KeyboardInterrupt:
    pass

# <codecell>


