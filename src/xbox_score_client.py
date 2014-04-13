"""
xbox_score_client.py

Reads joystick data from the xbox controller and converts it into score packets

@author: Allen Li
"""

import lcm
import argparse
import forseti2 as fs2
import settings
import util

SLEEP_TIME = 0.1
# packet format
PF = fs2.xbox_joystick_state

#Button configurations
BUTTON_GAME_PIECE_ENTER = [PF.A]
BUTTON_PERMANENT_GOAL_SCORE = [PF.B]
BUTTON_DISPENSER_BALLS_ENTER_FIELD = [PF.X]

BUTTON_BONUS_SET_BLUE = [PF.LB]
BUTTON_BONUS_SET_GOLD = [PF.RB]
AXIS_BONUS_SET_BLUE = [] # TODO
AXIS_BONUS_SET_GOLD = [] # TODO
BUTTON_BONUS_TOGGLE = [PF.A]

def describe_button(b):
    mapping = {
        PF.A : "A",
        PF.B : "B",
        PF.X : "X",
        PF.Y : "Y",
        PF.LB : "Left Button",
        PF.RB : "Right Button",
        PF.BACK : "Back",
        PF.START : "Start",
        PF.GUIDE : "Guide",
        PF.LSTICK : "Left stick press",
        PF.RSTICK : "Right stick press",
    }
    try:
        return ", ".join(describe_button(bb) for bb in b)
    except TypeError:
        if b in mapping:
            return mapping[b]
        else:
            return "Unknown"

class ScoreClient(object):

    def __init__(self, joystick_channel='default'):
        self.lc = lcm.LCM(settings.LCM_URI)
        self.subscription = self.lc.subscribe("xbox/state/{}/0".format(joystick_channel),
                                              self.handle_xbox)
        self.seq = util.LCMSequence(self.lc, fs2.score_delta, "score/delta")
        self.buttons = [0 for _ in xrange(11)]

    def update(self, i, b):
        print "RUNNING BASE ScoreClient"

    def process_message(self, msg):
        for i, b in enumerate(msg.buttons):
            if self.buttons[i] != b:
                self.buttons[i] = b
                self.update(i, b)

    def handle_xbox(self, channel, data):
        self.process_message(PF.decode(data))

    def handle(self):
        self.lc.handle()

    def update_alliance(self, alliance, i, b):
        if b != 1:
            # respond only on the down press
            return

        assert(alliance in [fs2.score_delta.BLUE, fs2.score_delta.GOLD])
        if alliance == fs2.score_delta.BLUE:
            if i in BUTTON_GAME_PIECE_ENTER:
                self.seq.publish(gold_normal_points=settings.GAME_PIECE_VALUE)
            elif i in BUTTON_PERMANENT_GOAL_SCORE:
                self.seq.publish(blue_permanent_points=settings.PERMANENT_GOAL_VALUE)
            elif i in BUTTON_DISPENSER_BALLS_ENTER_FIELD:
                self.seq.publish(gold_normal_points=settings.BALL_VALUE_PER_DISPENSER)
        else:
            if i in BUTTON_GAME_PIECE_ENTER:
                self.seq.publish(blue_normal_points=settings.GAME_PIECE_VALUE)
            elif i in BUTTON_PERMANENT_GOAL_SCORE:
                self.seq.publish(gold_permanent_points=settings.PERMANENT_GOAL_VALUE)
            elif i in BUTTON_DISPENSER_BALLS_ENTER_FIELD:
                self.seq.publish(blue_normal_points=settings.BALL_VALUE_PER_DISPENSER)

    def update_bonus(self, i, b):
        if b != 1:
            # respond only on the down press
            return

        if i in BUTTON_BONUS_SET_BLUE:
            self.seq.publish(bonus_possession=fs2.score_delta.BLUE)
        elif i in BUTTON_BONUS_SET_GOLD:
            self.seq.publish(bonus_possession=fs2.score_delta.GOLD)
        elif i in BUTTON_BONUS_TOGGLE:
            self.seq.publish(bonus_possession=fs2.score_delta.TOGGLE,
                             bonus_points=settings.BONUS_INCREMENT)


    def print_mapping_alliance(self, alliance):
        assert(alliance in [fs2.score_delta.BLUE, fs2.score_delta.GOLD])
        color = "Blue" if alliance == fs2.score_delta.BLUE else "Gold"

        print "Button mapping"
        print "--------------"
        print "    Game piece enters {} side of the field: {}".format(
            color,
            "".join(describe_button(BUTTON_GAME_PIECE_ENTER)))
        print "    {} alliance scores permanent goal: {}".format(
            color,
            "".join(describe_button(BUTTON_PERMANENT_GOAL_SCORE)))
        print "    Dispenser fully releases on {} side of the field: {}".format(
            color,
            "".join(describe_button(BUTTON_DISPENSER_BALLS_ENTER_FIELD)))

    def print_mapping_bonus(self):
        print "Button mapping"
        print "--------------"
        print "    Bonus ball initially enters the Blue side of the field:", describe_button(BUTTON_BONUS_SET_BLUE)
        print "    Bonus ball initially enters the Gold side of the field:", describe_button(BUTTON_BONUS_SET_GOLD)
        print "    Toggle bonus ball side, increment score:", describe_button(BUTTON_BONUS_TOGGLE)


class BlueScoreClient(ScoreClient):
    def update(self, i, b):
        self.update_alliance(fs2.score_delta.BLUE, i, b)

    def print_mapping(self):
        self.print_mapping_alliance(fs2.score_delta.BLUE)

class GoldScoreClient(ScoreClient):
    def update(self, i, b):
        self.update_alliance(fs2.score_delta.GOLD, i, b)

    def print_mapping(self):
        self.print_mapping_alliance(fs2.score_delta.GOLD)

class BonusScoreClient(ScoreClient):
    def update(self, i, b):
        self.update_bonus(i, b)

    def print_mapping(self):
        self.print_mapping_bonus()

class DebugScoreClient(ScoreClient):
    """
    Score client for debugging purposes.

    Penalties and resets would normally be done using the judge interface, but
    this provides an alternative for debugging purposes
    """

    button_actions = {
        PF.X : ("increment blue points", dict(blue_normal_points=settings.GAME_PIECE_VALUE)),
        PF.Y : ("increment gold points", dict(gold_normal_points=settings.GAME_PIECE_VALUE)),
        PF.A : ("increment blue permanent points", dict(blue_permanent_points=settings.PERMANENT_GOAL_VALUE)),
        PF.B : ("increment gold permanent points", dict(gold_permanent_points=settings.PERMANENT_GOAL_VALUE)),
        PF.BACK : ("blue bonus ball", dict(bonus_possession=fs2.score_delta.BLUE)),
        PF.START : ("gold bonus ball", dict(bonus_possession=fs2.score_delta.GOLD)),
        PF.GUIDE : ("change bonus ball posession, increment score", dict(
            bonus_possession=fs2.score_delta.TOGGLE,
            bonus_points=settings.BONUS_INCREMENT)),
        PF.LB : ("blue penalty", dict(blue_penalty=settings.PENALTY_REGULAR)),
        PF.RB : ("gold penalty", dict(gold_penalty=settings.PENALTY_REGULAR)),
        PF.RSTICK : ("RESET", dict(action_reset=True)),
    }

    def update(self, i, b):
        if b != 1:
            # respond only on the down press
            return

        if i in self.button_actions:
            self.seq.publish(**self.button_actions[i][1])

    def print_mapping(self):
        print "Button mapping"
        print "--------------"

        for k, v in self.button_actions.items():
            print "{:>20}: {}".format(describe_button(k), v[0])

def main():
    parser = argparse.ArgumentParser(description="Receives joystick values and outputs score changes")
    parser.add_argument('--type', required=True, type=str, choices=['blue', 'gold', 'bonus', 'debug'], action='store')
    parser.add_argument('--joystick', default=0, help="Joystick channel name")
    args = parser.parse_args()
    if args.type == 'blue':
        sclient = BlueScoreClient(joystick_channel=args.joystick)
    elif args.type == 'gold':
        sclient = GoldScoreClient(joystick_channel=args.joystick)
    elif args.type == 'bonus':
        sclient = BonusScoreClient(joystick_channel=args.joystick)
    elif args.type == 'debug':
        sclient = DebugScoreClient(joystick_channel=args.joystick)


    print "Initialized ScoreClient..."
    sclient.print_mapping()
    try:
        while True:
            sclient.handle()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
