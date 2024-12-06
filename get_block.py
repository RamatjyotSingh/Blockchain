# get_block.py
import json
import random
import socket
import time
import traceback

from icecream import ic


class GetBlock:
    CHUNK_SIZE = 150
    RETRY_LIMIT = 3  # Maximum number of retries for requesting a block
    TIMEOUT = 5      # Socket timeout in seconds
    # ACCEPTING_PEERS = [
    #     ("130.179.28.113", 8999),
    #     ("130.179.28.117", 8999),
       
    # ]  # List of peers that are blocked

    def __init__(self, sock, blockchain, peers):
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
            ic(f"Sent GET_BLOCK request for height {height} to {host}:{port}")
        except Exception as e:
            ic(f"Failed to send request to {host}:{port} - {e}")

    def send_req_to_all(self, peers,start_height,chunk_height):
        """
        Sends GET_BLOCK requests to all peers for the blocks.

        Args:
            peers (list): List of peer dictionaries with 'host' and 'port'.
            total_height (int): The height of the blockcahin to request.
        """
        
        ic(peers)
        for height in range(start_height,start_height+chunk_height):
            self.send_req(peers[ROUND_ROBIN_INDEX], height)

    def recv_res(self, waiting_time=300):
        """
        Receives a GET_BLOCK_REPLY response.

        Args:
            wanted_height (int, optional): The specific block height to wait for.

        Returns:
            dict: The received block replies mapped by their heights.
        """

        self.block_replies = {}
        self.socket.settimeout(self.TIMEOUT)
        start_time = time.time()
        curr_time = start_time
        try:
            while  curr_time - start_time < waiting_time:
                curr_time = time.time()
                data, addr = self.socket.recvfrom(4096)
                # if addr not in self.ACCEPTING_PEERS:
                #     continue

                reply = json.loads(data.decode('utf-8'))

                

                if reply.get('type') == 'GET_BLOCK_REPLY':
                    height = reply.get('height')
                    if height is not None:
                        self.block_replies[height] = reply
                        ic(f"Stored reply for height {height}.")
                        if len(self.block_replies) == self.blockchain.total_height:
                            ic("Received all blocks.")
                            break
                        # If the previous block is missing, request it
                        # if height > 0 and self.blockchain.get_block_by_height(height - 1) is None:
                        #     peer = {'host': addr[0], 'port': addr[1]}
                        #     self.send_req(peer, height - 1)
                        #     ic(f"Requesting block at height {height - 1} from {peer}")

                
                else:
                    continue
                        
        except (socket.timeout, TimeoutError):
            ic("Timed out waiting for GET_BLOCK_REPLY.")
        except json.JSONDecodeError:
            ic("Received invalid JSON data.")
        except Exception as e:
            ic(f"An error occurred: {e}")
            traceback.print_exc()

        return self.block_replies

    def add_block_from_reply(self, reply):
        """
        Adds a block to the blockchain based on the GET_BLOCK_REPLY.

        Args:
            reply (dict): The GET_BLOCK_REPLY message.
        """
        if reply['hash'] is None:
            ic(f"No block found at height {reply['height']}.")
            return

        block = self.blockchain.create_block(
            hash=reply['hash'],
            height=reply['height'],
            messages=reply['messages'],
            minedBy=reply['minedBy'],  # Ensure consistency
            nonce=reply['nonce'],
            timestamp=reply['timestamp']
        )

        if block:
            added = self.blockchain.add_block(block, reply['height'])
            if added:
                ic(f"Added block at height {reply['height']}.")
            else:
                ic(f"Failed to add block at height {reply['height']}.")
        else:
            ic("Block creation failed.")

    def get_blocks_by_chunks(self, peers, chunk_height, retry=0, start_height=None):
        if start_height is None:
            start_height = self.blockchain.get_curr_height()
        """
        Retrieves a block at a specific height from peers.

        Args:
            height (int): The height of the block to retrieve.
            peers (list): List of peer dictionaries.
        """
        
        if retry > self.RETRY_LIMIT:
            ic("Retry limit reached.")
            return
        if not peers:
            ic("No peers available to request blocks.")
            return

        self.send_req_to_all(peers,start_height,chunk_height)
        block_replies = self.recv_res()

        # Process all received replies in ascending order of height
        for h, reply in sorted(block_replies.items()):
            ic(f"Height: {h}, Reply: {reply}")
            self.add_block_from_reply(reply)
        
        if self.blockchain.is_chunk_filled(chunk_height):
            ic("Chunk is filled.")
            self.blockchain.increment_height_by_chunk(chunk_height)
        else:
            ic("Chunk is not filled. Requesting missing blocks.")
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
    #     ic(f"Start Height: {start_height}")
    #     end_height = min(start_height + chunk_size, self.blockchain.total_height)

    #     for height in range(start_height, end_height):
    #         self.get_block(height, peers)

    #         if height >= self.blockchain.total_height:
    #             raise Exception("Height out of bounds")

    #         if not self.blockchain.is_chunk_filled(chunk_size):
    #             self.req_missing_blocks(peers, chunk_size)
    #             break  # Exit to retry after filling missing blocks

    #     with open('blockchain_data.txt', 'a') as f:
    #         f.write(f'chunk_size: {chunk_size}\nstart_height: {start_height}\n')
    #     ic(f"Chunk Size: {chunk_size}")
    #     ic(f"Start Height: {start_height}")

    def req_missing_blocks(self, peers, start_height=None):
        """
        Requests any missing blocks within the specified chunk.

        Args:
            peers (list): List of peer dictionaries.
            chunk_size (int): Number of blocks to request.
            start_height (int, optional): Starting height for requesting blocks.
        """

        for height in range(start_height, start_height + self.CHUNK_SIZE + 1):
            if self.blockchain.get_block_by_height(height) is None:
                ic(f"Requesting block at height {height}.")
                for peer in peers:
                    self.send_req(peer, height)

        replies = self.recv_res(5)

        for h, reply in replies.items():
            ic(f"Height: {h}, Reply: {reply}")
            self.add_block_from_reply(reply)

    def execute(self):
        """
        Executes the block retrieval process until the blockchain is fully synchronized.
        """
        peers = self.peers
        chain_filled = self.blockchain.is_chain_filled()

        while not chain_filled:

            self.get_blocks_by_chunks(peers, self.CHUNK_SIZE)

            chain_filled = self.blockchain.is_chain_filled()

            if chain_filled:
                with open('blockreplies.txt', 'w') as f:
                    for height, reply in self.block_replies.items():
                        f.write(f"{height}: {json.dumps(reply)}\n")
                ic("Blockchain is fully synchronized.")
                break
            
            #failsafe
            if not self.blockchain.is_chunk_filled(self.CHUNK_SIZE):
                ic("Chunk is not fully synchronized. Requesting missing blocks.")
                self.req_missing_blocks(peers, start_height=self.blockchain.get_curr_height())
        
    def send_res(self, peer):
        """
        Sends a GET_BLOCK_REPLY response to a specified peer.

        Args:
            peer (dict): The peer dictionary with 'host' and 'port'.
        """
        height = self.blockchain.get_curr_height()
        res = self.create_res(height)
        host = peer['host']
        port = peer['port']
        ic(f"Sending GET_BLOCK_REPLY to {host}:{port}")
        self.socket.sendto(json.dumps(res).encode(), (host, port))