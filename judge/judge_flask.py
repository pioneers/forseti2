from flask import *
import threading
import lcm
import forseti2 as fs2
import sys
sys.path.append('../src')
import settings
import time
import datetime

app = Flask(__name__)

@app.route('/')
def serve_console():
    return render_template('judge_console.html')

# data container for persistent state
class FlaskInfo(object):
    def __init__(self):
        self._last_update_time = time.time()
        self.stored_a = 0
        self.game_time = 0.0
        self.stage_name = "none"
        self.blue_points = [0, 0, 0, 0]
        self.gold_points = [0, 0, 0, 0]
        self.bonus_possession = 0
        self.bonus_points = 0


    def __setattr__(self, name, value):
        self.__dict__["_last_update_time"] = time.time()
        self.__dict__[name] = value

    def time_since_last_update(self):
        return time.time() - self._last_update_time

fi = FlaskInfo()
def game_time():
    time = datetime.datetime.now()
    result = time.second + time.microsecond / float(1000000) ;
    result += 60 * (time.minute % 3);
    return result

def comms_status():
    return int(fi.time_since_last_update() < 1)

def game_mode():
    time = game_time()
    if time < 20:
        return "Autonomous"
    return "Teleop"

@app.route('/api/v1/all-info')
def all_info():
    data = {
        'stored-a' : fi.stored_a,
        'game-time' : game_time(),
        'comms-status' : comms_status(),
        'game-mode' : game_mode(),
        'stage-name' : fi.stage_name,
        'blue_points' : fi.blue_points,
        'gold_points' : fi.gold_points,
        'bonus_possession' : fi.bonus_possession,
        'bonus_points' : fi.bonus_points
    }
    js = json.dumps(data)
    print js
    resp = Response(js, status=200, mimetype='application/json')
    return resp

def handle_xbox(channel, data):
    msg = fs2.xbox_joystick_state.decode(data)
    fi.stored_a = msg.buttons[fs2.xbox_joystick_state.GUIDE]

def handle_score(channel, data):
    m = fs2.score_state.decode(data)
    fi.blue_points = [m.blue_total, m.blue_normal_points, m.blue_permanent_points, m.blue_penalty]
    fi.gold_points = [m.gold_total, m.gold_normal_points, m.gold_permanent_points, m.gold_penalty]
    fi.bonus_possession = m.bonus_possession
    fi.bonus_points = m.bonus_points

def main():
    global lc
    lc = lcm.LCM(settings.LCM_URI)
    subscription = lc.subscribe("xbox/state/default/0", handle_xbox)
    sub = lc.subscribe("score/state", handle_score)
    try:
        while True:
            lc.handle()
    except KeyboardInterrupt:
        pass

def run_flask_app():
    app.run(debug = True)

if __name__ == '__main__':
    t = threading.Thread(target = main)
    t.daemon = True
    t.start()

    run_flask_app()
