#!/usr/bin/env python2.7
import lcm
import forseti2 as fs2
import threading
import time
import sys

def printall(*arg):
    for a in arg:
        sys.stdout.write(str(a) + '\t')
    sys.stdout.write('\n')

class FieldController:

    def __init__(self, lcm):
        self.lcm = lcm
        self.msg = fs2.dispenser_cmd()
        self.msg.header = fs2.header()
        self.msg.header.seq = 0
        self.msg.header.time = time.time()
        self.msg.team = 0
        for i in range(4):
            self.msg.state[i] = fs2.dispenser_cmd.STATE_HELD

        # States[team][dispenser id]
        self.states = {
            fs2.dispenser_cmd.TEAM_BLUE:[0,0,0,0],
            fs2.dispenser_cmd.TEAM_GOLD:[0,0,0,0]}
        for team in (fs2.dispenser_cmd.TEAM_BLUE, fs2.dispenser_cmd.TEAM_GOLD):
            for i in range(4):
                self.states[team][i] = fs2.dispenser_cmd.STATE_HELD
        printall(self.states)

        # keys to open each dispenser. 
        self.keys = {
            fs2.dispenser_cmd.TEAM_BLUE:[200, 201, 202, 203],
            fs2.dispenser_cmd.TEAM_GOLD:[210, 211, 212, 213]}

    def _send_field_cmd(self):
        for team in (fs2.dispenser_cmd.TEAM_BLUE, fs2.dispenser_cmd.TEAM_GOLD):
            self.msg.header.seq+=1
            self.msg.header.time=time.time()
            self.msg.team = team
            self.msg.state = self.states[team]
            self.lcm.publish('sprocket/field', self.msg.encode())

    def handle_field_cmd(self, channel, data):
        m = fs2.piemos_field_cmd.decode(data)
        printall('received fs2.piemos_field_cmd',
            m.key, 
            m.dispenser_id,
            m.team,
            m.header.seq,
            m.header.time)
        if m.key == self.keys[m.team][m.dispenser_id]:
            self.states[m.team][m.dispenser_id]=fs2.dispenser_cmd.STATE_RELEASED
        self._send_field_cmd()

if __name__=='__main__':
    try:
        lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
        st = FieldController(lc)
        lc.subscribe("piemos0/field_cmd", st.handle_field_cmd)
        lc.subscribe("piemos1/field_cmd", st.handle_field_cmd)
        lc.subscribe("piemos2/field_cmd", st.handle_field_cmd)
        lc.subscribe("piemos3/field_cmd", st.handle_field_cmd)        

        while(True):
            lc.handle()
    except KeyboardInterrupt:
        raise
