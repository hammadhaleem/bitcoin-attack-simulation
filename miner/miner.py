import random as rand
import requests
import grequests
import time
import asyncio, threading, sys
import pprint as pp
serverurl = 'http://10.89.91.27:5000'
class Miner(threading.Thread ):
    def __init__(self):
        threading.Thread.__init__(self)
        self.totalCoins = 0
        self.totalPower = rand.randint(1,100)
        self.allChains = ['C1','C2']
        r = requests.get(serverurl+"/join/"+str(self.totalPower))
        self.ID = eval(r.text)['data']['miner_id']
    def discover_chains(self):
        r = requests.get(serverurl+"/discover/")
        self.allChains = []
        keys = eval(r.text)['data'].keys()
        for i in keys:
            self.allChains.append(eval(r.text)['data'][i])
            self.allChains[-1]['my_relative_power'] = 0
        #print(self.allChains)

    def send_chain_power(self):
        powerPerChain = int(self.totalPower/len(self.allChains))
        urls = []
        for i,val in enumerate(self.allChains):
            urls.append(serverurl+"/chain_powers/"+str(val['chain_id'])+'/'+str(powerPerChain)+'/'+str(self.ID))
            #r = requests.get(serverurl+"/chain_powers/"+str(val['chain_id'])+'/'+str(powerPerChain)+'/'+str(self.ID))
            # if i != (len(self.allChains) - 1):
            #     r = requests.get(serverurl+"/chain_powers/"+str(val['chain_id'])+'/'+str(powerPerChain)+'/'+str(self.ID))
            #     print(r.text)
            #     #self.allChains[i]['my_relative_power'] =
            # else:
            #     #GetInfo sent
            #     power = self.totalPower-(len(self.allChains)-1)*powerPerChain
            #     r = requests.get(serverurl+"/chain_powers/"+str(val['chain_id'])+'/'+str(power)+'/'+str(self.ID))
            #     print(r.text)
        result = (grequests.get(u) for u in urls)
        result = [eval(a.text) for  a in grequests.map(result)]

        for i in result:
            pp.pprint(i)
        #print(str(self.ID) + "\n" + str(result[1]))
    #def do_mining(self):

    def run(self):
        a = time.time()
        self.discover_chains()
        self.send_chain_power()
        #print("Finished in " + str(time.time() - a))


r = requests.get(serverurl+"/refresh/")
Miners = []
a = time.time()
for i in range(3):
    Miners.append(Miner())
    Miners[-1].start()
