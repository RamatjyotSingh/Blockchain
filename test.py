import json
import select
from gossip import Gossip
from stats import Stats
from blockchain import Blockchain
from block import Block
from get_block import GetBlock
from icecream import ic
import socket

PORT =8784

def test_gossip(sock,ip,port):

                gossip = Gossip(sock, ip, port, "Ramatjyot Singh")
                peers=gossip.execute()
                print(peers)
                return peers

def test_stats(peers):
                stats = Stats(sock,peers)
                priority_peers = stats.execute()
                print(priority_peers)
                return priority_peers


def test_get_blockchain_height(priority_peers):
                for peer_list in priority_peers:
                        for peer_host, peer_port in peer_list:
                                blockchain = Blockchain(priority_peers[peer_list][1])
                                ic('inner loop'+blockchain.height)

                       



with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        port = PORT
        try:
            sock.bind((ip, port))
            ic(f"Socket bound to {ip}:{port}")

        except Exception as e:
            ic(f"Failed to bind socket: {e}")
            exit(1)

        while True:
            ic("Waiting for readable sockets...")
            readables, _, _ = select.select([sock], [], [], 1)
            
            if not readables:
                ic("No readable sockets. Retrying...")
                continue  
            
            for readable_sock in readables:
                if readable_sock == sock:
                    ic("Socket is readable.")
                    try:
                        peers = test_gossip(sock,ip,port)  # Fetch peers via gossip
                        if peers:
                            priority_peers = test_stats(peers)  # Prioritize peers
                            
                        
                            test_get_blockchain_height(priority_peers)  # Process peers
                            ic("Handled prioritized peers.")
                            break
            
                    except Exception as e:
                        ic(f"Error handling  data: {e}")
            break

