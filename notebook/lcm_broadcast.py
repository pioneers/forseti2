# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import lcm

# <codecell>

import forseti2

# <codecell>

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

# <codecell>

msg = forseti2.health()

# <codecell>

msg.uptime = 0

# <codecell>

msg.uptime+=1
lc.publish("sprocket/health", msg.encode())

# <codecell>


