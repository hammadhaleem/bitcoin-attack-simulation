from flask import Flask, render_template
from flask import jsonify

import glob , os, json , random
import networkx as nx
from networkx.readwrite import json_graph
import shutil
from flask import Flask, Response
import uuid,time
import random

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
			'total_power' : 0,
			'winner_last' : None,
			'solution' : 10
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
	# time.sleep(10)
	while miners:
		miners.pop()

	s=set(miners_.keys())
	for i in s:
		del miners_[i]

	s=set(miners_mining.keys())
	for i in s:
		del miners_mining[i]

	s=set(chain_power_allocated.keys())
	for i in s:
		del chain_power_allocated[i]

	for i in range(1, number_of_chains+1):
		chains[i] = {
				'chain_id': i,
				'reward' : 10,
				'step' : 0,
				'total_power' : 0
			}

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

			if number_of_chains == len(chain_power_allocated.keys()) and \
				len(miners_.keys()) == len(chain_power_allocated[i].keys()):
				return_  = True
			else:
				return_ = False

		if return_ == True:
			break

	chain_info = chain_power_allocated[chain]


	powers = [ int(chain_info[miner]) for miner in chain_info.keys()]

	return jsonify(data={
		'relative_power' : float(current_power) / sum(powers),
		'powers' : str(powers),
		'miner_id' : miner_id,
		'chain': chain,
		'current_power' : current_power
	})


winning_lock = []
@app.route("/who_won/<miner_id>/<solution>/<chain_step>/<chain_id>")
def who_won(miner_id, solution, chain_step, chain_id):
	chain_id = int(chain_id)
	# verify minder id 

	winning_lock.append(miner_id)

	while True:

		obj = chain[chain_id]

		# it my turn 
		if winning_lock[0] == miner_id:
			break

		# someone else came before me 
		if obj['step'] > chain_step:
			break

	# update the chain if you won
	if  obj['step'] == chain_step and solution == obj['solution']:
		obj['step'] += 1
		obj['winner_last'] = miner_id
		obj['solution'] = random.randint(1,101)

		chain[chain_id] = obj

	# else get you didn't win you get winners name 
	winning_lock.pop(0)

	return jsonify(data=obj)



@app.route("/")
@app.route("/get_info_response/")
def get_info_response(next_id=0):

	return jsonify( data ={})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)