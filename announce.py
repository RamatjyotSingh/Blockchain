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
            req = self.create_req(self.block)
            for peer in self.peers:  # Iterate over the values of the dictionary
                host,port = peer['host'],peer['port']
                ic('-'*50)
                ic(f"Sending ANNOUNCE to {host}:{port}")
                ic('-'*50)
                self.sock.sendto(json.dumps(req).encode(), (host, port))


        
    

    def create_req(block):
        return {
            'type': 'ANNOUNCE',
            "height":block['height'],
            "minedBy": block['minedBy'],
            "nonce": block['nonce'],
            "messages": block['messages'],
            "hash": block['hash'],
            "timestamp": block['timestamp']
        }
    def handle_announcement(self,data,blockchain):
        
        blockchain.add_block_from_reply(data)
        
    