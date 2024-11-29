from gossip import Gossip
import socket

def test_gossip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    port = 8784
    sock.bind((ip, port))
    gossip = Gossip(sock, ip, port, "Ramatjyot Singh")
    reply=gossip.execute()
    print(reply)

test_gossip()