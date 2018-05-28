import random 

from processing import *


number_of_miners=10
miners=[]
for i in range(number_of_miners):
	p=Miner(random.randint(3,4))
	p.start()
	miners.append(p)

[p.join() for p in miners]