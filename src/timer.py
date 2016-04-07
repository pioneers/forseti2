#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
timer.py
Created on Wed Apr 24 12:00:00 2013

@author: kyle


"""
from __future__ import print_function

import forseti2
import json
import lcm
import threading
import time
import random
import os
import settings
import util
import LCMNode
from operator import add

Node = LCMNode.Node
LCMNode = LCMNode.LCMNode

class Timer(object):

    def __init__(self):
        self.segments = []
        self.segment_start_time = time.time()
        self.running = False

    def _this_segment_time(self):
        return time.time() - self.segment_start_time

    def time(self):
        if self.running:
            return sum(self.segments) + self._this_segment_time()
        else:
            return sum(self.segments)

    def start(self):
        if not self.running:
            self.running = True
            self.segment_start_time = time.time()
        return self

    def pause(self):
        if not self.running:
            return self
        self.running = False
        self.segments.append(self._this_segment_time())
        return self

    def add(self, additional_time):
        self.segments.append(additional_time)

    def subtract(self, less_time):
        self.segments.append(-less_time)

    def reset(self):
        self.__init__()
        return self

class Period(object):

    def __init__(self, name, length, autocontinue=False):
        self.name = name
        self.length = length
        self.autocontinue = autocontinue

class MatchTimer(LCMNode):

    def __init__(self, lc, robot_controller, live_score_server):
        self.match = None
        self.match_number = -1
        self.stage_ended = False
        self.lc = lc
        self.robot_controller = robot_controller
        self.live_score_server = live_score_server
        self.stages = [Period('Setup', 0),
            Period('Autonomous', settings.AUTONOMOUS_LENGTH_SECONDS, True), Period('Paused', 0),
            Period('Teleop', settings.TELEOP_LENGTH_SECONDS, True), Period('End', 0)]
        self.stage_index = 0
        self.match_timer = Timer()
        self.stage_timer = Timer()
        self.lc.subscribe('Timer/Control', self.handle_control)
        self.lc.subscribe('Match/Init', self.handle_init)
        self.start_thread()
        self.on_stage_change(None, self.stages[0])

    def reset(self, match_number):
        self.match_number = match_number
        self.stage_index = 0
        self.match_timer.reset()
        self.stage_timer.reset()
        self.robot_controller.reset()
        self.live_score_server.reset(match_number)
        self.on_stage_change(self.stages[self.stage_index], self.stages[0])
        self.stage_ended = True

    def current_stage(self):
        return self.stages[self.stage_index]

    def check_for_stage_change(self):
        if self.stage_timer.time() > self.current_stage().length:
            self.stage_timer.reset()
            self.stage_ended = True
            if self.current_stage().autocontinue:
                self.stage_index += 1
                self.on_stage_change(self.stages[self.stage_index - 1],
                    self.stages[self.stage_index])
                self.pause()
            else:
                self.pause()

    def on_stage_change(self, old_stage, new_stage):
        self.robot_controller.set_stage(new_stage.name)
        if new_stage.name in ['Setup', 'Paused', 'End']:
            self.pause()

    def start(self):
        self.match_timer.start()
        self.stage_timer.start()
        if self.stage_ended and self.stage_index + 1 < len(self.stages):
            self.stage_index += 1
            self.stage_ended = False
            self.on_stage_change(self.stages[self.stage_index - 1],
                self.stages[self.stage_index])

    def pause(self):
        self.stage_timer.pause()
        self.match_timer.pause()

    def reset_stage(self):
        #self.match_timer.stop()
        self.stage_timer.reset()

    def reset_match(self):
        self.stage_index = 0
        self.stage_timer.reset()
        self.match_timer.reset()

    def run(self):
        counter = 0
        while self.stage_index < len(self.stages):
            counter += 1
            time.sleep(0.3)
            self.check_for_stage_change()
            msg = forseti2.Time()
            msg.match_number = self.match_number
            msg.game_time_so_far = self.match_timer.time() * 1000
            msg.stage_time_so_far = self.stage_timer.time() * 1000
            msg.total_stage_time = self.current_stage().length * 1000
            msg.stage_name = self.current_stage().name
            self.robot_controller.set_stage(self.current_stage().name)
            self.lc.publish('Timer/Time', msg.encode())
            # hack to throttle event driven channels
            if counter == 9:
                counter = 0
                if self.match:
                    self.lc.publish('Timer/Match', self.match.encode())               
                self.robot_controller.publish()
                self.live_score_server.publish()

    def handle_control(self, channel, data):
        msg = forseti2.TimeControl.decode(data)
        print('Received command', msg.command_name)
        func = {
            'pause': self.pause,
            'start': self.start,
            'reset_match': self.reset_match,
            'reset_stage': self.reset_stage
        }[msg.command_name]
        func()

    def handle_init(self, channel, data):
        print("match init received")
        msg = forseti2.Match.decode(data)
        self.reset(msg.match_number)
        self.match = msg
        self.lc.publish('Timer/Match', self.match.encode())  


# handles business logic of robot state
# deals with emergency stop, manual override by field operators, and game state from timers
class Robot(object):

    def __init__(self):
        self.enabled = False
        self.running = False
        self.autonomous = True
        self.overridden = False
        self.estop = False

    def reset(self):
        self.__init__()

    def set_stage(self, stage_name):
        if not self.overridden:
            if stage_name == "Setup":
                self.running = False
                self.autonomous = True
                self.enabled = False
            elif stage_name == "Autonomous":
                self.running = True
                self.autonomous = True
                self.enabled = True
            elif stage_name == "Paused":
                self.running = True
                self.autonomous = True
                self.enabled = False
            elif stage_name == "Teleop":
                self.running = True
                self.autonomous = False
                self.enabled = True
            elif stage_name == "End":
                self.running = False
                self.autonomous = False
                self.enabled = False
            else:
                print("unrecognized stage: %s" % stage_name)

    # once estop is set, it cannot be unset until the robot is reset
    def emergency_stop(self, estop):
        if estop:
            self.estop = estop

    # for manual overriding of robot state (ignore timers)
    def override(self, override):
        self.overridden = override

    # manually set the state. only works if override is true
    def set_state(self, running, autonomous, enabled):
        if self.overridden:
            self.running = running
            self.autonomous = autonomous
            self.enabled = enabled

    @property
    def state(self):
        if self.estop:
            self.running = False
            self.enabled = False
        return (self.running, self.autonomous, self.enabled)

class RobotController(object):

    def __init__(self, lc, channels):
        self.lc = lc
        self.channels = channels
        self.robots = {channel: Robot() for channel in channels}
        self.lc.subscribe("Estop/Estop", self.handle_field_estop)
        for channel in channels:
            self.lc.subscribe("%s/Estop" % channel, self.handle_robot_estop)
            self.lc.subscribe("%s/Override" % channel, self.handle_override)
            self.lc.subscribe("%s/RobotState" % channel, self.handle_robot_state)
    
    def reset(self):
        for robot in self.robots.values():
            robot.reset()
        self.publish()

    # called when timer changes stage
    def set_stage(self, stage_name):
        for robot in self.robots.values():
            robot.set_stage(stage_name)
        self.publish()

    def handle_field_estop(self, channel, data):
        print("ESTOP RECEIVED")
        msg = forseti2.Estop.decode(data)
        for robot in self.robots.values():
            robot.emergency_stop(msg.estop)
        self.publish()

    # these apply to individual robots
    def handle_robot_estop(self, channel, data):
        msg = forseti2.Estop.decode(data)
        self.robots[channel.split('/')[0]].emergency_stop(msg.estop)
        self.publish()

    def handle_override(self, channel, data):
        msg = forseti2.Override.decode(data)
        self.robots[channel.split('/')[0]].override(msg.override)

    def handle_robot_state(self, channel, data):
        msg = forseti2.RobotState.decode(data)
        self.robots[channel.split('/')[0]].set_state(msg.running, msg.autonomous, msg.enabled)
        self.publish()

    def publish(self):
        for channel, robot in self.robots.items():
            msg = forseti2.RobotControl()
            msg.running, msg.autonomous, msg.enabled = robot.state
            self.lc.publish("%s/RobotControl" % channel, msg.encode())


class LiveScoreState(object):

    def __init__(self, msg=None):
        self.match_number = 0
        self.pearl = [0, 0, 0, 0]
        self.water_autonomous = [0, 0, 0, 0]
        self.treasure_autonomous = [0, 0, 0, 0]
        self.water_teleop = [0, 0, 0, 0]
        self.treasure_teleop = [0, 0, 0, 0]
        if msg:
            self.match_number = msg.match_number
            self.pearl = list(msg.pearl)
            self.water_autonomous = list(msg.water_autonomous)
            self.treasure_autonomous = list(msg.treasure_autonomous)
            self.water_teleop = list(msg.water_teleop)
            self.treasure_teleop = list(msg.treasure_teleop)

    def __iadd__(self, other):
        if type(other) != type(self):
            raise Exception("Invalid type...")
        if self.match_number != other.match_number:
            print("mismatched match numbers: %d server, %d client" % (self.match_number, other.match_number))
            return self
        attributes = ["pearl", "water_autonomous", "treasure_autonomous", "water_teleop", "treasure_teleop"]
        # element_wise addition
        for attr in attributes:
            setattr(self, attr, map(add, getattr(self, attr), getattr(other, attr)))
        return self

    def reset(self, match_number):
        self.match_number = match_number
        self.pearl = [0, 0, 0, 0]
        self.water_autonomous = [0, 0, 0, 0]
        self.treasure_autonomous = [0, 0, 0, 0]
        self.water_teleop = [0, 0, 0, 0]
        self.treasure_teleop = [0, 0, 0, 0]

    def as_lcm(self):
        msg = forseti2.LiveScore()
        for attribute in ["match_number", "pearl", "water_autonomous", "treasure_autonomous", "water_teleop", "treasure_teleop"]:
            setattr(msg, attribute, getattr(self, attribute))
        return msg

class LiveScoreServer(object):

    def __init__(self, lc):
        self.score = LiveScoreState()
        self.lc = lc
        self.lc.subscribe("LiveScore/ScoreDelta", self.handle_delta)

    def reset(self, match_number):
        self.score.reset(match_number)
        self.publish()

    def handle_delta(self, channel, data):
        msg = forseti2.LiveScore.decode(data)
        self.score += LiveScoreState(msg)
        self.publish()

    def publish(self):
        self.lc.publish("LiveScore/LiveScore", self.score.as_lcm().encode())

def main():
    lc = lcm.LCM(settings.LCM_URI)
    robot_controller = RobotController(lc, ["Robot0", "Robot1", "Robot2", "Robot3"])
    live_score_server = LiveScoreServer(lc)
    match_timer = MatchTimer(lc, robot_controller, live_score_server)
    match_timer.run()


if __name__ == '__main__':
    main()
