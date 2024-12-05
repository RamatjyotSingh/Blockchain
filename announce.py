import json
import socket
from block import Block
from gossip import Gossip
class Announce:
    def create_req(block):
        return {
            'type': 'ANNOUNCE',
            "height":block.height,
            "minedBy": block.minedBy,
            "nonce": block.nonce,
            "messages": block.messages,
            "hash": block.hash,
            "timestamp": block.timestamp
        }
    res= {
            'type': 'ANNOUNCE',
            "height":2201,
            "minedBy": "Ramatjyot Singh",
            "nonce": 844240035,
            "messages": ["Hello, Bob!"],
            "hash": 'ab089d791df1d4c7204fed40f6f740b35f7d405c63da8beaa9a3e37900000000',
            "timestamp": 1733335772
        }
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        port = 8784
        sock.bind((ip, port))
        gossip = Gossip(sock, ip, port, "Ramatjyot Singh")
        gossip.first_gossip()
        prev_hash = '05370e4b187ccf0e5adc3447dc1887d2d13d658b26544fa80404b10100000000'
        if __name__ == "__main__":
            with open("blocks.txt", "w") as f:
                for i in range(5):
                    print(f"Creating block {i}...")
                    try:
                        block = Block("Ramatjyot Singh", ["Hello, Bob!"], 2245+i, "prev_hash")
                        print(block, file=f)
                        prev_hash = block.hash
                        create_req(block)
                        sock.sendto(json.dumps(res).encode(), ('silicon.cs.umanitoba.ca', 8999))
                        sock.sendto(json.dumps(res).encode(), ('130.179.28.113',1234))
                        sock.sendto(json.dumps(res).encode(), ('130.179.28.113',8999))
                        



                    except AssertionError as e:
                        print(e)
                        print("Block creation failed.")
                    print("")
