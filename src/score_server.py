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
            team0_penalty = 0,
            team1_penalty = 0,
            team2_penalty = 0,
            team3_penalty = 0,
            bonus_possession = forseti2.score_delta.NEUTRAL,
            bonus_points = settings.BONUS_INITIAL
            )

    def handle(self):
        self.lc.handle()

    def delta_handler(self, channel, data):
        msg = forseti2.score_delta.decode(data)

        for k in ["blue_points",
                  "gold_points",
                  "team0_penalty",
                  "team1_penalty",
                  "team2_penalty",
                  "team3_penalty",
                  "bonus_points"]:
            self.state[k] += msg.__getattribute__(k)

        if msg.bonus_possession != forseti2.score_delta.UNCHANGED:
            self.state["bonus_possession"] = msg.bonus_possession

        self.print_score()

    def print_score(self):
        blue_bonus = self.state["bonus_possession"] == forseti2.score_delta.BLUE
        gold_bonus = self.state["bonus_possession"] == forseti2.score_delta.GOLD

        print "BLUE: {} = {}{} - {} | -{}{} + {} = {} : GOLD".format(
            self.state["blue_points"] - self.state["team0_penalty"] - self.state["team1_penalty"] + (self.state["bonus_points"] if blue_bonus else 0),
            self.state["blue_points"],
            " + {}".format(self.state["bonus_points"]) if blue_bonus else "",
            self.state["team0_penalty"] + self.state["team1_penalty"],
            self.state["team2_penalty"] + self.state["team3_penalty"],
            " + {}".format(self.state["bonus_points"]) if gold_bonus else "",
            self.state["gold_points"],
            self.state["gold_points"] - self.state["team2_penalty"] - self.state["team3_penalty"] + (self.state["bonus_points"] if gold_bonus else 0))


server = ScoreServer()

while True:
    server.handle()
