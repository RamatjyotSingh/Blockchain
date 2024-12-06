# blockchain.py
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

    def __init__(self, total_height):
        """
        Initializes the Blockchain.

        Args:
            total_height (int): The total number of blocks the blockchain can hold.
        """
        self.chain = []
        self.total_height = total_height
        self.init_chain()
        self.curr_height = 0

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

    
    def add_block(self, block, height):
        """
        Adds a block to the blockchain at the specified height after verification.

        Args:
            block (Block): The block to add.
            height (int): The height at which to add the block.

        Returns:
            bool: True if the block was added successfully, False otherwise.
        """
        if self.verify_block(block, height):
            self.chain[height] = block
            ic(f"Block added at height {height}.")
            return True
        else:
            ic(f"Block verification failed at height {height}.")
            return False

    def verify_block(self, block, height):
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
            if not prev_block:
                ic(f"No previous block found for height {height}.")
                return False
            if block.previous_hash != prev_block.hash:
                ic(f"Hash mismatch at height {height}: {block.previous_hash} != {prev_block.hash}")
                return False
        # Verify the block's own integrity (e.g., proof-of-work, hash validity)
        is_valid = block.verify_self()
        if not is_valid:
            ic(f"Block at height {height} failed self-verification.")
        return is_valid

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
            ic(f"Height {height} is out of bounds.")
            return None

    def get_curr_height(self):
        """
        Retrieves the current height of the blockchain.

        Returns:
            int: The current height.
        """
        return self.curr_height

    def is_chain_filled(self):
        """
        Checks if the entire blockchain is filled without any missing blocks.

        Returns:
            bool: True if the chain is fully filled, False otherwise.
        """
        for index, block in enumerate(self.chain):
            if block is None:
                if index == 0:
                    ic("Genesis block is missing.")
                else:
                    previous_block = self.chain[index - 1]
                    ic(f"Missing block at height {index}. Previous block hash: {previous_block.hash if previous_block else 'None'}")
                return False
        self.curr_height = self.total_height
        return True

    def is_chunk_filled(self, chunk_size):
        """
        Checks if a chunk of blocks starting from the current height is filled.

        Args:
            chunk_size (int): The number of blocks to check.

        Returns:
            bool: True if the chunk is fully filled, False otherwise.
        """
        height = self.get_curr_height()
        end_height = height + chunk_size
        end_height = min(end_height, self.total_height)  # Prevent overflow

        for i in range(height, end_height):
            if  self.chain[i] is None:
                return False
      

        return True

    def increment_height_by_chunk(self, chunk_size):
        """
        Increments the current height by a specified chunk size if the chunk is filled.

        Args:
            chunk_size (int): The number of blocks to increment.
        """
        if self.is_chunk_filled(chunk_size) and self.curr_height <= self.total_height - chunk_size:
            self.curr_height += chunk_size
            with open('blockchain_data.txt', 'a') as f:
                f.write('curr_height: ' + str(self.curr_height) + '\n')
            assert self.curr_height <= self.total_height, "Height exceeds total height."
            ic(f"Current height incremented by {chunk_size} to {self.curr_height}.")
        else:
            ic(f"Cannot increment height by {chunk_size}. Either chunk is not filled or exceeds total height.")

    def create_block(self, hash, height, messages, minedBy, nonce, timestamp):
        """
        Creates a new block if the position is available.

        Args:
            hash (str): The hash of the block.
            height (int): The height at which to place the block.
            messages (list): The list of messages or transactions.
            minedBy (str): Identifier of the miner.
            nonce (str): The nonce used in mining.
            timestamp (int): The timestamp of block creation.

        Returns:
            Block or None: The created block if successful, else None.
        """
        if height >= self.total_height:
            ic(f"Cannot create block at height {height}: exceeds total height.")
            return None

        if self.chain[height] is not None:
            ic(f"Block already exists at height {height}.")
            return None

        if height == 0:
            prev_hash = None
        else:
            prev_block = self.chain[height - 1]

            if not prev_block:
                ic(f"Cannot create block at height {height} because previous block at height {height - 1} is missing.")
                return None
            
            prev_hash = prev_block.hash

        block = Block(minedBy, messages, height, prev_hash, hash, nonce, timestamp)

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
            if not self.verify_block(self.chain[i], i):
                ic(f"Invalid block detected at height {i}.")
                return False
        return True

   