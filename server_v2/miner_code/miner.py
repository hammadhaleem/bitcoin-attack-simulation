#!/usr/bin/python
# -*- coding: utf-8 -*-

import random as rand
import requests
import grequests
import time
import asyncio
import threading
import sys
import pprint as pp

from random import randint
from time import sleep
from multiprocessing import Process
import random

RUNNING_THREADS = 0
serverurl = 'http://0.0.0.0:8001'


class MinerThread(threading.Thread):

    # This initializes the Miner and its thread for execution

    def __init__(self, thread_id, max_rounds):
        threading.Thread.__init__(self)
        self.ID = thread_id
        self.miner_id = self.ID.split('_')[0]
        self.block_range = self.get_current_block_range()
        self.max_rounds = max_rounds

        self.ledger = {
            1:{},
            2:{},
            3:{}
        }

    def get_current_block_range(self):
        url = serverurl + '/round'
        data = eval(requests.get(url).text)['data']
        return data['round']

    def run_miner_logic(self, chain):
        try:
            solution = randint(1, self.block_range)

            url = serverurl + '/solution/{}/{}/{}'.format(
                    self.miner_id, solution,
                    self.block_range
            )

            self.ledger[chain][self.block_range] = 0

            # adding certain randomness in the whole process
            time.sleep(random.randint(1,100)*0.001)

            r = requests.get(url)
            data = eval(r.text)['data']

            if data['solution'] == 'accepted':
                self.ledger[chain][self.block_range] = 1

            # print(self.ledger)
            self.block_range = data['current_block']

        except Exception as e:
            print(e)
            pass

    def run(self):
        while True:
            self.run_miner_logic(chain=1)
            if self.max_rounds < self.block_range:
                break

        print(self.ID, self.ledger)


def create_multi_threaded_miners(number_of_threads, process_id, max_rounds):
    miners = []

    # print (serverurl + '/join/' + str(number_of_threads))
    r = requests.get(serverurl + '/join/' + str(number_of_threads))
    ID = eval(r.text)['data']['miner_id']
    # print ('Hello, I am Miner ' + str(ID))

    # discover_chains()
    # if self.attacker is True: requests.get(serverurl+"/attacker/"+str(self.ID))

    for i in range(number_of_threads):
        m = MinerThread(str(ID) + '_' + str(i), max_rounds)
        miners.append(m)

    # random.shuffle(miners)

    [m.start() for m in miners]
    [m.join() for m in miners]


def run_all(max_numer_of_miners=5, max_number_of_threads=2, max_rounds=100):
    sleep(0.1)
    requests.get(serverurl + '/reset/')
    data = eval(requests.get(serverurl+"/set_rounds/"+str(max_rounds)).text)['data']['max_rounds']

    start_time = time.time()
    processes = []
    for process_id in range(max_numer_of_miners):
        p = Process(target=create_multi_threaded_miners, args=(random.randint(1, max_number_of_threads), process_id, max_rounds))
        processes.append(p)

    [p.start() for p in processes]
    [p.join() for p in processes]

    return time.time() - start_time


max_rounds = 100

for i in range(1,1+10):
    i  = i * 10
    time_taken = run_all(max_numer_of_miners=i, max_number_of_threads=10, max_rounds=max_rounds)
    print("Total time taken for {} rounds= {}, number_of_miners={}".format(max_rounds, time_taken, i ))
    break
