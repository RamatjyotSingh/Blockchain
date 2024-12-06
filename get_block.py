import json
import random
import socket
import time
import traceback

from icecream import ic


class GetBlock:

    CHUNK_SIZE = 150


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

    def recv_res(self ,wanted_height=None):
        
        if wanted_height is not None:
             if self.temp_block_replies.get(wanted_height) is not None:
                  
        self.block_replies 
       
        try:
                data, addr = self.socket.recvfrom(1024)
                reply = json.loads(data)

                if reply['type'] == 'GET_BLOCK_REPLY':
                    height = reply['height']
                    if height is not None:
                        self.block_replies[height] = reply

                        ic(f"Stored reply for height {height}.")

                       

                        block = self.blockchain.create_block(

                        hash=reply['hash'],
                        height=reply['height'],
                        messages=reply['messages'],
                        minedBy=reply['minedBy'],
                        nonce=reply['nonce'],
                        timestamp=reply['timestamp']

                        )
                        if block is None:
                            self.temp_block_replies[height] = reply
                            return
                  
                            
                        # verify block should be in create_block()

                    self.blockchain.add_block(block,height)
                        # verify new link  should be in add_block()
                                
                        
        except (TimeoutError, socket.timeout):   
            print("Timed out waiting for replies.")     
        except json.JSONDecodeError:
            print("Received invalid JSON data.")
        except Exception as e:
                print(f"An error occurred: {e}")
                traceback.print_exc()
            


        return self.block_replies

    def get_block(self,height,peers):

        curr_peer = peers[random.randint(0, len(peers) - 1)]
        # ic(curr_peer)
        self.send_req(curr_peer,height)
        block_replies = self.recv_res(wanted_height=height)

        try:
            reply = block_replies[height]
            for key in sorted(block_replies.keys()):
                ic(key, type(block_replies[key]))
                        
            assert reply['type'] == 'GET_BLOCK_REPLY'
            assert height == reply['height'], f"Expected block at height {height}, got block at height {reply['height']}."

        except KeyError:
            ic(block_replies)


            print(f"Failed to retrieve block at height {height}.")
           
         
            return 
        except Exception as e:  
          
            ic(block_replies)

            ic("Traceback:")
            traceback.print_exc()  # This will print the full traceback
        
        

      
            

       

    
    def get_blocks_in_chunks(self, peers, chunk_size):

        start_height = self.blockchain.get_curr_height() 
        if start_height >= self.blockchain.total_height:
            return
        ic(start_height)
        end_height = min(start_height + chunk_size,self.blockchain.total_height)

        for height in range(start_height, end_height):

            self.get_block(height, peers)

            if height > self.blockchain.total_height :
                raise Exception("Height out of bounds")
            
            if not self.blockchain.is_chunk_filled(chunk_size):
                self.req_missing_blocks(peers,chunk_size)
        
        with open('blockchain_data.txt', 'a') as f:
            f.write('chunk_size: ' + str(chunk_size) + '\n' + 'start_height: ' + str(start_height) + '\n')
        ic(chunk_size)
        ic(start_height)

           


            
    def req_missing_blocks(self,peers,chunk_size,start_height=None):
                
                start_height = start_height or self.blockchain.get_curr_height()

                for height in range(start_height, start_height+chunk_size +1):
                    if self.blockchain.get_block_by_height(height) is None:
                        ic(f"Requesting block at height {height}.")
                       
                        self.get_block(height,peers)
                    
                         

    def execute(self):

        peers = self.peers

        chain_height = self.blockchain.total_height
        curr_height = self.blockchain.get_curr_height()
        chain_filled = self.blockchain.is_chain_filled()

        while  not chain_filled:
           
            self.get_blocks_in_chunks(peers, self.CHUNK_SIZE)
            self.blockchain.increment_height_by_chunk(self.CHUNK_SIZE)
            time.sleep(1)
            
            chain_filled = self.blockchain.is_chain_filled()

            if chain_filled:
                with open('blockreplies.txt', 'w') as f:
                    for block in self.block_replies:
                        f.write(block)

                break
            
            else:
                   self.req_missing_blocks(peers,self.CHUNK_SIZE,start_height=0)
           