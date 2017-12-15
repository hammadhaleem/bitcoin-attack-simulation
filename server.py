from flask import Flask, render_template
from flask import jsonify

import glob , os, json , random
import networkx as nx
from networkx.readwrite import json_graph
import shutil
from flask import Flask, Response
import uuid,time

from settings import * 

chain_step = 0 

initialize_lock = []
state_cache ={}

miners  = []
miners_ ={}


miners_mining  = {}

## chain information 
chains = {}
for i in range(1, number_of_chains+1):
	chains[i] = {
			'chain_id': i,
			'reward' : 10,
			'step' : 0,
			'total_power' : 0
		}

chain_power_allocated = {
	
}
# # # # # 

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/favicon.ico")
def return_none():
	return jsonify({})

## Function to debugg 
@app.route("/get_all_chains")
def return_chains():
	return jsonify(data=
			{
				'chain_power_allocated':chain_power_allocated,
				'chains' : chains
			}
	)

@app.route("/get_all_miners")
def return_miner_info():
	return jsonify(data={'miners' : miners_, 'all_joined_miners':len(miners_.keys()) })

@app.route('/refresh/')
@app.route('/refresh')
def refresh():
	while miners:
		miners_.pop()

	for i in miners_.keys():
		del miners_[i]


	for i in miners_mining.keys():
		del miners_[i]


	for i in chain_power_allocated.keys():
		del chain_power_allocated[i]


	for i in range(1, number_of_chains+1):
		chains[i] = {
				'chain_id': i,
				'reward' : 10,
				'step' : 0,
				'total_power' : 0
			}


	print(miners_mining)
	return jsonify(data={})

@app.route('/join/<power>')
def join(power):
	miner_id = str(uuid.uuid1())
	miners.append(miner_id)
	miners_[miner_id] = int(power)
	return jsonify(data={'miner_id': miner_id})
	

@app.route('/discover/')
def discover_chains():
	return jsonify(data=chains)

@app.route("/chain_powers/<chain>/<current_power>/<miner_id>")
def chain_powers(chain, current_power, miner_id):
	current_power = int(current_power)
	chain = int(chain)

	if int(current_power) < miners_[miner_id]:
		try:
			chain_power_allocated[chain][miner_id] = current_power
		except:
			chain_power_allocated[chain] = {}
			chain_power_allocated[chain][miner_id] = current_power


	while True:
		return_ = False
		for i in range(1, number_of_chains+1):
			# print(("wait", number_of_chains , len(chain_power_allocated.keys())))

			if number_of_chains == len(chain_power_allocated.keys()) and \
				len(miners_.keys()) == len(chain_power_allocated[i].keys()):
				return_  = True
			else:
				return_ = False

		if return_ == True:
			break


	return jsonify(data=chain_power_allocated)


@app.route("/who_won/<miner_id>/<solution>/<chain_step>/<chain_id>")
def who_won(next_id):


	# if chain_step != current_step:
	# 	# tell you lost, 
	# 	# tell go to get_info_again
	# else:
	# 	# get lock 
	# 	# update state 
	# 	# release lock 
	# 	# change state 
	# while locks

	return jsonify(data={'error' : str(e)})

@app.route("/")
@app.route("/get_info_response/")
def get_info_response(next_id=0):

	return jsonify( data ={})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)