import random as rand
import requests
import grequests
import time
import asyncio, threading, sys
import pprint as pp

from settings import  * 
serverurl = 'http://10.89.91.27:5000' if int(sys.argv[1]) == 1 else 'http://0.0.0.0:5000'

completedChains = set()
open("../miner/money.txt","w").close()
open("../miner/info.txt","w").close()


class Miner(threading.Thread ):
    def __init__(self,internalId):
        threading.Thread.__init__(self)
        self.totalCoins = 0
        self.internalID = internalId
        self.totalPower = rand.randint(1,100)
        self.allChains = ['C1','C2']
        #self.strategy = strategy
        r = requests.get(serverurl+"/join/"+str(self.totalPower))
        self.ID = eval(r.text)['data']['miner_id']
        print("Hello, I am Miner "+str(self.ID))
        self.discover_chains()

    def discover_chains(self):
        r = requests.get(serverurl+"/discover/")
        self.allChains = []
        keys = eval(r.text)['data'].keys()
        for i in keys:
            self.allChains.append(eval(r.text)['data'][i])
            self.allChains[-1]['my_relative_power'] = 0

    def send_chain_power(self):
        powerPerChain = int(self.totalPower/len(self.allChains))
        urls = []

        for i,val in enumerate(self.allChains):
            urls.append(serverurl+"/chain_powers/"+str(val['chain_id'])+'/'+str(powerPerChain)+'/'+str(self.ID))

        result = (grequests.get(u) for u in urls)
        result = [eval(a.text)['data'] for  a in grequests.map(result)]
        for i in range(len(self.allChains)):
            print("Miner " + str(self.ID) + " has relative power " + str(result[i]['relative_power']) + " on chain " + str(i+1))
            self.allChains[i]['my_relative_power'] = result[i]['relative_power']

    def do_mining(self):
        for i,val in enumerate(self.allChains):
            numberTries = int(val['my_relative_power'] * 100)
            step = val['step']
            r = requests.get(serverurl+"/who_won/"+str(self.ID)+"/"+str(rand.randint(1,max_solution_size))+"/"+str(step)+'/'+str(val['chain_id']))
            data = eval(r.text)['data']
            # if miner found the i am not on correct step skip 
            if data['step'] == step:

                actual_sol = str(eval(r.text)['data']['solution'])

                # minimum tries 
                # while  True and numberTries>=1: 
                    # generate all solutions 
                all_solutons = [str(rand.randint(1,max_solution_size)) for i in range(numberTries)]

                if actual_sol in all_solutons: 
                    # send my solution for current block
                    r = requests.get(serverurl+"/who_won/"+str(self.ID)+"/"+actual_sol+"/"+str(val['step'])+'/'+str(val['chain_id']))

                    if(eval(r.text)['data']['step'] > step):
                        if(str(self.ID) == eval(r.text)['data']['winner_last']):
                            self.totalCoins += eval(r.text)['data']['reward']
                        self.allChains[i] = eval(r.text)['data']
                        completedChains.add(str(eval(r.text)['data']))
                        # break

    def run(self):
        start_time = time.time()

        for i in range(number_of_rounds):
            if self.internalID == 0:
                with open("../miner/info.txt",'a+') as f:
                    f.write("This is Info for Round " + str(i)+" which took " + str(time.time() - start_time) + " seconds:\n")
                    for i,val in enumerate(self.allChains):
                        f.write(str(val)+"\n")
            self.send_chain_power()
            self.do_mining()

            with open("../miner/money.txt","a+") as f:
                f.write("Miner " + str(self.internalID) + " has Money " + str(self.totalCoins) + "\n")

        #print("Miner " + str(self.ID) + " finished his round in " + str(time.time() - start_time))
        #print("Miner " + str(self.ID) + " sees " + str(self.allChains))


r = requests.get(serverurl+"/refresh/")
Miners = []
a = time.time()
for i in range(int(sys.argv[2])):
    Miners.append(Miner(i))
    Miners[-1].start()

# list(map((lambda x: x.start()), Miners))
