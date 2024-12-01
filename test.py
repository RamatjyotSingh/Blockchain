import json
from gossip import Gossip
from stats import Stats
from icecream import ic
import socket




def test_gossip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        port = 8784
        sock.bind((ip, port))
        gossip = Gossip(sock, ip, port, "Ramatjyot Singh")
        peers, misc=gossip.execute()
        ic(peers)
        return peers

peers = test_gossip()

def test_stats():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        port = 8784
        sock.bind((ip, port))
        stats = Stats(sock,peers)
        priority_peers,misc = stats.execute()
        ic(priority_peers)



test_stats()

# def new_stat_test():
#     req = {
#         'type': 'STATS'
#     }
#     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#         silicon = ('silicon.cs.umanitoba.ca', 8999)
#         s.sendto(json.dumps(req).encode(), silicon)
#         data, addr = s.recvfrom(1024)
#         print(data.decode())