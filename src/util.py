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
            msg.__setattr__(k, v)

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

def is_lcm_message(obj):
    """
    Check if an object is an instance of an LCM type

    LCM offers no official way to do this, so test for a uniquely-named method
    that is present in all LCM types
    """
    return '_get_packed_fingerprint' in dir(obj)


def print_lcm_msg(msg, indent='', indent_increment='  '):
    """
    Pretty-prints an LCM message to the console
    """
    print indent + msg.__module__ + ":"
    for slot in msg.__slots__:
        value = msg.__getattribute__(slot)
        if is_lcm_message(value):
            print indent + indent_increment + slot + ":"
            print_lcm_msg(value, indent + indent_increment)
        else:
            print indent + indent_increment + slot, "=", repr(value)
