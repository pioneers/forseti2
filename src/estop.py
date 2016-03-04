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

estop = forseti2.Estop()

estop.estop = True
#lc.publish("Match/Init", match_init.encode())
while True:
    raw_input("press enter to estop the field")
    lc.publish("Estop/Estop", estop.encode())




#lc.subscribe(".*", handle_all)
#TestNode(lc)
# while True:
#     pass




