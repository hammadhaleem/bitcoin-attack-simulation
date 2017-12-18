import random as rand
import requests
import grequests
import time
import asyncio, threading, sys
import pprint as pp

from random import randint
from time import sleep
from settings import  *
serverurl = 'http://0.0.0.0:5000' #'http://10.89.91.27:5000' if int(sys.argv[1]) == 1 else 'http://0.0.0.0:5000'

completedChains = set()
open("money.txt","w").close()
open("info.txt","w").close()


class Miner(threading.Thread ):
    #This initializes the Miner and its thread for execution
    def __init__(self,internalId, blocks):
        threading.Thread.__init__(self)
        self.totalCoins = 0
        self.internalID = internalId
        self.totalPower = rand.randint(90,100)
        self.allChains = ['C1','C2']
        self.all_blocks = {}
        self.max_block_count = blocks
        #self.strategy = strategy
        r = requests.get(serverurl+"/join/"+str(self.totalPower))
        self.ID = eval(r.text)['data']['miner_id']
        print("Hello, I am Miner "+str(self.ID))
        self.discover_chains()

    # When a miner is initialized, it will get information about the available chains through here
    def discover_chains(self):
        r = requests.get(serverurl+"/discover/")
        self.allChains = []
        keys = eval(r.text)['data'].keys()
        for i in keys:
            self.allChains.append(eval(r.text)['data'][i])
            self.allChains[-1]['my_relative_power'] = 0
            self.all_blocks[i] = {}

    # This is where the miner decides how much power to put into every chain
    def send_chain_power(self):
        powerPerChain = int(self.totalPower/len(self.allChains))
        urls = []

        for i,val in enumerate(self.allChains):
            urls.append(serverurl+"/chain_powers/"+str(val['chain_id'])+'/'+str(powerPerChain)+'/'+str(self.ID))

        result = (grequests.get(u) for u in urls)
        result = [eval(a.text)['data'] for  a in grequests.map(result)]
        for i in range(len(self.allChains)):
            # print("Miner " + str(self.ID) + " has relative power " + str(result[i]['relative_power']) + " on chain " + str(i+1))
            self.allChains[i]['my_relative_power'] = result[i]['relative_power']

    # Here the miner has already received its relative power, so it makes that
    #many guesses and tells the server if it got it right or not. If its the
    # the first miner to tell the server its right, it will get the reward
    def do_mining(self):
        for i,val in enumerate(self.allChains):
            numberTries = int(val['my_relative_power'] * 100)
            step = val['step']
            r = requests.get(serverurl+"/who_won/"+str(self.ID)+"/"+str(rand.randint(1,max_solution_size))+"/"+str(step)+'/'+str(val['chain_id']))
            data = eval(r.text)['data']


            # if miner found the i am not on correct step skip
            if data['step'] >= step:

                actual_sol = str(eval(r.text)['data']['solution'])

                # minimum tries
                # while  True and numberTries>=1:
                    # generate all solutions
                all_solutons = [str(rand.randint(1,max_solution_size)) for i in range(numberTries)]

                if actual_sol in all_solutons:
                    # send my solution for current block
                    r = requests.get(serverurl+"/who_won/"+str(self.ID)+"/"+actual_sol+"/"+str(val['step'])+'/'+str(val['chain_id']))
                    if(eval(r.text)['data']['step'] > step):

                        self.all_blocks[str(i+1)][int(data['step'])] = 1
                        if(str(self.ID) == eval(r.text)['data']['winner_last']):
                            self.totalCoins += eval(r.text)['data']['reward']

                        self.allChains[i] = eval(r.text)['data']
                        completedChains.add(str(eval(r.text)['data']))
                        # break
            else:
                self.all_blocks[str(i+1)][int(data['step'])] = 1

    #This is the threading loop
    def run(self):
        start_time = time.time()

        current_round = 0
        while True:
            sleep(randint(10,100)/100)
            if current_round >= self.max_block_count:
                break

            # print((current_round, self.max_block_count, self.all_blocks))
            self.send_chain_power()
            self.do_mining()

            current_blocks_discovered = 0
            for k,v in self.all_blocks.items():
                for k1,v1 in v.items():
                    current_blocks_discovered+=v1

            # print((self.internalID, self.all_blocks))
            with open("money.txt","a+") as f:
                f.write("Miner " + str(self.internalID) + " has Money " + str(self.totalCoins) + "\n")

            if current_blocks_discovered != current_round:
                if self.internalID == 0:
                    with open("info.txt",'a+') as f:
                        fi = float(int((time.time() - start_time)*100))/100
                        stri = "This is Info for block " + str(current_round)+" which took " + str(fi) + " seconds."
                        f.write(stri+"\n")
                        print(stri)
                        for i,val in enumerate(self.allChains):
                            f.write(str(val)+"\n")

                        start_time = time.time()

            current_round = current_blocks_discovered
            # print((self.all_blocks, current_blocks_discovered))
        #print("Miner " + str(self.ID) + " finished his round in " + str(time.time() - start_time))
        #print("Miner " + str(self.ID) + " sees " + str(self.allChains))

def run_miners(blocks, miners):
    Miners = []
    a = time.time()
    for i in range(miners):
        Miners.append(Miner(i, blocks))
    
    for m in  Miners:
        m.start()

run_miners(blocks=int(sys.argv[1]), miners=int(sys.argv[2]))
