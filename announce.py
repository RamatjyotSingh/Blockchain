import json
from icecream import ic
from block import Block
 
class Announce:

    def __init__(self,sock,block,peers):
        self.sock = sock
        self.block = block
        self.peers = peers
        self.broadcast()

    def broadcast(self):
        if self.block:
            req = self.create_req()
            for peer in self.peers:  # Iterate over the values of the dictionary
                host,port = peer['host'],peer['port']
                
                self.sock.sendto(json.dumps(req).encode(), (host, port))
                ic(f"Sending ANNOUNCE to {host}:{port}")



        
    

    def create_req(self):
        return {
            'type': 'ANNOUNCE',
            "height":self.block['height'],
            "minedBy": self.block['minedBy'],
            "nonce": self.block['nonce'],
            "messages": self.block['messages'],
            "hash": self.block['hash'],
            "timestamp": self.block['timestamp']
        }
    def handle_announcement(self,data,blockchain):
        
        blockchain.add_block_from_reply(data)
        
    