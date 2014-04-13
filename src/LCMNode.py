from __future__ import print_function

import forseti2
import configurator
import json
import lcm
import threading
import time
import random
import os
import settings
import util

lc_lock = threading.Lock()

class Node(object):

    def start_thread(self):
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.thread.start()

    def _loop(self):
        raise NotImplemented()


class LCMNode(Node):

    def _loop(self):
        while True:
            try:
                lc_lock.acquire()
                self.lc.handle()
            except Exception as ex:
                print('Got exception while handling lcm message', ex)
            finally:
                lc_lock.release()

