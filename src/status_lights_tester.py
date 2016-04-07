import lcm
import forseti2
import settings
import LCMNode
import time
# def handle_all(channel, data):
#     print "received on %s:" % channel
#     print "    %s" % str(forseti2.Time.decode(data))

# class TestNode(LCMNode.LCMNode):
#     def __init__(self, lc):
#         self.lc = lc
#         self.start_thread()




lc = lcm.LCM(settings.LCM_URI)



def make_packet((num, r, y, g)):
    status_light = forseti2.StatusLight()
    status_light.red = r == 1
    status_light.yellow = y == 1
    status_light.green = g == 1
    status_light.buzzer = False
    return "StatusLight%d/StatusLight" % num, status_light

def grid():
    lights = [make_packet((num, num%2, 1-num%2, num%2)) for num in range(8)]
    for channel, msg in lights:
        lc.publish(channel, msg.encode())
    time.sleep(.1)
    lights = [make_packet((num, 1-num%2, num%2, 1-num%2)) for num in range(8)]
    for channel, msg in lights:
        lc.publish(channel, msg.encode())
    time.sleep(.1)



#lc.publish("Match/Init", match_init.encode())
while True:
    #grid()
    #continue
    channel, status_light = make_packet(eval(raw_input("enter (light_number, r, y, g): ")))

    lc.publish(channel, status_light.encode())




#lc.subscribe(".*", handle_all)
#TestNode(lc)
# while True:
#     pass




