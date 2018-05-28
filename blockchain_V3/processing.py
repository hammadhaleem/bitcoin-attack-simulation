import multiprocessing
import sys
import re, time
import uuid, random
from random import randrange
from multiprocessing import Process, Queue
from multiprocessing import Process, Lock

def FermatPrimalityTest(number):
    ''' if number != 1 '''
    if (number > 1):
        ''' repeat the test few times '''
        for time in range(3):
            ''' Draw a RANDOM number in range of number ( Z_number )  '''
            randomNumber = random.randint(2, number)-1
            
            ''' Test if a^(n-1) = 1 mod n '''
            if randomNumber ** (number-1) % number != 1:
                return False
        
        return True
    else:
        ''' case number == 1 '''
        return False  


class MinerWorker(multiprocessing.Process):

    def __init__(self,miner_id, worker_id, chain, lock, data_set):
        multiprocessing.Process.__init__(self)
        self.miner_id = str(miner_id)
        self.worker_id = str(worker_id)
        self.chain = chain
        self.lock=lock
        self.data_set=data_set
        return

    def run(self):
        for i in self.data_set:
            sol = FermatPrimalityTest(i)
            sol1 = FermatPrimalityTest(i)
            
            if sol == True and sol == sol1:
                self.lock.acquire()

                lis = self.chain.get()
                lis.append(i)

                self.chain.put(lis)
                self.lock.release()

        return

class Miner(multiprocessing.Process):

    def __init__(self,power):
        multiprocessing.Process.__init__(self)
        self.miner_id = uuid.uuid1()
        self.power= power
        self.lock = Lock()
        self.chain = Queue()
        self.chain.put([])
        return

    def split(self, arr, size):
        L = len(arr)
        assert 0 < size <= L
        s, r = divmod(L, size)
        t = s + 1
        a = ([arr[p:p+t] for p in range(0, r*t, t)] + [arr[p:p+s] for p in range(r*t, L, s)])
        return a

    def compute_solution(self, start, end):
        try:

            lists = self.split(list(range(start, end)) , self.power)

            m=[]
            for li in lists: 
                m.append(MinerWorker(self.miner_id, lists.index(li),  self.chain, self.lock, li))

            [i.start() for i in m]
            [i.join() for i in m]

            return 1
        except Exception as e:
            print(e)
            return 0

    def run(self):
        chain =[]
        """
        Overloaded function provided by multiprocessing.Process.  Called upon start() signal
        """
        start_time = time.time()
        
        start = 2
        end = start + 100

        while  True:
            # create threads
            if self.compute_solution(start, end) == 1:

                self.lock.acquire()
                chain_items = self.chain.get()

                print("Miner ID: {}\tPower: {} Total_Primes_found {} Time taken {} ".format(self.miner_id, self.power, len(chain), (time.time() - start_time)))
                
                chain.extend(chain_items)

                self.chain.put(chain_items)
                self.lock.release()

            if end > 5000:
                return

            start = end
            end = start + 100






