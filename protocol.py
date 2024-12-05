from consensus import Consensus
from stats import Stats
from announce import Announce
from get_block import GetBlock
from gossip import Gossip
import socket

# The Protocol class is the main class that will be used to interact with the blockchain. It will be used to create the socket, and to initialize the other classes that will be used to interact with the blockchain. 
# The Protocol class will have the following attributes:
# - socket: This will be the socket that will be used to send and receive messages.
# - consensus: This will be an instance of the Consensus class that will be used to reach consensus on the blockchain.
# - stats: This will be an instance of the Stats class that will be used to keep track of the statistics of the blockchain.
# - announce: This will be an instance of the Announce class that will be used to announce new blocks to the network.
# - get_block: This will be an instance of the GetBlock class that will be used to get blocks from the network.
# - gossip: This will be an instance of the Gossip class that will be used to gossip with other nodes in the network.
# The Protocol class will have the following methods:
# - create_socket: This method will create a socket and return it.
# - init_get_block: This method will initialize the GetBlock class with the blockchain and the socket.
# - get_socket: This method will return the socket.

# important note : initialize each protocol type before using it

class Protocol:

    def __init__(self):
        self.socket = self.create_socket()
        self.consensus = None
        self.stats = None
        self.announce = None
        self.get_block = None
        self.gossip = None
        

    def create_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def init_get_block(self,blockchain):

        self.get_block = GetBlock(blockchain,self.socket)
    
    def get_socket(self):
        return self.socket