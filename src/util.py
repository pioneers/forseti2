"""
Misc utilities
"""

import forseti2
import time

class LCMSequence:
    def __init__(self, lcm_instance, msg_type, channel_name, **defaults):
        self.lcm_instance = lcm_instance
        self.msg_type = msg_type
        self.channel_name = channel_name
        self.defaults = defaults
        self.debug = True

    def new_msg(self):
        msg = self.msg_type()
        msg.header = forseti2.header()
        msg.header.seq = 0
        msg.header.time = time.time()

        for k, v in self.defaults.items():
            msg.__setattribute__(k, v)

        return msg

    def publish(self, **kwargs):
        msg = self.new_msg()
        msg.header.seq+=1
        msg.header.time = time.time()

        for k, v in kwargs.items():
            msg.__setattr__(k, v)

        if self.debug:
            print "Sending", self.msg_type.__name__
            for k in set(self.defaults.keys()) | set(kwargs.keys()):
                print "  ", k, "=", msg.__getattribute__(k)

        self.lcm_instance.publish(self.channel_name, msg.encode())

        return msg

