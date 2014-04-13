#!/usr/bin/env python2.7
"""
Score server
"""

import lcm
import time
import forseti2
import settings
import util

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
        self.time_sub = self.lc.subscribe("Timer/Time", self.time_handler)
        self.seq = util.LCMSequence(self.lc, forseti2.score_state, "score/state")
        self.seq.debug = False

        self.current_time = 0
        self.bonus_penalty_time = 0 # Time when bonus penalty will be assessed

        self.reset_scores()

    def reset_scores(self):
        self.state = dict(
            blue_normal_points = settings.INITIAL_ALLIANCE_SCORE,
            gold_normal_points = settings.INITIAL_ALLIANCE_SCORE,
            blue_autonomous_points = 0,
            gold_autonomous_points = 0,
            blue_permanent_points = 0,
            gold_permanent_points = 0,
            blue_penalty = 0,
            gold_penalty = 0,
            bonus_possession = forseti2.score_delta.NEUTRAL,
            bonus_points = settings.BONUS_INITIAL
            )

    def handle(self):
        self.lc.handle()

    def time_handler(self, channel, data):
        msg = forseti2.Time.decode(data)
        self.current_time = msg.game_time_so_far

        if self.current_time >= self.bonus_penalty_time:
            if self.state["bonus_possession"] == forseti2.score_delta.BLUE:
                self.state["blue_penalty"] += settings.PENALTY_BONUS_TIMER
                print "Blue alliance penalized for over-possession of the bonus ball"
            elif self.state["bonus_possession"] == forseti2.score_delta.GOLD:
                self.state["gold_penalty"] += settings.PENALTY_BONUS_TIMER
                print "Gold alliance penalized for over-possession of the bonus ball"
            else:
                return

            self.bonus_penalty_time = self.current_time + settings.BONUS_TIMER_SECONDS

            self.print_score()
            self.seq.publish(**self.tabulate_state())


    def delta_handler(self, channel, data):
        msg = forseti2.score_delta.decode(data)

        if msg.action_reset:
            self.reset_scores()

        for k in ["blue_normal_points",
                  "gold_normal_points",
                  "blue_autonomous_points",
                  "gold_autonomous_points",
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
        reset_bonus_timer = False
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
                reset_bonus_timer = True
            elif self.state["bonus_possession"] == forseti2.score_delta.GOLD:
                self.state["bonus_possession"] = forseti2.score_delta.BLUE
                count_bonus_points = True
                reset_bonus_timer = True
        elif msg.bonus_possession == self.state["bonus_possession"]:
            print "WARNING: ignoring attempt to reassign bonus ball to the team already in possession"
        else:
            self.state["bonus_possession"] = msg.bonus_possession
            count_bonus_points = True
            reset_bonus_timer = True

        if count_bonus_points:
            self.state["bonus_points"] += msg.bonus_points

        if reset_bonus_timer:
            self.bonus_penalty_time = self.current_time + settings.BONUS_TIMER_SECONDS

        self.print_score()
        self.seq.publish(**self.tabulate_state())

    def tabulate_state(self):
        state = self.state.copy()

        # Team that does *not* have possession gets points
        blue_bonus = 0
        gold_bonus = 0
        if state["bonus_possession"] == forseti2.score_delta.GOLD:
            blue_bonus = state["bonus_points"]
        elif state["bonus_possession"] == forseti2.score_delta.BLUE:
            gold_bonus = state["bonus_points"]

        state["blue_total"] = state["blue_normal_points"] + state["blue_autonomous_points"] + state["blue_permanent_points"] - state["blue_penalty"] + blue_bonus
        state["gold_total"] = state["gold_normal_points"] + state["gold_autonomous_points"]+ state["gold_permanent_points"] - state["gold_penalty"] + gold_bonus

        if state["bonus_possession"] == forseti2.score_delta.NEUTRAL:
            state["bonus_time_remaining"] = settings.BONUS_TIMER_SECONDS
        else:
            state["bonus_time_remaining"] = int(self.bonus_penalty_time - time.time())

        return state

    def print_score(self):
        state =  self.tabulate_state()

        blue_bonus = 0
        gold_bonus = 0
        if state["bonus_possession"] == forseti2.score_delta.GOLD:
            blue_bonus = state["bonus_points"]
        elif state["bonus_possession"] == forseti2.score_delta.BLUE:
            gold_bonus = state["bonus_points"]

        print "BLUE: {} = {} + {} + {}{} - {} | -{}{} + {} + {} + {} = {} : GOLD".format(
            state["blue_total"],
            state["blue_normal_points"],
            state["blue_autonomous_points"],
            state["blue_permanent_points"],
            " + {}".format(state["bonus_points"]) if blue_bonus else "",
            state["blue_penalty"],
            state["gold_penalty"],
            " + {}".format(state["bonus_points"]) if gold_bonus else "",
            state["gold_permanent_points"],
            state["gold_autonomous_points"],
            state["gold_normal_points"],
            state["gold_total"]
            )

server = ScoreServer()

while True:
    server.handle()
