import json
import socket
from block import Block
from gossip import Gossip
class Announce:
    def create_req(block):
        return {
            'type': 'ANNOUNCE',
            "height":block.height,
            "minedBy": block.name,
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
        gossip = Gossip(socket=sock, port=port,host=ip, name="Ramatjyot Singh")
        gossip.execute()
        prev_hash = '9588d90863aff6af0bbd3e0cdf800a0edafd16fd0512e65d00c62a5000000000'
        if __name__ == "__main__":
            with open("blocks.txt", "w") as f:
                for i in range(5):
                    print(f"Creating block {i}...")
                    try:
                        block = Block("Ramatjyot Singh", ["Hello, Bob!"], 2211+i, "prev_hash")
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
