import traceback
from icecream import ic
from request_handler import RequestHandler
class Peer:
   
    def __init__(self,protocol):
      self.protocol = protocol
      self.protocol.init_consensus(self)
      
    
    def do_gossip(self):

        self.protocol.init_gossip()
        known_peers = self.protocol.gossip.execute()
        return known_peers
    
    def get_stats(self,known_peers):
        self.protocol.init_stats(known_peers)
        priority_peer_groups = self.protocol.stats.execute()
        return priority_peer_groups
    
    def fetch_blocks(self,priority_peer_groups):

        for height, priority_peers in priority_peer_groups.items():
            ic(f"Processing height: {height}")
               

            try:  

                
                self.protocol.init_blockchain(height)
                self.protocol.init_get_block(priority_peers)
                self.protocol.get_block.execute()

          
            
                if self.protocol.blockchain.is_valid():
                    blockchain = self.protocol.blockchain
                    
                    ic(f"Validated blockchain at height {blockchain.curr_height}")

                    return True
                
                else:
                    ic("Invalid blockchain.")
                    continue
            except Exception as e:
                ic(f"Error: {e}")
                ic(traceback.format_exc())
                continue


        return False
        
    def build_chain(self):
        known_peers = self.do_gossip()
        priority_peer_groups = self.get_stats(known_peers)
        return self.fetch_blocks(priority_peer_groups)
    
    def do_background_tasks(self):
        self.protocol.gossip.do_background_tasks()
        self.protocol.consensus.do_consensus()

    def do_announce(self,block,peers):

        self.protocol.announce_block(block,peers)

        
