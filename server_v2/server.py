
from flask import Flask

app_port = 8001
app = Flask(__name__)
app.config['DEBUG'] = True

from chain_sim import * 
from gui_elements import *

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=app_port, threaded=True)