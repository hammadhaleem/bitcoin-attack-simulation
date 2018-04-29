#!/usr/bin/python
# -*- coding: utf-8 -*-
import glob
import os
import json
import random
import time
import networkx as nx
import shutil
import uuid
import time
import random
import requests

from flask import jsonify
from flask import Flask
from flask import request

from subprocess import call

from server import *

number_of_chains = 1
max_solution_size = 1000

serverurl = 'http://0.0.0.0:' + str(int(app_port))

miners = []
miners_ = {}
block_size = [1]

current_block_global = 1
solution_global = random.randint(1, current_block_global)
lock = False
winners_ledger = {}


@app.route('/join/<power>')
def join(power):
    miner_id = str(uuid.uuid1())
    miners.append(miner_id)
    miners_[miner_id] = int(power)
    return jsonify(data={'miner_id': miner_id})


@app.route('/get_all_miners')
def return_miner_info():
    return jsonify(data={'miners': list(set(winners_ledger.values())),
                   'all_joined_miners': len(set(winners_ledger.values()))})


@app.route('/solution/<miner_id>/<solution>/<current_block>')
def get_solution(miner_id, solution, current_block):
    global current_block_global
    global solution_global
    global lock

    time_ = int(time.time())
    solution = int(solution)
    current_block = int(current_block)

    # print((solution, solution_global, current_block, current_block_global))

    while True:

        if current_block != current_block_global or solution \
            != solution_global:
            return jsonify(data={'solution': 'not-accepted',
                           'current_block': current_block_global})

        if lock == False:
            lock = True
            break

    if lock == True:
        if solution == solution_global\
         and current_block_global == current_block:
            block_size.append(current_block_global + 1)
            current_block_global = current_block_global + 1
            solution_global = random.randint(1, current_block_global)

            winners_ledger[current_block] = miner_id

            lock = False

            return jsonify(data={'solution': 'accepted'})

    return jsonify(data={'solution': 'not-accepted',
                   'current_block': current_block_global})

@app.route("/reset")
@app.route("/reset/")
def reset():
	global miners
	global miners_
	global block_size
	global current_block_global
	global solution_global
	global lock
	global winners_ledger

	miners = []
	miners_ = {}
	block_size = [1]

	current_block_global = 10
	solution_global = random.randint(1, current_block_global)
	lock = False
	winners_ledger = {}

	return jsonify(data={'reset': 1})

@app.route('/round')
def get_round():
    return jsonify(data={'round': current_block_global})


@app.route('/winners')
def get_winners():
    return jsonify(data={'winners': winners_ledger})
