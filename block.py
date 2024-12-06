from datetime import datetime
import hashlib
import time
import logging
from icecream import ic

logging.basicConfig(
    filename='block.log',                  # Log file name
    filemode='a',                           # Append mode
    level=logging.INFO,                     # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'             # Date format
)

DIFFICULTY = 8  # Adjusted for testing


class Block:
    """
    Represents a single block in the blockchain.
    """

    def __init__(self, minedBy, messages, height, previous_hash, hash=None, nonce=None, timestamp=None):
        self.minedBy = minedBy
        self.messages = messages
        self.height = height
        self.previous_hash = previous_hash if height != 0 else None

        if hash:
            self.hash = hash
            self.nonce = str(nonce)
            self.timestamp = timestamp
        else:
            self.timestamp = int(time.time())
            self.nonce = 0
            self.hash = self.find_valid_hash()
            
        self.verify_self()  # Verify block integrity after mining

    def compute_hash(self, nonce):
        """
        Computes the SHA-256 hash of the block's contents with a given nonce.

        Parameters:
            nonce (int): The nonce value for Proof-of-Work.

        Returns:
            str: The hexadecimal hash of the block.
        """
        hash_base = hashlib.sha256()

        if self.previous_hash:
            hash_base.update(self.previous_hash.encode('utf-8'))

        hash_base.update(self.minedBy.encode('utf-8'))

        for message in self.messages:
            hash_base.update(message.encode('utf-8'))

        # Convert timestamp and nonce to bytes and update the hash
        hash_base.update(self.timestamp.to_bytes(8, 'big'))
        hash_base.update(str(nonce).encode('utf-8'))

        return hash_base.hexdigest()

    def find_valid_hash(self):
        """
        Finds a valid hash by iterating through nonce values until the difficulty requirement is met.

        Returns:
            str: The valid hash.
        """
        nonce = 0
        print(f"Starting mining for block at height {self.height}...")
        start_time = time.time()

        while True:
            hash_result = self.compute_hash(nonce)
            if hash_result.endswith('0' * DIFFICULTY):
                self.nonce = nonce
                end_time = time.time()
                print(f"Valid hash found: Nonce = {nonce}, Hash = {hash_result}")
                print(f"Time taken to mine block: {end_time - start_time:.2f}s")
                return hash_result
            nonce += 1

    def verify_self(self):
        """
        Verifies the block's integrity by checking its hash and other constraints.
    
        Raises:
            ValueError: If any verification fails.
    
        Returns:
            bool: True if all verifications pass.
        """
        valid = True  # Flag to track overall validity
    
        # Validate height
        if self.height < 0:
            logging.error("Height must be non-negative. Current height: %d", self.height)
            valid = False
    
        # Validate miner information
        if not self.minedBy:
            logging.error("minedBy cannot be empty.")
            valid = False
    
        # Validate previous hash
        if not self.previous_hash and self.height != 0:
            logging.error("Previous hash cannot be empty unless height is 0. Current height: %d", self.height)
            valid = False
    
        # Validate timestamp
        current_time = int(time.time())
        if self.timestamp > current_time:
            logging.error("Timestamp cannot be in the future. Block timestamp: %d, Current time: %d", self.timestamp, current_time)
            valid = False
    
        # Validate nonce length
        if len(str(self.nonce)) > 40:
            logging.error("Nonce must be at most 40 characters long. Current nonce length: %d", len(str(self.nonce)))
            valid = False
    
        # Validate number of messages
        if len(self.messages) > 10:
            logging.error("A block can have at most 10 messages. Current number of messages: %d", len(self.messages))
            valid = False

        if self.hash[-DIFFICULTY:] != '0' * DIFFICULTY:
            logging.error("Block hash does not meet difficulty requirement. Hash: '%s'", self.hash)
            valid = False
            
        # Validate each message length
        for idx, message in enumerate(self.messages, start=1):
            if len(message) > 20:
                logging.error("Message %d exceeds 20 characters. Message: '%s'", idx, message)
                valid = False
    
        if not valid:
            raise ValueError("Block verification failed. Check logs for details.")
    
        ic("Block verification passed for height %d.", self.height)
        return True

    def __repr__(self):
        return (
            f"Block(minedBy: {self.minedBy}, Messages: {self.messages}, Height: {self.height}, "
            f"Previous Hash: {self.previous_hash}, Hash: {self.hash}, Nonce: {self.nonce}, Timestamp: {self.timestamp})"
        )


# Example usage
if __name__ == "__main__":
    with open("blocks.txt", "w") as f:
        previous_hash = "0189845a1f74eb9883e07e479cd77d8c33fa50bdebd05a2dc1a0d28200000000"
        for i in range(5):
            print(f"Creating block {i}...")
            try:
                block = Block(
                    minedBy="Ramatjyot Singh",
                    messages=["Hello, Bob!"],
                    height=2189 + i,
                    previous_hash=previous_hash
                )
                print(block, file=f)
                previous_hash = block.hash  # Update for the next block
            except AssertionError as e:
                print(e)
                print("Block creation failed.")
            print("")
