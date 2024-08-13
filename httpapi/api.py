import os
import yaml
from flask import Flask, request, render_template, send_from_directory
from utils import ReadVersion
import subprocess

'''
usage: http://{YourServerURL}:{Port}/api?app=light&cmd=on
'''


# Constants
VALID_QUERY = ['app', 'cmd']
HTTPAPI_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(HTTPAPI_PATH) # api.pyの一つ上がroot
CONFIG_PATH = os.path.join(HTTPAPI_PATH, 'server.config.yaml')
VERSION = ReadVersion.get(os.path.join(HTTPAPI_PATH, 'static', 'config', 'version.info.json'))

# Flask settigns
app = Flask(__name__)
app._static_folder = os.path.join(HTTPAPI_PATH, 'static')

@app.route('/')
def index():
    return render_template(
        'index.html',
        version=VERSION,
    )

@app.route('/dashboard')
def dashboard():
    return render_template(
        'dashboard.html',
        version=VERSION,
    )

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'icons'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/apple-touch-icon.png')
def apple_tough_icon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'icons'), 'apple-touch-icon.png', mimetype='image/png')

@app.route('/api', methods=['GET'])
def api():
    if request.method == 'GET' and all(query in request.args for query in VALID_QUERY):
        # センサロギング系
        if str(request.args['app']) == "runscr":
            if str(request.args['cmd']) == "sensor":
                param = str(request.args['app']) + ':' + str(request.args['cmd'])
                command = f'python3 {ROOT_PATH}/sensor.py -pc ./static/logs/current.json -pl ./static/logs/history.json --test'
                scr_name = 'sensor.py'
            else:
                return f'{str(request.args["cmd"])}.py is not found'
            
        # リモコンコマンド送出系
        else:
            param = str(request.args['app']) + ':' + str(request.args['cmd'])
            command = f'python3 {ROOT_PATH}/irrp.py -p -g17 -f {ROOT_PATH}/codes {param}'
            scr_name = 'irrp.py'
        
        # 実行
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout == '':
            return f'Smartremocon has successfully sent a command ->   {param}'
        else:
            return f'Failed to execute {scr_name}'

    else:
        return f'Bad query'

if __name__ == '__main__':
    with open(CONFIG_PATH, 'r') as yml:
        config = yaml.safe_load(yml)
    app.run(debug=True, host=config['SERVER']['HOST'], port=config['SERVER']['PORT'])
