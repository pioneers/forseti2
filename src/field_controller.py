#!/usr/bin/env python2.7
"""
The field controller:
* Listens to field commands from PiEMOS
* Listens to field commands from the match management and reset
* Keeps track of the state of field elements
* Sends commands to actuate field elements
* Keeps track of RFID cards on the field, and their associations
"""
import lcm
import forseti2 as fs2
import threading
import time
import sys
import settings
import util
import re
import json

ALLIANCE_BLUE = 0
ALLIANCE_GOLD = 1

CODE_LEFT = 3
CODE_RIGHT = 4
CODE_FALSE = 5

class FieldController:
    def __init__(self, in_lcm):
        self.lcm = in_lcm
        self.seq = util.LCMSequence(self.lcm, fs2.forest_cmd, "/forest/cmd")
        self.seq.debug = False
        self.bad_rfid_seq = util.LCMSequence(self.lcm, fs2.piemos_bad_rfid, "piemos/bad_rfid")
        # This also initializes variables
        self.reset_field()

    def reset_field(self):
        # dispenser_released[alliance][dispenser id]
        self.dispenser_released = {
            ALLIANCE_BLUE: [False for _ in range(4)],
            ALLIANCE_GOLD: [False for _ in range(4)],
            }

        # lights[alliance][dispenser id][RED/ORANGE/GREEN]
        self.lights = {
            ALLIANCE_BLUE: [[False, False, False] for _ in range(4)],
            ALLIANCE_GOLD: [[False, False, False] for _ in range(4)],
            }

        self.release_codes = {}

        self.send_forest_cmd()

    def release_teleop_dispensers(self):
        """Release dispensers, as needed, at start of tele-op"""
        self.dispenser_released[0][settings.DISPENSER_TELEOP_0] = True
        self.dispenser_released[0][settings.DISPENSER_TELEOP_1] = True
        self.dispenser_released[1][settings.DISPENSER_TELEOP_0] = True
        self.dispenser_released[1][settings.DISPENSER_TELEOP_1] = True

    def send_forest_cmd(self):
        lights = [None for _ in range(8)]
        servos = [None for _ in range(8)]
        for team, offset in ((ALLIANCE_BLUE, 0), (ALLIANCE_GOLD, 4)):
            for i in range(4):
                lights[offset + i] = self.lights[team][i]
                servos[offset + i] = settings.SERVO_RELEASED if self.dispenser_released[team][i] else settings.SERVO_HELD
        self.seq.publish(lights=lights, servos=servos)

    def set_flash(self, alliance, team, code_type, is_start):
        # TODO(nikita): this just turns on the light, instead of flashing it
        if code_type == CODE_FALSE:
            print "INFO: attempting to flash dispenser lights associated with a false release code"
        elif code_type == CODE_LEFT:
            self.lights[alliance][settings.DISPENSER_LEFT][fs2.forest_cmd.BRANCH_ORANGE] = is_start
        elif code_type == CODE_RIGHT:
            self.lights[alliance][settings.DISPENSER_RIGHT][fs2.forest_cmd.BRANCH_ORANGE] = is_start
        else:
            assert(False) # code type not valid

    def release_dispenser(self, alliance, team, code_type):
        if code_type == CODE_FALSE:
            self.disable_robot(team)
        elif code_type == CODE_LEFT:
            if not self.dispenser_released[alliance][settings.DISPENSER_LEFT]:
                self.lights[alliance][settings.DISPENSER_LEFT][fs2.forest_cmd.BRANCH_GREEN] = True
                self.dispenser_released[alliance][settings.DISPENSER_LEFT] = True
        elif code_type == CODE_RIGHT:
            if not self.dispenser_released[alliance][settings.DISPENSER_RIGHT]:
                self.lights[alliance][settings.DISPENSER_RIGHT][fs2.forest_cmd.BRANCH_GREEN] = True
                self.dispenser_released[alliance][settings.DISPENSER_RIGHT] = True
        else:
            assert(False) # Code type not valid

    def disable_robot(self, team):
        """Disable a robot after it sends a false release code"""
        # TODO(nikita): some kind of debouncing if these are sent too frequently
        print "station {} sent false release code".format(team)
        self.bad_rfid_seq.publish(station=team)

    def handle_field_cmd(self, channel, data):
        msg = fs2.piemos_field_cmd.decode(data)
        team = int(re.match("piemos(\d)/field_cmd", channel).group(1))
        print "received fs2.piemos_field_cmd from PiEMOS", team
        util.print_lcm_msg(msg, "  ")

        if msg.rfid_uid not in self.release_codes:
            # TODO(nikita): logging and anti-cheating
            print "WARNING: received RFID code that is not on the field"
            self.send_forest_cmd()
            return

        expected_alliance, code_type = self.release_codes[msg.rfid_uid]

        if (team in [0, 1] and expected_alliance != ALLIANCE_BLUE) or (
            team in [2, 3] and expected_alliance != ALLIANCE_GOLD):
            # TODO(nikita): logging and anti-cheating
            print "WARNING: received RFID code to actuate dispenser for opposing alliance"
            self.send_forest_cmd()
            return

        if msg.isFlash:
            self.set_flash(expected_alliance, team, code_type, msg.isStart)
        else:
            self.release_dispenser(expected_alliance, team, code_type)

        self.send_forest_cmd()

    def handle_control(self, channel, data):
        # TODO(nikita): is there a way to do this that doesn't depend on strings?
        msg = fs2.ControlData.decode(data)
        if msg.Stage == "Teleop":
            # This should dispense at the start of teleop
            # (but not when the game is paused between autonomous and teleop)
            self.release_teleop_dispensers()
        elif msg.Stage == "End":
            # This call is not enough to make sure the field is reset at the
            # *start* of each match
            # However, the field will likely remain in the "End" stage for a
            # while before scores are tabulated and submitted. This allows field
            # reset to happen simultaneously.
            self.reset_field()

        self.send_forest_cmd()

    def handle_match_init(self, channel, data):
        # Make sure the field is fully reset at the start of the match
        self.reset_field()

        # Load RFID tag data for the match
        msg = fs2.Match.decode(data)
        with open(msg.gold_items_loc) as f:
            gold_items = json.load(f)
        with open(msg.blue_items_loc) as f:
            blue_items = json.load(f)

        for tag in gold_items:
            self.release_codes[int(tag["uid"], 16)] = (ALLIANCE_GOLD, tag["objectType"])
        for tag in blue_items:
            self.release_codes[int(tag["uid"], 16)] = (ALLIANCE_BLUE, tag["objectType"])

        self.send_forest_cmd()


if __name__=='__main__':
    try:
        lc = lcm.LCM(settings.LCM_URI)
        st = FieldController(lc)
        lc.subscribe("piemos0/field_cmd", st.handle_field_cmd)
        lc.subscribe("piemos1/field_cmd", st.handle_field_cmd)
        lc.subscribe("piemos2/field_cmd", st.handle_field_cmd)
        lc.subscribe("piemos3/field_cmd", st.handle_field_cmd)
        lc.subscribe("piemos/Control", st.handle_control)
        lc.subscribe("Match/Init", st.handle_match_init)

        while(True):
            lc.handle()
    except KeyboardInterrupt:
        raise
