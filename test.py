import json
import select
from gossip import Gossip
from stats import Stats
from blockchain import Blockchain
from block import Block
from get_block import GetBlock
from icecream import ic
import socket

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        port = 8784
        sock.bind((ip, port))


        def test_gossip():
        
                gossip = Gossip(sock, ip, port, "Ramatjyot Singh")
                peers=gossip.execute()
                print(peers)
                return peers


        def test_stats(peers):
                stats = Stats(sock,peers)
                priority_peers = stats.execute()
                print(priority_peers)




        while True:
                readables, writables, _ = select.select([sock], [], [], 1)

                if sock in readables:
                        
                        peers = test_gossip()
                        test_stats(peers)

     