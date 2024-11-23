import hashlib
import os
import time
from multiprocessing import Pool, cpu_count,current_process

DIFFICULTY = 2 # Reduce difficulty for testing
NUM_WORKERS = max(3, cpu_count() - 3)

def compute_hash(args):

    block_data, nonce = args
    name, messages, height, previous_hash = block_data

    data = f"{name}{messages}{nonce}{height}{previous_hash}".encode('utf-8')
    block_hash = hashlib.sha256(data).hexdigest()

    return block_hash, nonce

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

    def calc_hash(self, nonce):
        data = f"{self.name}{self.messages}{nonce}{self.height}{self.previous_hash}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def find_valid_hash(self):
        nonce = 0
        block_data = (self.name, self.messages, self.height, self.previous_hash)
        start_time = time.time()
        with Pool(processes=NUM_WORKERS) as pool:
            while True:

                nonces = [nonce + i for i in range(NUM_WORKERS)]
                results = pool.map(compute_hash, [(block_data, n) for n in nonces])

                for block_hash, nonce in results:

                    if block_hash[-DIFFICULTY:] == '0' * DIFFICULTY:

                        print(f"Valid hash found by process : Nonce = {nonce}, Hash = {block_hash}")
                        print(f"Time taken to mine block: {time.time() - start_time:.2f}s")
                        print(current_process().pid)
                        print("Current Time: "+ time.time().strftime("%H:%M:%S"))
                        self.nonce = nonce
                        return block_hash
                    
                nonce += NUM_WORKERS
                

    def verify_self(self):
        assert self.block_hash == self.calc_hash(self.nonce) and self.block_hash[-DIFFICULTY:] == '0' * DIFFICULTY, "Block hash verification failed. " + self.block_hash
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

# Example usage
for i in range(5):
    print(f"Creating block {i}...")
    try:
        block = Block("Alice"+str(i), ["Hello, Bob!"], 0, "")
    except AssertionError as e:
        print(e)
        print("Block creation failed.")
    print("")
print(cpu_count())