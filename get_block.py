# get_block.py
import json
import random
import socket
import time
import traceback
import logging
from icecream import ic
logging.basicConfig(
    filename='get_block.log',                  # Log file name
    filemode='a',                           # Append mode
    level=logging.INFO,                     # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'             # Date format
)


class GetBlock:

   
     

    def __init__(self, sock, peers,blockchain, gossip, stats,chunk_size, retry_limit):
        """
        Initializes the GetBlock handler.

        Args:
            sock (socket.socket): The UDP socket for communication.
            blockchain (Blockchain): The blockchain instance.
            peers (list): List of peer dictionaries with 'host' and 'port'.
        """
        self.blockchain = blockchain
        self.socket = sock
        self.peers = peers
        self.block_replies = {}
        self.gossip = gossip
        self.stats = stats
        self.CHUNK_SIZE = chunk_size
        self.ROUND_ROBIN_INDEX = 0
        self.RETRY_LIMIT = retry_limit

    def inc_round_robin_index(self):
        self.ROUND_ROBIN_INDEX = (self.ROUND_ROBIN_INDEX + 1) % len(self.peers)

    def create_req(self, height):
        """
        Creates a GET_BLOCK request.

        Args:
            height (int): The height of the block to request.

        Returns:
            dict: The GET_BLOCK request message.
        """
        return {
            "type": "GET_BLOCK",
            "height": height
        }

    def create_res(self, height):
        """
        Creates a GET_BLOCK_REPLY response based on the requested height.

        Args:
            height (int): The height of the block to respond with.

        Returns:
            dict: The GET_BLOCK_REPLY message.
        """
        block = self.blockchain.get_block_by_height(height)

        if block is None:
            return {
                "type": "GET_BLOCK_REPLY",
                "hash": None,
                "height": None,
                "messages": None,
                "minedBy": None,  # Changed from 'mined_by' to 'minedBy'
                "nonce": None,
                "timestamp": None
            }
        return {
            "type": "GET_BLOCK_REPLY",
            "hash": block.hash,
            "height": block.height,
            "messages": block.messages,
            "minedBy": block.minedBy,  # Changed from 'mined_by' to 'minedBy'
            "nonce": block.nonce,
            "timestamp": block.timestamp
        }

    def send_req(self, peer, height):
        """
        Sends a GET_BLOCK request to a specified peer.

        Args:
            peer (dict): The peer dictionary with 'host' and 'port'.
            height (int): The height of the block to request.
        """
        host = peer['host']
        port = peer['port']
        req = self.create_req(height)
        try:
            self.socket.sendto(json.dumps(req).encode(), (host, port))
            # print(f"Sent GET_BLOCK request for height {height} to {host}:{port}")
        except Exception as e:
            logging.error(f"Failed to send request to {host}:{port} - {e}")

    def send_req_to_all(self, peers,start_height,chunk_height):
        """
        Sends GET_BLOCK requests to all peers for the blocks.

        Args:
            peers (list): List of peer dictionaries with 'host' and 'port'.
            total_height (int): The height of the blockcahin to request.
        """
        
        # print(peers)
        total_height = self.blockchain.total_height
        end_height = min(start_height + chunk_height,total_height)
        for height in range(start_height,end_height):
            if self.blockchain.get_block_by_height(height) is None:
                self.send_req(peers[self.ROUND_ROBIN_INDEX], height)
                self.inc_round_robin_index()

    def recv_res(self, max_messages=None):

        if max_messages is None:
            max_messages = self.CHUNK_SIZE * 3

        """
        Receives a GET_BLOCK_REPLY response.

        Args:
            max_messages (int): The maximum number of messages to receive.

        Returns:
            dict: The received block replies mapped by their heights.
        """

        self.block_replies = {}
        num_messages = 0

        try:

            while num_messages < max_messages:

                data, peer = self.socket.recvfrom(4096)
                num_messages += 1
                # if addr not in self.ACCEPTING_PEERS:
                #     continue
               
                reply = json.loads(data.decode('utf-8'))

                

                if reply.get('type') == 'GET_BLOCK_REPLY':
                    height = reply.get('height')
                    if height is None:
                        print("Received empty block reply.")
                        continue
                    self.block_replies[height] = reply
                    # print(f"Stored reply for height {height}.")
                    if len(self.block_replies) == self.blockchain.total_height or len(self.block_replies) == self.blockchain.curr_height + min(self.CHUNK_SIZE, self.blockchain.total_height - self.blockchain.curr_height):
                        print("Received all blocks.")
                        break
                       

                elif reply.get('type') == 'GOSSIP' or reply.get('type') == 'GOSSIP_REPLY':
                    self.gossip.handle_gossip(reply)
                elif reply.get('type') == 'STATS':
                    self.stats.send_res(self.blockchain,peer)
              
               
                        
        except (socket.timeout, TimeoutError):
            logging.error("Timed out waiting for GET_BLOCK_REPLY.")
        except json.JSONDecodeError as jsde :
            logging.error("Received invalid JSON data.")
            logging.error(jsde)
            traceback.print_exc()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            traceback.print_exc()

        return self.block_replies

    def is_chunk_filled(self):
        """
        Checks if a chunk of blocks starting from the current height is filled.

        Returns:
            bool: True if the chunk is fully filled, False otherwise.
        """
        height = self.blockchain.curr_height
        end_height = height + self.CHUNK_SIZE
        end_height = min(end_height, self.blockchain.total_height)  # Prevent overflow

        for i in range(height, end_height):
            if  self.blockchain.chain[i] is None:
                return False
      

        return True
    
    # def add_chunk_of_blocks(self, chunk_height):
    #     """
    #     Adds a chunk of blocks to the blockchain.

    #     Args:
    #         chunk_height (int): The chunks of blocks to add.
    #     """
    #     start_height = self.blockchain.curr_height
    #     end_height = min(start_height + chunk_height, self.blockchain.total_height)

    #     for height in range(start_height, end_height):
    #         block = self.blockchain.get_block_by_height(height)
    #         if block is None:
    #             print(f"Block at height {height} is missing.")
    #             return

    #         added = self.blockchain.add_block(block, height)
    #         if added:
    #             print(f"Added block at height {height}.")
    #         else:
    #             print(f"Failed to add block at height {height}.")

    def increment_height_by_chunk(self):
        """
        Increments the current height by a specified chunk size if the chunk is filled.

        """
        if self.is_chunk_filled() and self.blockchain.curr_height <= self.blockchain.total_height - self.CHUNK_SIZE:
            self.blockchain.curr_height += min(self.CHUNK_SIZE, self.blockchain.total_height - self.blockchain.curr_height)
            with open('blockchain_data.txt', 'a') as f:
                f.write('curr_height: ' + str(self.blockchain.curr_height) + '\n')
            assert self.blockchain.curr_height <= self.blockchain.total_height, "Height exceeds total height."
            print(f"Current height incremented by {self.blockchain.curr_height-self.CHUNK_SIZE} to {self.blockchain.curr_height}.")
        else:
            print(f"Cannot increment height by {self.CHUNK_SIZE}. Either chunk is not filled or exceeds total height.")

    

    def get_blocks_by_chunks(self, peers, chunk_height, retry=0, start_height=None):
        if start_height is None:
            start_height = self.blockchain.curr_height

        """
        Retrieves a block at a specific height from peers.

        Args:
            height (int): The height of the block to retrieve.
            peers (list): List of peer dictionaries.
        """
        
        if retry > self.RETRY_LIMIT:
            print("Retry limit reached.")
            return False
        if not peers:
            print("No peers available to request blocks.")
            return False

        self.send_req_to_all(peers,start_height,chunk_height)
        block_replies = self.recv_res()

        # Process all received replies in ascending order of height
        for h, reply in sorted(block_replies.items()):
            # print(f"Height: {h}, Reply: {reply}")
            self.blockchain.add_block_from_reply(reply)
        
        if self.is_chunk_filled():
            print("Chunk is filled.")
            self.increment_height_by_chunk()
            return True
           
        else:
            print("Chunk is not filled. Requesting missing blocks.")
            time.sleep(1)
            self.get_blocks_by_chunks(peers,chunk_height,retry+1)

    # def get_blocks_in_chunks(self, peers, chunk_size):
    #     """
    #     Retrieves blocks in specified chunks.

    #     Args:
    #         peers (list): List of peer dictionaries.
    #         chunk_size (int): Number of blocks to retrieve in one chunk.
    #     """
    #     start_height = self.blockchain.get_curr_height()
    #     if start_height >= self.blockchain.total_height:
    #         return
    #     print(f"Start Height: {start_height}")
    #     end_height = min(start_height + chunk_size, self.blockchain.total_height)

    #     for height in range(start_height, end_height):
    #         self.get_block(height, peers)

    #         if height >= self.blockchain.total_height:
    #             raise Exception("Height out of bounds")

    #         if not self.is_chunk_filled():
    #             self.req_missing_blocks(peers, chunk_size)
    #             break  # Exit to retry after filling missing blocks

    #     with open('blockchain_data.txt', 'a') as f:
    #         f.write(f'chunk_size: {chunk_size}\nstart_height: {start_height}\n')
    #     print(f"Chunk Size: {chunk_size}")
    #     print(f"Start Height: {start_height}")

    def req_missing_blocks(self, peers, start_height=None):
        """
        Requests any missing blocks within the specified chunk.

        Args:
            peers (list): List of peer dictionaries.
            start_height (int, optional): Starting height for requesting blocks.
        """
       
        for height in range(start_height, start_height + self.CHUNK_SIZE + 1):
            if self.blockchain.get_block_by_height(height) is None:
                print(f"Requesting block at height {height}.")
                for peer in peers:
                    self.send_req(peer, height)

        replies = self.recv_res(self.CHUNK_SIZE*3)

        for h, reply in replies.items():
            # print(f"Height: {h}, Reply: {reply}")
            self.blockchain.add_block_from_reply(reply)
        
        if self.is_chunk_filled():
            print("Chunk is filled.")
            self.increment_height_by_chunk()
            return True
        else:
            print("Chunk is not filled even after requesting missing blocks.")
            return False

    def execute(self):
        """
        Executes the block retrieval process until the blockchain is fully synchronized.
        """
        chain_filled = self.blockchain.is_chain_filled()
        
        while not chain_filled:
       
            chunk_filled = self.get_blocks_by_chunks(self.peers, self.CHUNK_SIZE)

            if not chunk_filled:
                print("Failed to retrieve blocks. Trying to request missing blocks.")
                #last desperate attempt to fill the chunk
                filled = self.req_missing_blocks(self.peers, self.blockchain.curr_height)
                if filled:
                    continue
                return False
            
            chain_filled = self.blockchain.is_chain_filled()
     
          
        if chain_filled:
                with open('blockreplies.txt', 'a') as f:
                    for height, reply in self.block_replies.items():
                        f.write(f"{height}: {json.dumps(reply)}\n")
                print("Blockchain is fully synchronized.")
                return True
        else:
            print("Failed to synchronize blockchain.")
            return False
        
    def send_res(self, peer,height):
        """
        Sends a GET_BLOCK_REPLY response to a specified peer.

        Args:
            peer (dict): The peer dictionary with 'host' and 'port'.
        """
    
        res = self.create_res(height)
        print(f"Sending GET_BLOCK_REPLY to {peer}")
        self.socket.sendto(json.dumps(res).encode(), peer)