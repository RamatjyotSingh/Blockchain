from datetime import datetime
import hashlib
import time
import multiprocessing
from multiprocessing import Process, Queue, Event

DIFFICULTY = 8  # Adjusted for testing

def worker(name, messages, height, previous_hash, timestamp, difficulty, step, start_nonce, result_queue, stop_event):
    """
    Worker function to find a valid nonce.
    
    Parameters:
        name (str): Name associated with the block.
        messages (list): List of messages in the block.
        height (int): Height of the block in the blockchain.
        previous_hash (str): Hash of the previous block.
        timestamp (int): Timestamp of the block creation.
        difficulty (int): Difficulty level (number of trailing zeros required).
        step (int): Step size for nonce iteration (number of workers).
        start_nonce (int): Starting nonce for this worker.
        result_queue (Queue): Queue to send back the result.
        stop_event (Event): Event to signal workers to stop searching.
    """
    nonce = start_nonce
    while not stop_event.is_set():
        # Compute hash for the current nonce
        hash_result = compute_hash(name, messages, height, previous_hash, timestamp, nonce)
        
        # Check if the hash satisfies the difficulty requirement
        if hash_result.endswith('0' * difficulty):
            # Put the valid nonce and hash into the result queue
            result_queue.put((nonce, hash_result))
            # Signal other workers to stop
            stop_event.set()
            break
        
        # Increment nonce by the number of workers to avoid overlap
        nonce += step

def compute_hash(name, messages, height, previous_hash, timestamp, nonce):
    """
    Computes the SHA-256 hash of the block's contents.
    
    Parameters:
        name (str): Name associated with the block.
        messages (list): List of messages in the block.
        height (int): Height of the block in the blockchain.
        previous_hash (str): Hash of the previous block.
        timestamp (int): Timestamp of the block creation.
        nonce (int): Nonce value for Proof-of-Work.
    
    Returns:
        str: The hexadecimal hash of the block.
    """
    hash_base = hashlib.sha256()

    if previous_hash:
        hash_base.update(previous_hash.encode('utf-8'))

    hash_base.update(name.encode('utf-8'))

    for message in messages:
        hash_base.update(message.encode('utf-8'))

    # Convert timestamp and nonce to bytes and update the hash
    hash_base.update(timestamp.to_bytes(8, 'big'))
    hash_base.update(nonce.to_bytes(8, 'big'))

    return hash_base.hexdigest()

class Block:
    """
    Represents a single block in the blockchain.
    """

    def __init__(self, name, messages, height, previous_hash,block_hash=None,nonce=None,timestamp=None):
        self.name = name
        self.messages = messages
        self.height = height
        self.previous_hash = previous_hash
        
        if block_hash:
            self.hash = block_hash
            self.nonce = nonce
            self.timestamp = timestamp
        else:
            self.nonce = 0

            self.timestamp = int(time.time())  # Initialize timestamp as integer
            self.hash = self.find_valid_hash()
     
        # Verify constraints
        self.verify_nonce()
        self.verify_messages()
        self.verify_self()

    def compute_hash(self, nonce):
        """
        Computes the SHA-256 hash of the block's contents with a given nonce.
        
        Parameters:
            nonce (int): The nonce value for Proof-of-Work.
        
        Returns:
            str: The hexadecimal hash of the block.
        """
        return compute_hash(self.name, self.messages, self.height, self.previous_hash, self.timestamp, nonce)

    def verify_hash(self):
        """
        Recomputes the hash of the block to verify its integrity.
        
        Returns:
            bool: True if the recomputed hash matches the stored hash and satisfies difficulty, else False.
        """
        return self.compute_hash(self.nonce) == self.hash and self.hash.endswith('0' * DIFFICULTY)

    def find_valid_hash(self):
        """
        Finds a valid hash by searching for a nonce that satisfies the difficulty requirement using multiprocessing.
        
        Returns:
            str: The valid hash.
        """
        num_workers = max(multiprocessing.cpu_count() - 3,3)  # Number of worker processes
        result_queue = Queue()
        stop_event = Event()
        processes = []

        print(f"Starting mining with {num_workers} workers...")

        # Start worker processes
        for i in range(num_workers):
            p = Process(target=worker, args=(
                self.name,
                self.messages,
                self.height,
                self.previous_hash,
                self.timestamp,
                DIFFICULTY,
                num_workers,
                i,
                result_queue,
                stop_event
            ))
            p.start()
            processes.append(p)
            print(f"Worker {i} started.")

        # Wait for a result from any worker
        nonce, hash_result = result_queue.get()  # This will block until a worker puts a result

        # Set the nonce and hash
        self.nonce = nonce
        self.hash = hash_result

        # Ensure all workers are signaled to stop
        stop_event.set()

        # Terminate all worker processes
        for p in processes:
            p.terminate()
            p.join()
            print(f"Worker {p.pid} terminated.")

        end_time = time.time()
        readable_time = datetime.fromtimestamp(end_time).strftime('%H:%M:%S')

        print(f"Valid hash found: Nonce = {nonce}, Hash = {hash_result}")
        print(f"Time taken to mine block: {end_time - self.timestamp:.2f}s")
        print(f"Current Time: {readable_time}")
        print(f"Block timestamp: {self.timestamp}")

        return hash_result 

    def verify_self(self):
        """
        Verifies the block's integrity by checking its hash and other constraints.
        
        Raises:
            AssertionError: If any verification fails.
        
        Returns:
            bool: True if all verifications pass.
        """
        assert self.verify_hash(), "Block hash verification failed. " + self.hash
        assert self.height >= 0, "Height must be non-negative."
        assert self.name != '', "Name cannot be empty."
        assert self.previous_hash != '' or self.height == 0, "Previous hash cannot be empty unless height is 0."
        return True

    def verify_nonce(self):
        """
        Verifies the nonce value to ensure it's valid.
        
        Raises:
            AssertionError: If nonce is invalid.
        
        Returns:
            bool: True if nonce is valid.
        """
        assert len(str(self.nonce)) < 40, "Nonce must be less than 40 characters."
        return True

    def verify_messages(self):
        """
        Verifies that the block's messages meet the predefined constraints.
        
        Raises:
            AssertionError: If any message constraint is violated.
        
        Returns:
            bool: True if all messages are valid.
        """
        assert len(self.messages) <= 10, "A block can have at most 10 messages."
        for message in self.messages:
            assert len(message) <= 20, "Each message must be at most 20 characters long."
        return True

    def __repr__(self):
        return f"Block(Name: {self.name}, Messages: {self.messages}, Height: {self.height}, Previous Hash: {self.previous_hash}, Hash: {self.hash}, Nonce: {self.nonce}, Timestamp: {self.timestamp})"

   
# Example usage
if __name__ == "__main__":
    with open("blocks.txt", "w") as f:
        previous_hash = "0189845a1f74eb9883e07e479cd77d8c33fa50bdebd05a2dc1a0d28200000000"
        for i in range(5):
            print(f"Creating block {i}...")
            try:
                block = Block(
                    name="Ramatjyot Singh",
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