import lcm
import forseti2
import time
import settings

class PiemosController:

    def __init__(self):
        self.lc = lcm.LCM(settings.LCM_URI)
        self.msg = forseti2.piemos_cmd()
        self.msg.header = forseti2.header()
        self.msg.header.seq = 0
        self.msg.header.time = time.time()
        self.msg.auton = False
        self.msg.game_time = 0;
        self.bad_rfids = [-1,-1,-1,-1]
        self.enable = False
        self.team_override= [True,True,True,True]

    def handle_override(self, channel, data):
        incMsg = forseti2.piemos_override.decode(data)
        self.team_override[incMsg.team] = not incMsg.override
        self.send_commands()

    def send_commands(self):
        self.msg.header.seq += 1
        if self.msg.game_time == 0:
            # Reset the bad rfid timers at the start of each match
            self.bad_rfids = [-1,-1,-1,-1]
        for station in range(4):
            self.msg.enabled = self.enable and self.team_override[station] and (self.msg.game_time > self.bad_rfids[station])
            self.msg.header.time = time.time()
            self.lc.publish("piemos"+str(station)+"/cmd", self.msg.encode())

    def handle_gamemode(self, channel, data):
        incMsg = forseti2.ControlData.decode(data)
        self.msg.auton = incMsg.AutonomousEnabled
        self.enable = incMsg.RobotEnabled
        self.msg.game_time = incMsg.Time
        self.send_commands()

    def handle_bad_rfid(self, channel, data):
        incMsg = forseti2.piemos_bad_rfid.decode(data)
        print("Got bad rfid time=" + str(self.msg.game_time) + " station="+str(incMsg.station))
        self.bad_rfids[incMsg.station] = self.msg.game_time + settings.BAD_RFID_DISABLE_SECONDS
        self.send_commands()

if __name__=='__main__':
    try:
        pc = PiemosController()
        pc.lc.subscribe("piemos/override", pc.handle_override)
        pc.lc.subscribe("piemos/Control", pc.handle_gamemode)
        pc.lc.subscribe("piemos/bad_rfid", pc.handle_bad_rfid)
        while(True):
            pc.lc.handle()
    except KeyboardInterrupt:
        raise

