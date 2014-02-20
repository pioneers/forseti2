import lcm
import forseti2
import threading
import time

class FakePiemos:

    def __init__(self):
        lc = lcm.LCM()
        self.msg = forseti2.piemos_health()
        self.msg.header = forseti2.header()
        self.msg.header.seq = 0
        self.msg.header.time = time.time()

        self._thread = threading.Thread(target=self.run)
        self._thread.daemon = True

    def start(self):
        self._thread.start()

    def run(self):
        while True:
            with open('/proc/uptime', 'r') as f:
                self.msg.uptime= float(f.readline().split()[0])
                print 'sending message'
                self.msg.header.seq+=1
                self.msg.header.time = time.time()
                lc.publish("piemos0/health", self.msg.encode())
                time.sleep(.30)

    def handle_health(self, channel, data):
        incMsg = forseti2.piemos_cmd.decode(data)
        self.msg.auton = incMsg.auton
        self.msg.enabled = incMsg.enabled

if __name__=='__main__':
    try:
        lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
        st = FakePiemos()
        lc.subscribe("piemos0/cmd", st.handle_health)
        st.start()

        while(True):
            lc.handle()
    except KeyboardInterrupt:
        raise
