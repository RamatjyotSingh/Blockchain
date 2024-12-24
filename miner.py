import hashlib
import socket
import argparse
import time
import json
import traceback
from icecream import ic

class Miner:
    def __init__(self, previous_hash, minedBy, messages, difficulty, height):
        self.height = height
        self.messages = messages
        self.previous_hash = str(previous_hash)
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

    def mine_block(self):
        hashbase = self.get_static_hash()
        nonce = 0

        while True:
            current_hash = hashbase.copy()
            current_hash.update(str(nonce).encode('utf-8'))
            hash_hex = current_hash.hexdigest()
            if hash_hex.endswith('0' * self.DIFFICULTY):
                self.nonce = nonce
                return hash_hex
            nonce += 1

    def report_block(self, block, sock, master):
        """
        Sends the mined block to a peer using TCP.
        """
        try:
            block_data = json.dumps(block).encode('utf-8')
            sock.sendall(block_data)
            print(f'Sent block to {master}')
        except Exception as e:
            print(f"Failed to report block to {master}: {e}")

# Command-line interface
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Miner Program")
    parser.add_argument("--peer_host", type=str, required=True, help="Peer host (IP address)")
    parser.add_argument("--peer_port", type=int, required=True, help="Peer port")
    args = parser.parse_args()

    MASTER = (args.peer_host, args.peer_port)
    MINING_HEIGHT = None
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(MASTER)
        print(f"Connected to {MASTER}")
        while True:
            try:
                    data = sock.recv(4096)
                    

                    if not data:
                        continue
          
            
                    data = json.loads(data.decode('utf-8'))
                  
                    messages = data['messages']
                    height = data['height']
                    previous_hash = data['previous_hash']
                    difficulty = data['difficulty']
                    minedBy = data['minedBy']
                  

                    if MINING_HEIGHT != height:
                        
                        miner = Miner(previous_hash, minedBy, messages, difficulty, height)
                        MINING_HEIGHT = height
                        mined_hash = miner.mine_block()

                        block = {
                            'height': height,
                            'messages': messages,
                            'previous_hash': previous_hash,
                            'minedBy': miner.minedBy,
                            'timestamp': miner.timestamp,
                            'nonce': miner.nonce,
                            'hash': mined_hash
                        }
                        print(block)
                        miner.report_block(block, sock, MASTER)

                        print(f"Block mined: {block}")
                        print(f"Block sent to {args.peer_host}:{args.peer_port}")
            except json.JSONDecodeError:
                print("Error: Invalid data received")
                continue
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
                continue
