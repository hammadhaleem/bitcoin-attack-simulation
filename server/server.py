from flask import Flask

app = Flask(__name__)
app.config['DEBUG'] = True

from chain_elements import * 
from gui_elements import *

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000,  threaded=True)