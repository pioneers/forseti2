import lcm
import forseti2
import settings
import time

# def handle_all(channel, data):
#     print "received on %s:" % channel
#     print "    %s" % str(forseti2.Time.decode(data))

# class HeartbeatNode(LCMNode.LCMNode):
#     def __init__(self, lc):
#         self.lc = lc
#         self.start_thread()




lc = lcm.LCM(settings.LCM_URI)
contracted = forseti2.Heartbeat()
contracted.state = False
contracted = contracted.encode()

expanded = forseti2.Heartbeat()
expanded.state = True
expanded = expanded.encode()

times = [1,1]
last = time.time()
state = 0
while True:
    if time.time() - last > times[state]:
        last = time.time()
        state += 1
        state = state % len(times)
        lc.publish("Heartbeat/Beat", expanded if state % 2 else contracted)

# match_init = forseti2.Match()
# lc.publish("Match/Init", match_init.encode())

# match_start = forseti2.TimeControl()
# match_start.command_name = "start"
# lc.publish("Match/Init", match_init.encode())
# lc.publish("Timer/Control", match_start.encode())

#lc.subscribe(".*", handle_all)
#TestNode(lc)
# while True:
#     pass




