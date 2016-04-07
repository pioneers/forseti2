import lcm
import forseti2
import settings
import LCMNode

# def handle_all(channel, data):
#     print "received on %s:" % channel
#     print "    %s" % str(forseti2.Time.decode(data))

# class TestNode(LCMNode.LCMNode):
#     def __init__(self, lc):
#         self.lc = lc
#         self.start_thread()




lc = lcm.LCM(settings.LCM_URI)

match_init = forseti2.Match()
match_init.match_number = 0
match_init.team_numbers = [10, 1, 2, 3]
match_init.team_names = ['test0', 'test1', 'test2', 'test3']

match_start = forseti2.TimeControl()
match_start.command_name = "start"
#lc.publish("Match/Init", match_init.encode())
while True:
    raw_input("press enter to initialize a match")
    lc.publish("Match/Init", match_init.encode())
    raw_input("press enter to start autonomous")
    lc.publish("Timer/Control", match_start.encode())
    raw_input("press enter to start teleop")
    lc.publish("Timer/Control", match_start.encode())



#lc.subscribe(".*", handle_all)
#TestNode(lc)
# while True:
#     pass




