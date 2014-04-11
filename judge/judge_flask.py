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

stored_time = 0
last_time = time.time()
def game_time():
    time = datetime.datetime.now()
    result = 60 - (time.second + time.microsecond / float(1000000)) 
    if time.minute % 2:
        result += 60
    return result

def comms_status():
    if last_time + 1 < time.time():
        return 0
    else:
        return 1

@app.route('/api/v1/all-info')
def all_info():
    data = {
        'game-time' : game_time(),
        'comms-status' : comms_status()
    }
    js = json.dumps(data)
    print js
    resp = Response(js, status=200, mimetype='application/json')
    return resp

def handle_xbox(channel, data):
    global stored_time
    global last_time
    last_time = time.time()
    msg = fs2.xbox_joystick_state.decode(data)
    stored_time = msg.buttons[0]

def main():
    global lc
    lc = lcm.LCM(settings.LCM_URI)
    subscription = lc.subscribe("xbox/state/default/0", handle_xbox)
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
