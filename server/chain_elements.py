import glob , os, json , random, time
import networkx as nx
import shutil
import uuid,time
import random
import requests

from flask import jsonify
from flask import Flask
from flask import request

from subprocess import call

from server import *

number_of_chains = 1
max_solution_size = 1000

serverurl = 'http://0.0.0.0:'+str(int(app_port))

chain_step = 0

initialize_lock = []
state_cache ={}

winning_lock = []
miners  = []

miners_ ={}
miners_mining  = {}

## chain information
chain_power_allocated = {}
chains = {}
winners_list = {}
attacker_id = None

for i in range(1, number_of_chains+1):
	chains[i] = {
			'chain_id': i,
			'reward' : 10,
			'step' : 0,
			'total_power' : 0,
			'winner_last' : -1,
			'solution' : random.randint(1,max_solution_size),
			'winner' : -1
		}

	winners_list[i] = []


@app.route("/send_parameters/", methods=['GET', 'POST'])
@app.route("/send_parameters", methods=['GET', 'POST'])
def receive_parameters():
	r = requests.get(serverurl+"/refresh/")

	data_rec  = request.form
	chains_rec = int(data_rec['Chains'])
	blocks_rec  = int(data_rec['Blocks'])
	miners_rec  = int(data_rec['Miners'])
	attacker_power = float(data_rec['AttackerPower'])
	reward_rec = float(data_rec['Reward'])

	global number_of_chains
	number_of_chains = chains_rec

	for i in range(1, number_of_chains+1):
		if i == number_of_chains:
			reward = reward_rec
		else:
			reward = 10.0

		chains[i] = {
			'chain_id': i,
			'reward' : reward,
			'step' : 0,
			'total_power' : 0,
			'winner_last' : -1,
			'solution' : random.randint(1,max_solution_size),
			'winner' : -1
		}

		winners_list[i] = []

	stri = "python3 miner_code/miner.py {} {} {} {}".format( str(blocks_rec), str(miners_rec), str(attacker_power), str(app_port))
	os.system(stri)

	return jsonify(data="true")


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
	return jsonify(data={
		'miners' : miners_,
		'all_joined_miners':len(miners_.keys())
	})

@app.route('/ledger')
def ledger():
	data = {}
	for k,value in winners_list.items():
		data[k] = {}
		for i in value:
			try:
				data[k][i['winner']]['coins'] += i['reward']
			except:
				data[k][i['winner']] ={}
				data[k][i['winner']]['coins'] = i['reward']
				data[k][i['winner']]['power'] = miners_[i['winner']]

	return jsonify(data={
		'account': data,
		'sequence':winners_list,
		'miners' : miners_,
		'attacker' : attacker_id
	})

@app.route("/attacker/<miner_id>")
def set_attacker(miner_id):
	global attacker_id
	attacker_id = miner_id
	return jsonify(data={})


@app.route('/refresh/')
@app.route('/refresh')
def refresh():
	# time.sleep(10)
	global number_of_chains
	number_of_chains = 1

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

	s=set(winners_list.keys())
	for i in s:
		winners_list[i]=[]

	s=set(chains.keys())
	for i in s:
		del chains[i]


	for i in range(1, 2):
		chains[i] = {
				'chain_id': i,
				'reward' : 10,
				'step' : 0,
				'total_power' : 0,
				'winner_last' : -1,
				'solution' : random.randint(1,max_solution_size)
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
	# print("In chain power ",int(current_power)," ",miners_[miner_id])
	if int(current_power) <= miners_[miner_id]:
		try:
			chain_power_allocated[chain][miner_id] = current_power
		except:
			chain_power_allocated[chain] = {}
			chain_power_allocated[chain][miner_id] = current_power


	while True:
		return_ = False
		for i in range(1, number_of_chains+1):

			# print(number_of_chains," ",len(chain_power_allocated.keys()))
			if number_of_chains == len(chain_power_allocated.keys()) and \
				len(miners_.keys()) == len(chain_power_allocated[i].keys()):
				return_  = True
			else:
				return_ = False
		if return_ == True:
			break

	chain_info = chain_power_allocated[chain]

	powers = [ int(chain_info[miner]) for miner in chain_info.keys()]
	chains[chain]['total_power'] = sum(powers)
	# print((powers,float(current_power) / sum(powers) ))
	return jsonify(data={
		'relative_power' : float(current_power) / sum(powers),
		'powers' : str(powers),
		'miner_id' : miner_id,
		'chain': chain,
		'current_power' : current_power
	})

@app.route("/who_won/<miner_id>/<solution>/<chain_step>/<chain_id>")
def who_won(miner_id, solution, chain_step, chain_id):
	chain_id = int(chain_id)
	# verify minder id

	winning_lock.append(miner_id)

	while True:
		obj = chains[chain_id]

		# it my turn
		if winning_lock[0] == miner_id:
			break

		# someone else came before me
		if int(obj['step']) > int(chain_step):
			break

	# its my turn
	obj = chains[chain_id]

	# update the chain if you won
	if  int(obj['step']) == int(chain_step) and int(solution) == int(obj['solution']):

		# i am the winner
		obj['winner'] = miner_id
		obj['time'] =  time.time()
		# print((obj, miner_id,chain_id))
		winners_list[chain_id].append(obj.copy())

		obj['step'] += 1
		obj['winner_last'] = miner_id
		obj['solution'] = random.randint(1,max_solution_size)
		obj['winner'] = -1
		# with open('results.txt','a') as f:
		# 	f.write("SOLUTION FOUND FOR CHAIN "+str(obj['chain_id']) + " BY " + str(miner_id)+"\n")
		# 	f.write(str(obj)+"\n")
		# 	f.close()
		chains[chain_id] = obj

		with open('winners_list.json', 'w') as outfile:
			data = json.dumps(winners_list, indent=4, sort_keys=True)
			outfile.write(data)

	# else get you didn't win you get winners name
	winning_lock.pop(0)
	return jsonify(data=obj)

@app.route("/get_info_response/")
def get_info_response(next_id=0):
	return jsonify( data ={})
