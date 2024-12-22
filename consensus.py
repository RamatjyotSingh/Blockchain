import time


class Consensus:

    LAST_CONSENSUS = time.time()


    def __init__(self,peer,consensus_interval):
        self.peer = peer
        self.CONSENSUS_INTERVAL = consensus_interval

    def do_consensus(self):
        current_time = time.time()
        if current_time - self.LAST_CONSENSUS > self.CONSENSUS_INTERVAL:
            self.LAST_CONSENSUS = current_time
            self.peer.build_chain()
            return True
        else:
            return False
    def execute(self):
        self.peer.build_chain()
       
    
       