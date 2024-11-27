from datetime import datetime
import hashlib
import os
import time
from multiprocessing import Pool, cpu_count,current_process

DIFFICULTY = 8 # Reduce difficulty for testing
NUM_WORKERS = max(3, cpu_count() - 3)

def compute_hash(args):
    block_data, nonce = args
    name, messages,  previous_hash = block_data

    hashBase = hashlib.sha256()

    if previous_hash:

        hashBase.update(previous_hash.encode())

    hashBase.update(name.encode())

    for message in messages:

        hashBase.update(message.encode())
    timestamp = time.time()
    hashBase.update(int(timestamp).to_bytes(8, 'big'))

    hashBase.update(str(nonce).encode())

    block_hash = hashBase.hexdigest()

    return block_hash, nonce , timestamp


class Block:

    def __init__(self, name, messages, height, previous_hash):
        self.name = name
        self.messages = messages
        self.nonce = 0
        self.height = height
        self.previous_hash = previous_hash
        self.block_hash = self.find_valid_hash()
     
       

        # Verify constraints
        self.verify_nonce()
        self.verify_messages()
        self.verify_self()

    def verify_hash(self):
        hashBase = hashlib.sha256()
      

        if self.previous_hash:

            hashBase.update(self.previous_hash.encode())

        hashBase.update(self.name.encode())

        for message in self.messages:

            hashBase.update(message.encode())
        hashBase.update(int(self.timestamp).to_bytes(8, 'big'))

        hashBase.update(str(self.nonce).encode())

        block_hash = hashBase.hexdigest()

        return block_hash

    def find_valid_hash(self):
        nonce = 0
        block_data = (self.name, self.messages, self.previous_hash)
        start_time = time.time()

        with Pool(processes=NUM_WORKERS) as pool:

            while True:

                nonces = [nonce + i for i in range(NUM_WORKERS)]
                results = pool.map(compute_hash, [(block_data, n) for n in nonces])

                for block_hash, nonce,endtime in results:

                    if block_hash[-DIFFICULTY:] == '0' * DIFFICULTY:

                        self.timestamp = endtime
                        self.nonce = nonce

                        print(f"Valid hash found by process : Nonce = {nonce}, Hash = {block_hash}")
                        print(f"Time taken to mine block: {endtime - start_time:.2f}s")
                        print(current_process().pid)
                        print(f"Current Time: {datetime.fromtimestamp(endtime).strftime('%H:%M:%S')}")

                        return block_hash 
                    
                nonce += NUM_WORKERS
                

    def verify_self(self):
        assert self.block_hash == self.verify_hash() and self.block_hash[-DIFFICULTY:] == '0' * DIFFICULTY, "Block hash verification failed. " + self.block_hash
        assert self.height >= 0, "Height must be non-negative."
        assert self.name != '', "Name cannot be empty."
        assert self.previous_hash != '' or self.height == 0, "Previous hash cannot be empty unless height is 0."
        return True

    def verify_nonce(self):
        assert len(str(self.nonce)) < 40, "Nonce must be less than 40 characters."
        return True

    def verify_messages(self):
        assert len(self.messages) <= 10, "A block can have at most 10 messages."
        for message in self.messages:
            assert len(message) <= 20, "Each message must be at most 20 characters long."
        return True
    
    def __repr__(self):
        return f"Block({self.name}, {self.messages}, {self.height}, {self.previous_hash}, {self.block_hash}, {self.nonce}, {self.timestamp})"
        

    

# Example usage
with open("blocks.txt", "w") as f:
    for i in range(5):
        print(f"Creating block {i}...")
        try:
            block = Block("Ramatjyot Singh" , ["Hello, Bob!"], 0, "")
            print(block, file=f)
        except AssertionError as e:
            print(e)
            print("Block creation failed.")
        print("")
