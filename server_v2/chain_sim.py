#!/usr/bin/python
# -*- coding: utf-8 -*-
import glob, os, json
import random, time
import networkx as nx
import shutil, uuid
import time, random, requests

from flask import jsonify
from flask import Flask
from flask import request

from subprocess import call

from server import *

number_of_chains = 1
max_solution_size = 1000

serverurl = 'http://0.0.0.0:' + str(int(app_port))

@app.route('/join/<power>')
def join(power):

    # lock based system to make sure all the miners have joined.
    while True:
        # time.sleep(0.01 * random.randint(10,100))
        if cache.get('join_lock') == False:

            miners = cache.get('miners')
            miners_ = cache.get('miners_')
            cache.set('join_lock', True, timeout=5 * 60 * 60)

            miner_id = str(uuid.uuid1())
            miners.append(miner_id)
            miners_[miner_id] = int(power)

            cache.set('miners_', miners_, timeout=5 * 60 * 60)
            cache.set('miners', miners, timeout=5 * 60 * 60)

            cache.set('join_lock', False, timeout=5 * 60 * 60)
            break

    return jsonify(data={'miner_id': miner_id})


@app.route('/get_all_miners')
def return_miner_info():
    winners_ledger = cache.get('winners_ledger')
    return jsonify(data={
        'miners': cache.get('miners_'),
        'total_miners': len(cache.get('miners'))
    })


@app.route('/solution/<miner_id>/<solution>/<current_block>')
def get_solution(miner_id, solution, current_block):

    time_ = int(time.time())
    solution = int(solution)
    current_block = int(current_block)

    while True:
        solution_global = cache.get('solution_global')
        current_block_global = cache.get('current_block_global')

        if current_block != current_block_global or solution != solution_global:
            return jsonify(data={'solution': 'not-accepted', 'current_block': current_block_global})

        if cache.get('lock') == False:
            lock = True
            cache.set('lock', True, timeout=5 * 60 * 60)
            break

    if lock == True:
        solution_global = cache.get('solution_global')
        current_block_global = cache.get('current_block_global')
        block_size = cache.get('block_size')

        if solution == solution_global and current_block_global == current_block:
            block_size.append(current_block_global + 1)
            current_block_global = current_block_global + 1
            solution_global = random.randint(1, current_block_global*10)

            winners_ledger = cache.get('winners_ledger')
            if winners_ledger is None:
                winners_ledger = {}
            winners_ledger[current_block] = miner_id

            cache.set('current_block_global', current_block_global, timeout=5 * 60 * 60)
            cache.set('solution_global', solution_global, timeout=5 * 60 * 60)
            cache.set('winners_ledger', winners_ledger, timeout=5 * 60 * 60)
            cache.set('block_size', block_size, timeout=5 * 60 * 60)

            cache.set('lock', False, timeout=5 * 60 * 60)

            return jsonify(data={'solution': 'accepted', 'current_block': current_block_global})

    return jsonify(data={'solution': 'not-accepted',
                   'current_block': current_block_global})

@app.route('/set_rounds/<rounds>')
def set_rounds(rounds):
    cache.set('max_rounds', int(rounds), timeout=5 * 60 * 60)
    return jsonify(data={'max_rounds': rounds})

@app.route("/reset")
@app.route("/reset/")
def reset():
    cache.set('lock', False,timeout=5 * 60 * 60)
    cache.set('join_lock', False,timeout=5 * 60 * 60)
    cache.set('miners', [],timeout=5 * 60 * 60)
    cache.set('miners_', {},timeout=5 * 60 * 60)
    cache.set('block_size', [1],timeout=5 * 60 * 60)
    cache.set('current_block_global', 1,timeout=5 * 60 * 60)
    cache.set('solution_global', 1,timeout=5 * 60 * 60)
    cache.set('winners_ledger', {}, timeout=5 * 60 * 60)
    cache.set('max_rounds', 50, timeout=5*60*60)

    return jsonify(data={
        'reset': True,
        'lock' : cache.get('lock'),
        'miners':cache.get('miners'),
        'miners':cache.get('miners_'),
        'block_size':cache.get('block_size'),
        'current_block_global':cache.get('current_block_global'),
        'solution_global':cache.get('solution_global'),
        'winners_ledger':cache.get('winners_ledger'),
    })

@app.route('/round')
def get_round():
    current_block_global = cache.get('current_block_global')
    return jsonify(data={'round': current_block_global})


@app.route('/winners')
def get_winners():
    winners_ledger = cache.get('winners_ledger')
    return jsonify(data={
        'winners': winners_ledger,
        'total_rounds_passed': max(winners_ledger.keys()),
        'all_miners': list(set(winners_ledger.values()))
    })
