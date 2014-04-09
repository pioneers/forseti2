
#!/usr/bin/env python2.7
"""
This node tests piemos by scrubbing through all option.
"""

import lcm
import time
import forseti2 as fs2
import settings

lc = lcm.LCM(settings.LCM_URI)

msg	= fs2.piemos_cmd()

msg.header = fs2.header()
msg.header.seq = 0
msg.header.time = time.time()

msg.auton = True
msg.enabled = True

def send_msg(m):
    m.header.seq+=1
    m.header.time = time.time()
    print('fs2.health: enabled='
        + str(m.enabled)
        + ', auton='
        + str(m.auton)
        + ', header.seq='
        + str(m.header.seq)
        + ', header.time='
        + str(m.header.time))
    lc.publish("piemos0/cmd", m.encode())

sleep_time = 1


while True:
	for enabled in (True, False):
		for auton in (True, False):
			msg.enabled = enabled
			msg.auton = auton
			send_msg(msg)
			time.sleep(1)
