import random as rand
import requests
import grequests
import time
import asyncio, threading, sys
import pprint as pp
serverurl = 'http://10.89.91.27:5000' if int(sys.argv[1]) == 1 else 'http://0.0.0.0:5000'

completedChains = set()
open('../server/results.txt', 'w').close()
class Miner(threading.Thread ):
    def __init__(self,strategy):
        threading.Thread.__init__(self)
        self.totalCoins = 0
        self.totalPower = rand.randint(1,100)
        self.allChains = ['C1','C2']
        self.strategy = strategy
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
            #print("Miner " + str(self.ID) + " has relative power " + str(result[i]['relative_power']) + " on chain " + str(i+1))
            self.allChains[i]['my_relative_power'] = result[i]['relative_power']

    def do_mining(self):
        for i,val in enumerate(self.allChains):
            numberTries = int(val['my_relative_power'] * 100)
            step = val['step']
            #print("Miner " + str(self.ID) + " has " + str(numberTries) + " number of Attempts on chain " + str(i+1))
            while numberTries >= 0:
                sol = str(rand.randint(1,100))
                #print("Trying solution "+sol)
                r = requests.get(serverurl+"/who_won/"+str(self.ID)+"/"+sol+"/"+str(val['step'])+'/'+str(val['chain_id']))
                numberTries -= 1
                if(eval(r.text)['data']['step'] > step):
                    if(str(self.ID) == eval(r.text)['data']['winner_last']):
                        self.totalCoins += eval(r.text)['data']['reward']
                    self.allChains[i] = eval(r.text)['data']
                    completedChains.add(str(eval(r.text)['data']))
                    break

    def run(self):
        start_time = time.time()
        for i in range(sys.argv[3]):
            self.send_chain_power()
            self.do_mining()
            if(i == 9) :
                with open("../server/results.txt","a") as f:
                    f.write("Miner " + str(self.ID) + " had Money/Power Ratio " + str(self.totalCoins/self.totalPower) + "\n")
                    #f.write("Miner " + str(self.ID) + " has money " + str(self.totalCoins) + " had Power " + str(self.totalPower) + "\n")
        #print("Miner " + str(self.ID) + " finished his round in " + str(time.time() - start_time))
        #print("Miner " + str(self.ID) + " sees " + str(self.allChains))


r = requests.get(serverurl+"/refresh/")
Miners = []
a = time.time()
for i in range(int(sys.argv[2])):
    Miners.append(Miner(0))
    Miners[-1].start()
