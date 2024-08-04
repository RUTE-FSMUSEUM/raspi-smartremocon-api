import os
import yaml
from flask import Flask, request, render_template, send_from_directory
import subprocess

'''
usage: http://{YourServerURL}:{Port}/api?app=light&cmd=on
'''

# Flask settigns
app = Flask(__name__)
app._static_folder = "./static"

# Constants
VALID_QUERY = ['app', 'cmd']
ROOT_PATH = '../'
CONFIG_PATH = './server.config.yaml'

@app.route('/')
def index():
    return 'Hello world'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'icons'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/apple-touch-icon.png')
def apple_tough_icon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'icons'), 'apple-touch-icon.png', mimetype='image/png')

@app.route('/api', methods=['GET'])
def api():
    if request.method == 'GET' and all(query in request.args for query in VALID_QUERY):
        param = str(request.args['app']) + ':' + str(request.args['cmd'])
        command = f'python3 {ROOT_PATH}/irrp.py -p -g17 -f {ROOT_PATH}/codes {param}'
        

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout == '':
            return f'Smartremocon has successfully sent a command ->   {param}'
        else:
            return f'Failed to execute irrp.py'

    else:
        return f'Bad query'

if __name__ == '__main__':
    with open(CONFIG_PATH, 'r') as yml:
        config = yaml.safe_load(yml)
    app.run(debug=True, host=config['SERVER']['HOST'], port=config['SERVER']['PORT'])
