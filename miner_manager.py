
import json
import select
import traceback
from icecream import ic

class MinerMaster:

    def __init__(self,protocol):
        self.miners = []
        self.protocol = protocol
        self.sock = [protocol.create_miner_socket()]
        
     
    def add_miner(self,miner):
        self.miners.append(miner)
    
    def feed_miners(self,data):
        for miner in self.miners:
            miner.sendall(json.dumps(data).encode())

    def transport_blocks(self,peers):
        readable, _, exceptional = select.select(self.miners + self.sock, [], self.miners + self.sock, 0)

        for s in readable:
            if s in self.sock:
                miner, addr = s.accept()
                self.add_miner(miner)
            else:
                data = s.recv(4096)
                print(data)
             
                
            
                try:
                            block = json.loads(data)
                            print(block)
                            if block:
                                self.protocol.announce_block(block,peers)

                except Exception as e:
                            print(f"Failed to parse message: {e}")
                            traceback.print_exc()
                            continue
                    
        for s in exceptional:
            self.miners.remove(s)
            s.close()

    def manage_miners(self,messages,peers):
        block = self.protocol.blockchain.get_last_valid_block()
        block_data = {

            "minedBy": self.protocol.name,
            "previous_hash": block.hash,
            "height": block.height + 1,
            "difficulty": self.protocol.DIFFICULTY,
        }
        if messages is not None:
            block_data["messages"] = [messages]
        else :
            block_data["messages"] = ["Helloo There!"]
        self.feed_miners(block_data)
        self.transport_blocks(peers)
                
