from os import popen
import re
import sys
import settings
import threading
import lcm
import time
import util
import forseti2

CHANNEL_PREFIX = "xbox/state"
SLEEP_TIME = 0.01
LED_BLUE = 6 # LED 1
LED_GOLD = 7 # LED 2
LED_BONUS = 10 # Rotate LEDs

s = re.compile('[ :]')

class Event:
    def __init__(self,key,value,old_value):
        self.key = key
        self.value = value
        self.old_value = old_value
    def is_press(self):
        return self.value==1 and self.old_value==0
    def __str__(self):
        return 'Event(%s,%d,%d)' % (self.key,self.value,self.old_value)

def apply_deadzone(x, deadzone, scale):
    if x < 0:
        return (scale * min(0,x+deadzone)) / (32768-deadzone)
    return (scale * max(0,x-deadzone)) / (32768-deadzone)

def event_stream(deadzone=0,scale=32768,joystick=0,led=0):
    _data = None
    subprocess = popen('nohup xboxdrv --no-uinput -d -i {} -l {}'.format(
        joystick, led),'r',65536)
    while (True):
        line = subprocess.readline()
        if 'Error' in line:
            raise ValueError(line)
        data = filter(bool,s.split(line[:-1]))
        if len(data)==42:
            # Break input string into a data dict
            data = { data[x]:int(data[x+1]) for x in range(0,len(data),2) }
            if not _data:
                _data = data
                continue
            for key in data:
                if key=='X1' or key=='X2' or key=='Y1' or key=='Y2':
                    data[key] = apply_deadzone(data[key],deadzone,scale)
                if data[key]==_data[key]: continue
                event = Event(key,data[key],_data[key])
                yield event
            _data = data

class Joystick:
    BUTTONS = ["A", "B", "X", "Y", "LB", "RB", "back", "start", "guide", "UNUSED", "UNUSED"]
    AXES = ["X1", "Y1", "X2", "Y2", "LT", "RT"]
    MAX_STATE = 2**16
    def __init__(self, joystick=0, led=0):
        self.stream = None
        self.joystick = joystick
        self.led = led

        self.button_states = [False for _ in Joystick.BUTTONS]
        self.axis_states = [0 for _ in Joystick.AXES]
        self.state_id = 0

        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon=True
        self.thread.start()

    def _loop(self):
        for event in event_stream(4000, 100, joystick=self.joystick, led=self.led):
            if event.key in Joystick.BUTTONS:
                self.button_states[Joystick.BUTTONS.index(event.key)] = event.value
            elif event.key in Joystick.AXES:
                self.axis_states[Joystick.AXES.index(event.key)] = event.value
            self.state_id = (self.state_id + 1) % Joystick.MAX_STATE

def make_seq(lc, node_name, joystick):
    return util.LCMSequence(lc,
                            forseti2.xbox_joystick_state,
                            CHANNEL_PREFIX + "/" + node_name + "/" + str(joystick))

def main():
    joysticks = [Joystick(0, LED_BLUE),
                 Joystick(1, LED_GOLD),
                 Joystick(2, LED_BONUS)]

    lc = lcm.LCM(settings.LCM_URI)

    if len(sys.argv) > 1:
        node_name = sys.argv[1]
    else:
        node_name = "default"

    seqs = [make_seq(lc, node_name, joystick.joystick) for joystick in joysticks]

    current_state_ids = [0 for _ in range(3)]
    while True:
        time.sleep(SLEEP_TIME)
        for i in range(3):
            if joysticks[i].state_id != current_state_ids[i]:
                current_state_ids[i] = joysticks[i].state_id
                seqs[i].publish(axes=joysticks[i].axis_states,
                                buttons=joysticks[i].button_states)

if __name__ == '__main__':
    main()
