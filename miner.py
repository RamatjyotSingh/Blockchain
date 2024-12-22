import hashlib
import socket
import argparse
import time
import json
import multiprocessing
import sys

class Miner:
    
   

    def __init__(self, previous_hash, minedBy,messages,difficulty):
        self.height = height
        self.messages = messages
        self.previous_hash = previous_hash
        self.minedBy = minedBy
        self.timestamp = int(time.time())
        self.nonce = 0
        self.DIFFICULTY = difficulty

    def get_static_hash(self):
        hashbase = hashlib.sha256()
        hashbase.update(self.previous_hash.encode('utf-8'))
        hashbase.update(self.minedBy.encode('utf-8'))
        for message in self.messages:
            hashbase.update(message.encode('utf-8'))
        hashbase.update(self.timestamp.to_bytes(8, 'big'))
        return hashbase

    def mine_worker(self, nonce_start, step, event, result_queue):
        hashbase = self.get_static_hash()
        nonce = nonce_start

        while not event.is_set():
            current_hash = hashbase.copy()
            current_hash.update(str(nonce).encode('utf-8'))
            hash_hex = current_hash.hexdigest()
            if hash_hex.endswith('0' * self.DIFFICULTY):
                event.set()
                result_queue.put((nonce, hash_hex))
                break
            nonce += step

    def mine_block(self, num_processes=4):
        manager = multiprocessing.Manager()
        event = manager.Event()
        result_queue = manager.Queue()
        processes = []

        for i in range(num_processes):
            p = multiprocessing.Process(target=self.mine_worker, args=(i, num_processes, event, result_queue))
            processes.append(p)
            p.start()

        nonce, hash_hex = result_queue.get()
        event.set()

        for p in processes:
            p.join()

        self.nonce = nonce
        return hash_hex

    def report_Block(self, block,sock):
        """
        Sends the mined block to a peer using TCP.
        """
        try:
                block_data = json.dumps(block).encode('utf-8')
                sock.sendall(block_data)
                print(f'Sent block to {self.MASTER}')
        except Exception as e:
            print(f"Failed to report block to {self.MASTER}: {e}")

# Command-line interface
if __name__ == "__main__":
 

    parser = argparse.ArgumentParser(description="Miner Program")
    parser.add_argument("--peer_host", type=str, required=True, help="Peer host (IP address)")
    parser.add_argument("--peer_port", type=int, required=True, help="Peer port")
    parser.add_argument("--processes", type=int, default=4, help="Number of parallel mining processes")
    args = parser.parse_args()

    MASTER = (args.peer_host, args.peer_port)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(MASTER)
        print(f"Connected to {MASTER}")
        data = sock.recv(4096)
        data = json.loads(data.decode('utf-8'))
        print(f"Received data: {data}")
        messages = data['messages']
        height = data['height']
        previous_hash = data['previous_hash']
        difficulty = data['difficulty']
        miner = Miner(height, messages, previous_hash,difficulty)
        mined_hash = miner.mine_block(args.processes)

        block = {
            'height': height,
            'messages': messages,
            'previous_hash': previous_hash,
            'minedBy': miner.minedBy,
            'timestamp': miner.timestamp,
            'nonce': miner.nonce,
            'hash': mined_hash
        }
        miner.report_block(block,sock)
      
        print(f"Block mined: {block}")
        print(f"Block sent to {args.peer_host}:{args.peer_port}")
        print("Announcement sent to peer")
        print("Miner program completed.")