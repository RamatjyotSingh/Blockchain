import json
import random
import socket

from icecream import ic


class GetBlock:

    CHUNK_SIZE = 50


    def __init__(self,socket, blockchain,peers):
        self.blockchain = blockchain
        self.socket = socket
        self.peers = peers
        self.block_replies = {}

    def create_req(self,height):

        return{
            "type":"GET_BLOCK",
            "height":height
        }
    
    def create_res(self,height):

        block = self.blockchain.get_block_by_height(height)

        if block is None:
            return {
                "type": "GET_BLOCK_REPLY",
                "hash": None,
                "height": None,
                "messages": None,
                "mined_by": None,
                "nonce": None,
                "timestamp": None
            }
        return {
            "type": "GET_BLOCK_REPLY",
            "hash": block.hash,
            "height": block.height,
            "messages": block.messages,
            "mined_by": block.name,
            "nonce": block.nonce,
            "timestamp": block.timestamp
        }
    
    def send_req(self,peer,height):

        
            host = peer['host']
            port = peer['port']
            req = self.create_req(height)
            self.socket.sendto(json.dumps(req).encode(), (host, port))

    def recv_res(self,max_msges=100):

        self.block_replies 
       
        try:
                data, addr = self.socket.recvfrom(1024)
                ic(data,addr)
                reply = json.loads(data)

                if reply['type'] == 'GET_BLOCK_REPLY':
                    height = reply['height']

                    self.block_replies[height] = (reply)


            
            
        except json.JSONDecodeError:
                print("Received invalid JSON data.")
        except Exception as e:
                print(f"An error occurred: {e}")
            


        return self.block_replies

    def get_block(self,height,peers):

        curr_peer = peers[random.randint(0, len(peers) - 1)]
        ic(curr_peer)
        self.send_req(curr_peer,height)
        block_replies = self.recv_res()
        
        reply = block_replies[height]
        ic(reply)

        assert reply['type'] == 'GET_BLOCK_REPLY'
        assert height == reply['height'], f"Expected block at height {height}, got block at height {reply['height']}."

            

        block = self.blockchain.create_block(

                hash=reply['hash'],
                height=reply['height'],
                messages=reply['messages'],
                minedBy=reply['minedBy'],
                nonce=reply['nonce'],
                timestamp=reply['timestamp']

            )
        if block is None:
            return None
            # verify block should be in create_block()

        self.blockchain.add_block(block,height)
            # verify new link  should be in add_block()

        return block
    
    def get_blocks_in_chunks(self, peers, chunk_size):

        start_height = self.blockchain.get_curr_height() 
        ic(start_height)
        end_height = start_height + chunk_size

        for height in range(start_height, end_height):
            
            if height >= self.blockchain.total_height:
                height=0

            block = self.get_block(height, peers)
            
            if block:
                ic(block)
                continue  

            else:

                print(f"Failed to retrieve block at height {height}.")

    def execute(self):

        peers = self.peers

        chain_height = self.blockchain.total_height
        curr_height = self.blockchain.get_curr_height()
        chain_filled = self.blockchain.is_chain_filled()

        while curr_height < chain_height or not chain_filled:
           
            self.get_blocks_in_chunks(peers, self.CHUNK_SIZE)
            
            chain_filled = self.blockchain.is_chain_filled()
            if chain_filled:
                break
           