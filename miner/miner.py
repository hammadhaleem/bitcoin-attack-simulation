import random as rand
import requests
import grequests
import time
import asyncio, threading, sys
import pprint as pp
serverurl = 'http://10.89.91.27:5000' if int(sys.argv[1]) == 1 else 'http://0.0.0.0:5000'
class Miner(threading.Thread ):
    def __init__(self):
        threading.Thread.__init__(self)
        self.totalCoins = 0
        self.totalPower = rand.randint(1,100)
        self.allChains = ['C1','C2']
        r = requests.get(serverurl+"/join/"+str(self.totalPower))
        self.ID = eval(r.text)['data']['miner_id']

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
            self.allChains[i]['my_relative_power'] = result[i]['relative_power']
        #print(str(self.ID) + "\n" + str(result[1]))
    def do_mining(self):
        for i in range(len(self.allChains)):
            startVal,endVal = 0
            relativePower = self.allChains[i]['my_relative_power']


    def run(self):
        start_time = time.time()
        self.send_chain_power()
        # for i in mine_steps:
        #     print(i)
        #     self.do_mining()
        print("Finished in " + str(time.time() - start_time))


#r = requests.get(serverurl+"/refresh/")
Miners = []
a = time.time()
for i in range(100):
    Miners.append(Miner())
    Miners[-1].start()
