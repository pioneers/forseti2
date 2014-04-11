"""
score_server.py

@author: Allen Li
"""

import lcm
import time
import sys
import forseti2 as fs2
import settings

SLEEP_TIME = 0.1
# packet format
PF = fs2.xbox_joystick_state

class ScoreServer(object):

    def __init__(self, num_teams = 2, update_fn = None):
        if update_fn:
            self.update = update_fn
        self.scores = [0 for _ in xrange(num_teams)]
        self.buttons = [0 for _ in xrange(11)]

    def num_teams():
        return len(self.scores)

    def increment_score(self, team, quantity):
        self.scores[team] += quantity
        print "new scores = " + str(self.scores)

    def reset_scores(self):
        self.scores = [0 for _ in xrange(len(self.scores))]
        print "new scores = " + str(self.scores)

    def update(self, i, b):
        if b == 1: # respond only to pressing down
            if i == PF.A or i == PF.START or i == PF.RB:
                self.increment_score(0, 1)
            if i == PF.B or i == PF.BACK or i == PF.LB:
                self.increment_score(0, -1)
            if i == PF.X or i == PF.RSTICK:
                self.increment_score(1, 1)
            if i == PF.Y or i == PF.LSTICK:
                self.increment_score(1, -1)
            if i == PF.GUIDE:
                self.reset_scores()


    def process_message(self, msg):
        for i, b in enumerate(msg.buttons):
            if self.buttons[i] != b:
                self.buttons[i] = b
                self.update(i, b)

def handle_xbox(channel, data):
    sserver.process_message(PF.decode(data))

def main():
    global lc
    global sserver 
    sserver = ScoreServer()
    lc = lcm.LCM(settings.LCM_URI)
    subscription = lc.subscribe("xbox/state/default/0", handle_xbox)
    print "Initialized ScoreServer..."
    try:
        while True:
            lc.handle()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
