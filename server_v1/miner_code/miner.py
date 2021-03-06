import random as rand
import requests
import grequests
import time
import asyncio, threading, sys
import pprint as pp

from random import randint
from time import sleep
from settings import  *
serverurl = 'http://0.0.0.0:' #'http://10.89.91.27:5000' if int(sys.argv[1]) == 1 else 'http://0.0.0.0:5000'

completedChains = set()
open("money.txt","w").close()
open("info.txt","w").close()

oldAllocation = {'0': 0.5, '1': 0.5}
class Miner(threading.Thread ):
    #This initializes the Miner and its thread for execution
    def __init__(self,internalId, blocks, power=None):
        threading.Thread.__init__(self)
        self.totalCoins = 0
        self.internalID = internalId

        self.totalPower = power if power else rand.randint(50,100)
        self.attacker = True if power else False

        self.allChains = ['C1','C2']
        self.all_blocks = {}
        self.max_block_count = blocks

        print(serverurl+"/join/"+str(self.totalPower))
        r = requests.get(serverurl+"/join/"+str(self.totalPower))
        self.ID = eval(r.text)['data']['miner_id']
        print("Hello, I am Miner "+str(self.ID))
        self.discover_chains()
        if self.attacker is True:
            requests.get(serverurl+"/attacker/"+str(self.ID))

    def get_power(self):
        return self.totalPower

    def set_power(self,number):
        self.totalPower = number

    # When a miner is initialized, it will get information about the available chains through here
    def discover_chains(self):
        r = requests.get(serverurl+"/discover/")
        self.allChains = []
        keys = eval(r.text)['data'].keys()
        for i in keys:
            self.allChains.append(eval(r.text)['data'][i])
            self.allChains[-1]['my_relative_power'] = 0
            self.all_blocks[i] = 0

    # This is where the miner decides how much power to put into every chain
    def send_chain_power(self):
        #powerPerChain = int(self.totalPower/len(self.allChains))
        powerPerChain = {}
        if len(self.allChains) == 1:
            powerPerChain['0'] = self.totalPower
        else:
            payoffs = [i['reward']/max(i['total_power'],1) for i in self.allChains]
            oldAllocation['0'] = min(1,oldAllocation['0']+0.05) if payoffs[0] > payoffs[1] else max(0,oldAllocation['0'] - 0.05)
            oldAllocation['1'] = 1 - oldAllocation['0']
            powerPerChain['0'] = int(oldAllocation['0']*self.totalPower)
            powerPerChain['1'] = int(oldAllocation['1']*self.totalPower)
        urls = []
        for i,val in enumerate(self.allChains):
            if(self.attacker):
                if(i == 1) :
                    urls.append(serverurl+"/chain_powers/"+str(val['chain_id'])+'/0/'+str(self.ID))
                else:
                    urls.append(serverurl+"/chain_powers/"+str(val['chain_id'])+'/' + str(self.totalPower) + '/'+str(self.ID))
            else:
                urls.append(serverurl+"/chain_powers/"+str(val['chain_id'])+'/'+str(powerPerChain[str(i)])+'/'+str(self.ID))
        # print(self.ID," ",powerPerChain)
        result = (grequests.get(u) for u in urls)
        result = [eval(a.text)['data'] for  a in grequests.map(result)]
        for i in range(len(self.allChains)):
            # print("Miner " + str(self.ID) + " has relative power " + str(result[i]['relative_power']) + " on chain " + str(i+1))
            self.allChains[i]['my_relative_power'] = result[i]['relative_power']

    # Here the miner has already received its relative power, so it makes that
    # many guesses and tells the server if it got it right or not. If its the
    # the first miner to tell the server its right, it will get the reward
    def do_mining(self):
        for i,val in enumerate(self.allChains):
            numberTries = int(val['my_relative_power'] * 100)
            step = val['step']
            r = requests.get(serverurl+"/who_won/"+str(self.ID)+"/"+str(max_solution_size+1)+"/"+str(step)+'/'+str(val['chain_id']))
            data = eval(r.text)['data']
            self.allChains[i] = eval(r.text)['data']
            self.all_blocks[str(i+1)] = max( int(eval(r.text)['data']['step']) ,self.all_blocks[str(i+1)])

            actual_sol = str(eval(r.text)['data']['solution'])
            all_solutons = [str(rand.randint(0,max_solution_size+1)) for i in range(numberTries+1)]

            # if miner found the i am not on correct step skip
            if data['step'] == step:
                if actual_sol in all_solutons:
                    # send my solution for current block
                    r = requests.get(serverurl+"/who_won/"+str(self.ID)+"/"+actual_sol+"/"+str(val['step'])+'/'+str(val['chain_id']))
                    if(eval(r.text)['data']['step'] > step):
                        if(str(self.ID) == eval(r.text)['data']['winner_last']):
                            self.totalCoins += eval(r.text)['data']['reward']

                        completedChains.add(str(eval(r.text)['data']))
                        # break

    #This is the threading loop
    def run(self):
        start_time = time.time()

        current_round = 0
        while True:
            # sleep(randint(10,100)/100)
            if current_round >= self.max_block_count:
                break

            # print((current_round, self.max_block_count, self.all_blocks))
            self.send_chain_power()
            self.do_mining()

            current_blocks_discovered = 0
            for k,v in self.all_blocks.items():
                if int(k) == 1:
                    current_blocks_discovered+=int(v)
            # print(current_blocks_discovered)
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

def run_miners(blocks, miners, percentage, port):
    global serverurl
    serverurl = serverurl+str(port)
    Miners = []
    a = time.time()
    for i in range(miners):
        if i == miners - 1:
            power = sum([i.get_power() for i in Miners])
            new_power = int(( percentage * power ) / ( 1 - percentage)) + 1
            Miners.append(Miner(i, blocks, new_power))

        else:
            Miners.append(Miner(i, blocks))

    s = [i.start() for i in Miners]
    for m in Miners:
        m.join()

run_miners(blocks=int(sys.argv[1]), miners=int(sys.argv[2]), percentage=float(sys.argv[3]), port=int(sys.argv[4]))
