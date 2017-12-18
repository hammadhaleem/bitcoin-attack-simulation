# bitcoin-attack-simulation

The idea is to create a simplified simulation of bitcoin, to see if you can
introduce a new puzzle chain with its own reward to take power away from the main
chain, giving someone with < 50% effective control over the network.

Progress:

- Currently can only do basic simulations, haven't implemented attacker code yet
Running Instructions:

python server.py

python miner.py [num_of_blocks] [num_of_miners]
