from flask import *
app = Flask(__name__)

greeting = 'Hello World'
name = "Andrew"

@app.route('/')
def serve_console():
    return render_template('judge_console.html')

@app.route('/api/v1/<method>', methods=['GET', 'POST'])
def api(method):
    if request.method == 'POST':
        return greeting
    else:
        pass

if __name__ == '__main__':
    app.run(debug = True)