from flask import *
import threading
import lcm
import forseti2 as fs2
import sys
sys.path.append('../src')
import settings
import util
import time
import datetime

app = Flask(__name__)

@app.route('/')
def serve_console():
    return render_template('judge_console.html')

@app.route('/clock')
def serve_clock():
    return render_template('clock.html')

@app.route('/bar')
def serve_bar():
    return render_template('bar.html')

@app.route('/api/v1/score-delta', methods=["PUT", "POST"])
def score_delta():
    global seq
    args = {}
    for k, v in request.form.items():
        args[k] = int(v)
    seq.publish(**args)
    return "{success: true}"


# data container for persistent state
class FlaskInfo(object):
    def __init__(self):
        self._last_update_time = time.time()
        self.stored_a = 0

        self.game_time = 0.0
        self.stage_time = 0.0
        self.total_stage_time = 0.0
        self.stage_name = "none"
        self.bonus_time = 0.0

        self.blue_points = ['?', '?', '?', '?', 0]
        self.gold_points = ['?', '?', '?', '?', 0]
        self.bonus_possession = '?'
        self.bonus_points = '?'

        self.team_numbers = [0, 0, 0, 0]
        self.team_names = ['', '', '', '']
        self.match_number = -1

    def __setattr__(self, name, value):
        self.__dict__["_last_update_time"] = time.time()
        self.__dict__[name] = value

    def time_since_last_update(self):
        return time.time() - self._last_update_time

fi = FlaskInfo()
def comms_status():
    return "COMMS_UP" if fi.time_since_last_update() < 1 else "COMMS_DOWN"

@app.route('/api/v1/all-info')
def all_info():
    data = {
        'stored_a' : fi.stored_a,
        'comms_status' : comms_status(),
        'game_time' : fi.game_time,
        'stage_time' : fi.stage_time,
        'total_stage_time' : fi.total_stage_time,
        'stage_name' : fi.stage_name,
        'bonus_time' : fi.bonus_time,
        'blue_points' : fi.blue_points,
        'gold_points' : fi.gold_points,
        'bonus_possession' : fi.bonus_possession,
        'bonus_points' : fi.bonus_points,
        'team_numbers' : fi.team_numbers,
        'team_names' : fi.team_names,
        'match_number' : fi.match_number
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
    fi.blue_points = [m.blue_total, m.blue_autonomous_points, m.blue_normal_points, m.blue_permanent_points, m.blue_penalty]
    fi.gold_points = [m.gold_total, m.gold_autonomous_points, m.gold_normal_points, m.gold_permanent_points, m.gold_penalty]
    fi.bonus_possession = m.bonus_possession
    fi.bonus_points = m.bonus_points
    fi.bonus_time = m.bonus_time_remaining

def handle_time(channel, data):
    m = fs2.Time.decode(data)
    fi.game_time = m.game_time_so_far
    fi.stage_time = m.stage_time_so_far
    fi.total_stage_time = m.total_stage_time
    fi.stage_name = m.stage_name

def handle_match_init(channel, data):
    m = fs2.Match.decode(data)
    fi.team_numbers = m.team_numbers
    fi.team_names = m.team_names
    fi.match_number = m.match_number

def main():
    global lc, seq
    lc = lcm.LCM(settings.LCM_URI)
    lc.subscribe("xbox/state/debug/0", handle_xbox)
    lc.subscribe("score/state", handle_score)
    lc.subscribe("Timer/Time", handle_time)
    lc.subscribe("Match/Init", handle_match_init)
    seq = util.LCMSequence(lc, fs2.score_delta, "score/delta")
    try:
        while True:
            lc.handle()
    except KeyboardInterrupt:
        pass

def run_flask_app():
    app.run(host = '0.0.0.0', port=5002)

if __name__ == '__main__':
    t = threading.Thread(target = main)
    t.daemon = True
    t.start()

    run_flask_app()
