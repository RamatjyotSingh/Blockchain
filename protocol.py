from consensus import Consensus
from stats import Stats
from announce import Announce
from get_block import GetBlock
from gossip import Gossip

class Protocol:

    def __init__(self):
        self.consensus = Consensus()
        self.stats = Stats()
        self.announce = Announce()
        self.get_block = GetBlock()
        self.gossip = Gossip()
