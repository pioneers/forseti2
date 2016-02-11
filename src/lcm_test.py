import lcm
import forseti2
import settings
import LCMNode

def handle_all(channel, data):
    print "received on %s:" % channel
    print "    %s" % str(forseti2.Time.decode(data))

class TestNode(LCMNode.LCMNode):
    def __init__(self, lc):
        self.lc = lc
        self.start_thread()




lc = lcm.LCM(settings.LCM_URI)

match_init = forseti2.Match()
lc.publish("Match/Init", match_init.encode())

match_start = forseti2.TimeControl()
match_start.command_name = "start"
lc.publish("Match/Init", match_init.encode())
lc.publish("Timer/Control", match_start.encode())

#lc.subscribe(".*", handle_all)
#TestNode(lc)
# while True:
#     pass




