import wx
import threading
import lcm
import random
import forseti2
import configurator

BLUE = (24, 25, 141)
GOLD = (241, 169, 50)

class Overrider(object):

    def __init__(self):
        self.lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')
        self.lc.subscribe('Schedule/Schedule', self.handle_schedule)
        self.lc.subscribe('Timer/Time', self.handle_time)
        self.match_list_box = None
        self.match_control = None
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True

    def

