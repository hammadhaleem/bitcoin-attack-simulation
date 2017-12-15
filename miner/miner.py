import random as rand
import requests
import time
serverurl = 'http://10.89.91.27:5000'
class Miner:
    def __init__(self):
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
        print(self.allChains)
    def send_chain_power(self):
        powerPerChain = int(self.totalPower/len(self.allChains))
        for i,val in enumerate(self.allChains):
            if i != (len(self.allChains) - 1):
                r = requests.get(serverurl+"/chain_powers/"+str(val['chain_id'])+'/'+str(powerPerChain)+'/'+str(self.ID))
                print(r.text)
            else:
                #GetInfo sent
                power = self.totalPower-(len(self.allChains)-1)*powerPerChain
                r = requests.get(serverurl+"/chain_powers/"+str(val['chain_id'])+'/'+str(power)+'/'+str(self.ID))
                print(r.text)
    #def do_mining(self):

Miners = []
a = time.time()
for i in range(3):
    Miners.append(Miner())
for i in range(3):
    Miners[i].discover_chains()
for i in range(3):
    Miners[i].send_chain_power()
print("COMPLETE")
print(time.time() - a)
