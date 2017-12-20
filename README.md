# Bitcoin attack simulation

Running Instructions:

python server.py

# Introdcution 
Researchers have discussed and proposed a plethora of attacks that allow for pools with less than 51% of the total CPU power to successfully gain control over the blockchain. With the prevalence of pools with a significant amount of CPU power at their disposal, it's becoming increasingly important to check whether these attacks can be carried out and, if they can be, how we can work to prevent them

Most of these proposed attacks are shown to be mathematically rigorous within their assumptions, but have not been experimentally tested in any meaningful way. This paper proposes a system to simulate various attacks on a blockchain based network and visually analyze various metrics during the attack; the system will also be capable of highlighting various weak points that are vulnerable to the attack being investigated.

To acheive the goals of this system, we will create simulated workers that are given incentive functions similar to real-world incentive mechanisms. We then allow users to select where to start an attack in the network and simulate the attack over time in the network, providing a way for researchers to test their hypothetical attacks. All of this is visually explorable via our system's visual analytics. 

* Simulation for `When cryptocurrencies mine their own business` ,  https://people.cs.uchicago.edu/~teutsch/papers/repurposing_miners.pdf
