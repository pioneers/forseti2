from flask import *
import threading
import lcm
import forseti2 as fs2
import sys
sys.path.append('../src')
import settings
import time

app = Flask(__name__)

@app.route('/')
def serve_console():
    return render_template('judge_console.html')

stored_time = 0
last_time = time.time()
@app.route('/api/v1/game-time')
def game_time():
    return str(stored_time)

@app.route('/api/v1/comms-status')
def cs():
    if last_time + 1 < time.time():
        return str(0)
    else:
        return str(1)

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
