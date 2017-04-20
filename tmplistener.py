import lcm

import forseti2

def my_handler(channel, data):
    msg = forseti2.Heartbeat.decode(data)
    print("aasdfa %s" % msg.state)
"""
    print("Received message on channel \"%s\"" % channel)
    print("   timestamp   = %s" % str(msg.timestamp))
    print("   position    = %s" % str(msg.position))
    print("   orientation = %s" % str(msg.orientation))
    print("   ranges: %s" % str(msg.ranges))
    print("   name        = '%s'" % msg.name)
    print("   enabled     = %s" % str(msg.enabled))
    print("")
"""

def my_handler2(channel, data):
    msg = forseti2.Time.decode(data)
    print("gametime %s" % msg.game_time_so_far)
    print("stagetime %s" % msg.stage_time_so_far)
    print("totaltime %s" % msg.total_stage_time)
    print("stagename %s" % msg.stage_name)
   

def my_handler3(channel, data):
    msg = forseti2.Match.decode(data)
    print("matchnumver %s" % msg.match_number)
    print("teamnum %s" % msg.team_numbers)
    print("teamname %s" % msg.team_names)
 
lc = lcm.LCM()
subscription = lc.subscribe("Heartbeat/Beat", my_handler)
subscription2 = lc.subscribe("Timer/Time", my_handler2)
subscription2 = lc.subscribe("Timer/Match", my_handler3)

try:
    while True:
        lc.handle()
except KeyboardInterrupt:
    pass

lc.unsubscribe(subscription)
lc.unsubscribe(subscription2)

