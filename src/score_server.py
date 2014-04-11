#!/usr/bin/env python2.7
"""
Score server
"""

import lcm
import time
import forseti2
import settings

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
#sub = lc.subscribe("sprocket/health", health_handler)


class ScoreServer:
    def __init__(self):
        self.lc = lcm.LCM(settings.LCM_URI)
        self.sub = self.lc.subscribe("score/delta", self.delta_handler)

        self.reset_scores()

    def reset_scores(self):
        self.state = dict(
            blue_points = 0,
            gold_points = 0,
            blue_permanent_points = 0,
            gold_permanent_points = 0,
            blue_penalty = 0,
            gold_penalty = 0,
            bonus_possession = forseti2.score_delta.NEUTRAL,
            bonus_points = settings.BONUS_INITIAL
            )

    def handle(self):
        self.lc.handle()

    def delta_handler(self, channel, data):
        msg = forseti2.score_delta.decode(data)

        if msg.action_reset:
            self.reset_scores()

        for k in ["blue_points",
                  "gold_points",
                  "blue_permanent_points",
                  "gold_permanent_points",
                  "blue_penalty",
                  "gold_penalty",
                  ]:
            self.state[k] += msg.__getattribute__(k)


        self.state["blue_permanent_points"] = min(self.state["blue_permanent_points"],
                                                  settings.PERMANENT_GOAL_MAXIMUM)
        self.state["gold_permanent_points"] = min(self.state["gold_permanent_points"],
                                                  settings.PERMANENT_GOAL_MAXIMUM)
        # Logic to handle bonus ball posession changes
        # If bonus points are included as part of a bonus possession change delta,
        # do not count those points if the delta turns out to be invalid
        count_bonus_points = False
        if msg.bonus_possession == forseti2.score_delta.UNCHANGED:
            count_bonus_points = True
        elif msg.bonus_possession == forseti2.score_delta.NEUTRAL:
            self.state["bonus_possession"] = msg.bonus_possession
            count_bonus_points = True
        elif msg.bonus_possession == forseti2.score_delta.TOGGLE:
            if self.state["bonus_possession"] == forseti2.score_delta.NEUTRAL:
                print "WARNING: ignoring attempt to toggle bonus ball that is not in possession of any team"
            elif self.state["bonus_possession"] == forseti2.score_delta.BLUE:
                self.state["bonus_possession"] = forseti2.score_delta.GOLD
                count_bonus_points = True
            elif self.state["bonus_possession"] == forseti2.score_delta.GOLD:
                self.state["bonus_possession"] = forseti2.score_delta.BLUE
                count_bonus_points = True
        elif msg.bonus_possession == self.state["bonus_possession"]:
            print "WARNING: ignoring attempt to reassign bonus ball to the team already in possession"
        else:
            self.state["bonus_possession"] = msg.bonus_possession
            count_bonus_points = True

        if count_bonus_points:
            self.state["bonus_points"] += msg.bonus_points

        self.print_score()

    def print_score(self):
        # Team that does *not* have possession gets points
        blue_bonus = self.state["bonus_possession"] == forseti2.score_delta.GOLD
        gold_bonus = self.state["bonus_possession"] == forseti2.score_delta.BLUE

        print "BLUE: {} = {} + {}{} - {} | -{}{} + {} + {} = {} : GOLD".format(
            self.state["blue_points"] + self.state["blue_permanent_points"] - self.state["blue_penalty"] + (self.state["bonus_points"] if blue_bonus else 0),
            self.state["blue_points"],
            self.state["blue_permanent_points"],
            " + {}".format(self.state["bonus_points"]) if blue_bonus else "",
            self.state["blue_penalty"],
            self.state["gold_penalty"],
            " + {}".format(self.state["bonus_points"]) if gold_bonus else "",
            self.state["gold_permanent_points"],
            self.state["gold_points"],
            self.state["gold_points"] + self.state["gold_permanent_points"] - self.state["gold_penalty"] + (self.state["bonus_points"] if gold_bonus else 0))


server = ScoreServer()

while True:
    server.handle()
