import json
import lcm
import settings
import forseti2
import time
import LCMNode
LCMNode = LCMNode.LCMNode



# handles business logic of robot state
# deals with emergency stop, manual override by field operators, and game state from timers
# TODO karthik-shanmugam: should e-stopped robot be treated differently from disabled?
class Robot(object):

    def __init__(self):
        self.enabled = False
        self.autonomous = True
        self.overridden = False
        self.estop = False

    def set_stage(self, stage_name):
        if not self.overridden:
            if stage_name in ["Setup", "Paused", "End"]:
                self.enabled = False
            elif stage_name == "Autonomous":
                self.autonomous = True
                self.enabled = True
            elif stage_name == "Teleop":
                self.autonomous = False
                self.enabled = True
            else:
                print "unrecognized stage: %s" % stage_name

    def emergency_stop(self, estop):
        self.estop = estop

    # for manual overriding of robot state (ignore timers)
    def override(self, override):
        self.overridden = override

    # manually set the state. only works if override is true
    def set_state(self, autonomous, enabled):
        if self.overridden:
            self.autonomous = autonomous
            self.enabled = enabled

    @property
    def state(self):
        return (self.estop, self.autonomous, self.enabled)

class RobotControllerNode(LCMNode):

    def __init__(self, lc, channels):
        self.lc = lc
        self.channels = channels
        self.robots = {channel: Robot() for channel in channels}
        self.lc.subscribe("Timer/Time", self.handleTime)
        for channel in channels:
            self.lc.subscribe("%s/Estop" % channel, self.handleEstop)
            self.lc.subscribe("%s/Override" % channel, self.handleOverride)
            self.lc.subscribe("%s/RobotState" % channel, self.handleRobotState)

    # time applies to every robot
    def handleTime(self, channel, data):
        msg = forseti2.Time.decode(data)
        for robot in self.robots.values():
            robot.set_stage(msg.stage_name)

    # these apply to individual robots
    def handleEstop(self, channel, data):
        msg = forseti2.Estop.decode(data)
        self.robots[channel.split('/')[0]].emergency_stop(msg.estop)

    def handleOverride(self, channel, data):
        msg = forseti2.Override.decode(data)
        self.robots[channel.split('/')[0]].override(msg.override)

    def handleRobotState(self, channel, data):
        msg = forseti2.RobotState.decode(data)
        self.robots[channel.split('/')[0]].set_state(msg.set_state)

    def run(self):
        while True:
            for channel, robot in self.robots.items():
                msg = forseti2.RobotControl()
                msg.estop, msg.autonomous, msg.enabled = robot.state
                self.lc.publish("%s/RobotControl" % channel, msg.encode())
            time.sleep(.3)

def main():
    print "Robot Controller Started"
    lc = lcm.LCM(settings.LCM_URI)
    robotNode = RobotControllerNode(lc, ["Robot0", "Robot1", "Robot2", "Robot3"])
    robotNode.start_thread()
    robotNode.run()


if __name__ == '__main__':
    main()