import json
from icecream import ic
class RequestHandler:
    
    def __init__(self,sock,gossip,stats,get_block,announce,consensus,blockchain):
        self.sock = sock
        self.gossip = gossip
        self.stats = stats
        self.get_block = get_block
        self.announce = announce
        self.conensus = consensus
        self.blockchain = blockchain
        

    def handle(self):
        try:
            req,peer = self.sock.recvfrom(4096)
            if not req.strip():
                raise ValueError("Received empty request")
            data = json.loads(req)
           
        
            req_type = data['type']
            if req_type in ['GOSSIP', 'GOSSIP_REPLY']:
                self.gossip.handle_gossip(data)
            elif req_type == 'STATS':
                self.stats.send_res(self.blockchain, peer)
            elif req_type == 'GET_BLOCK':
                height = data['height']
                self.get_block.send_res(peer,height)
            elif req_type == 'ANNOUNCE':
            
                added=self.announce.handle_announcement(data, self.blockchain)
                if added:
                    ic(f"Block added at height {data['height']}.")

            elif req_type == 'CONSENSUS':
                ic(f"Received CONSENSUS from {peer[0]}:{peer[1]}")
                self.conensus.execute()
            elif req_type == 'NEW_WORD':
                word = data['word']
                return word

            else:
                ic(f"Unknown request type: {req_type}")
                return None
        
        
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None
        except ValueError as e:
            print(f"Error: {e}")
            return None