# blockchain.py
import traceback
from icecream import ic
from block import Block
import time
import logging

logging.basicConfig(
    filename='Blockchain.log',                  # Log file name
    filemode='a',                           # Append mode
    level=logging.INFO,                     # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'             # Date format
)

class Blockchain:


    def __init__(self, total_height, DIFFICULTY):
        """
        Initializes the Blockchain.

        Args:
            total_height (int): The total number of blocks the blockchain can hold.
        """
        self.chain = []
        self.total_height = total_height
        self.init_chain()
        self.curr_height = 0
        Block.DIFFICULTY = DIFFICULTY

    def init_chain(self):
        """
        Initializes the blockchain with a genesis block followed by empty slots.

        Args:
            total_height (int): The total number of blocks the blockchain can hold.
        """
        # Create and add the genesis block

        # Initialize the rest of the chain with None
        for i in range(0, self.total_height):
            
            self.chain.append(None)

    
    def add_block_from_reply(self, reply):
        """
        Adds a block to the blockchain at the specified height after verification.

        Args:
            reply (dict): The reply received from a peer.

        Returns:
            bool: True if the block was added successfully, False otherwise.
        """
        height = reply['height']

        if height == self.total_height:
            self.chain.append(None)

        block = self.create_block(reply)

        if block is None:
            return False
        
        assert height == block.height

        link = self.verify_integrity(block,height)
        
        if not link:
            # print(f"Block verification failed at height {height}.")
            return False
        
       

        if height == self.total_height: # Append to the end of the chain

                self.total_height += 1
                self.curr_height += 1
                self.chain.append(block)
                # print(f"Block added at height {height}.")


                return True
        
        elif height < self.total_height: # Insert at the specified height
            
            self.chain[height] = block
            # print(f"Block added at height {height}.")
            return True
       

    
    
    def get_last_valid_block(self):
        """
        Retrieves the last non-None block from the blockchain.

        Args:
            blockchain (Blockchain): The blockchain instance.

        Returns:
            Block or None: The last valid block if exists, otherwise None.
        """
        for block in reversed(self.chain):
            if block is not None:
                return block
        return None

    def verify_integrity(self, block,height):
        """
        Verifies the integrity of a block.

        Args:
            block (Block): The block to verify.
            height (int): The height at which the block is to be added.

        Returns:
            bool: True if the block is valid, False otherwise.
        """
        if height > 0:
            prev_block = self.get_block_by_height(height - 1)
            if  prev_block is None:
                print(f"No previous block found for height {height}.")
                return False
            if block.previous_hash != prev_block.hash:
                print(f"Hash mismatch at height {height}: {block.previous_hash} != {prev_block.hash}")
                return False
        # Verify the block's own integrity (e.g., proof-of-work, hash validity)
       
        return True

    def get_block_by_height(self, height):
        """
        Retrieves a block from the blockchain by its height.

        Args:
            height (int): The height of the block to retrieve.

        Returns:
            Block or None: The block if found, else None.
        """
        if 0 <= height < len(self.chain):
            return self.chain[height]
        else:
            print(f"Height {height} is out of bounds.")
            return None

   
    def is_chain_filled(self):
        """
        Checks if the entire blockchain is filled without any missing blocks.

        Returns:
            bool: True if the chain is fully filled, False otherwise.
        """
        for index, block in enumerate(self.chain):
            if block is None:
                if index == 0:
                    print("Genesis block is missing.")
                else:
                    previous_block = self.chain[index - 1]
                    print(f"Missing block at height {index}. Previous block hash: {previous_block.hash if previous_block else 'None'}")
                return False
        self.curr_height = self.total_height
        return True

    
    def create_block(self,reply):
        """
        Creates a new block if the position is available.

        Args:
           reply (dict): The reply received from a peer.

        Returns:
            Block or None: The created block if successful, else None.
        """
        try:

            height = reply['height']
            minedBy = reply['minedBy']
            messages = reply['messages']
            hash = reply['hash']
            nonce = reply['nonce']
            timestamp = reply['timestamp']

        except KeyError:
            print("Invalid block data received.")
            return None


        if self.chain[height] is not None:
            print(f"Block already exists at height {height}.")
            return None

        if height == 0:
            prev_hash = None
        else:
            prev_block = self.chain[height - 1]

            if not prev_block:
                print(f"Cannot create block at height {height} because previous block at height {height - 1} is missing.")
                return None
            
            prev_hash = prev_block.hash

        block = Block(minedBy, messages, height, prev_hash, hash, nonce, timestamp) #Block is implicitly verified when created

        return block

    def get_chain(self):
        """
        Retrieves the entire blockchain.

        Returns:
            list: The list of blocks in the blockchain.
        """
        return self.chain

    def is_valid(self):
        """
        Verifies the integrity of the entire blockchain.

        Returns:
            bool: True if the blockchain is valid, False otherwise.
        """
        for i in range(1, len(self.chain)):
            if not self.verify_integrity(self.chain[i], i):
                print(f"Invalid block detected at height {i}.")
                return False
        return True

   