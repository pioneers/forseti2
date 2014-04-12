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
        self.stored_a = 0
        self.last_time = time.time()

fi = FlaskInfo()
def game_time():
    time = datetime.datetime.now()
    result = time.second + time.microsecond / float(1000000) ;
    result += 60 * (time.minute % 3);
    return result

def comms_status():
    if fi.last_time + 1 < time.time():
        return 0
    else:
        return 1

def game_mode():
    time = game_time()
    if time < 20:
        return "Autonomous"
    return "Teleop"

@app.route('/api/v1/all-info')
def all_info():
    data = {
        'game-time' : game_time(),
        'comms-status' : comms_status(),
        'game-mode' : game_mode()
    }
    js = json.dumps(data)
    print js
    resp = Response(js, status=200, mimetype='application/json')
    return resp

def handle_lcm(channel, data):
    fi.last_time = time.time()
    msg = fs2.xbox_joystick_state.decode(data)
    fi.stored_a = msg.buttons[0]

def main():
    global lc
    lc = lcm.LCM(settings.LCM_URI)
    subscription = lc.subscribe("xbox/state/default/0", handle_lcm)
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
