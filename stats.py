import json
import socket
from icecream import ic


class Stats:
    
    def __init__(self,socket,peers):
        self.socket = socket
        self.peers = peers
        
    
    
      
    def create_req(self):
        return {
            'type': 'STATS'

        } 
    def create_res(self,block):
        return {

            "type":"STATS_REPLY",
            "height":block.height,
            "hash":block.hash
            
             }
    
    def send_req(self):
        req = self.create_req()
        for peer in self.peers:  # Iterate over the values of the dictionary
            host = peer['host']
            port = peer['port']
            ic('-'*50)
            ic(f"Sending STATS to {host}:{port}")
            ic('-'*50)
            self.socket.sendto(json.dumps(req).encode(), (host, port))

    def recv_res(self,max_msges=100):

        socket.timeout(5)
        stats_replies = []
        msges = 0
        while msges < max_msges:
            try:
                data, addr = self.socket.recvfrom(1024)
                msges += 1
                reply = json.loads(data)
                reply_type = reply['type'] 
                ic(f"Received {reply_type} from {addr[0]}:{addr[1]}")
                if reply_type == 'STATS_REPLY':
                    ic(f"Received {reply_type} from {addr[0]}:{addr[1]}")

                    stats_replies.append((reply,addr))
                # elif reply['type'] == 'STATS':

                    # self.send_res(addr,blockchain)

           
            except (TimeoutError, socket.timeout):
                ic("Socket timed out, no more data received.")
                break

            except Exception  :
                ic('breaking out from loop')
                break

           

        return stats_replies
    
    def send_res(self,reply_type,addr,blockchain):

        if reply_type == 'STATS_REPLY' and self.blockchain.is_chain_filled():
            height = len(self.blockchain.chain)
            block = self.blockchain.chain[height-1]
            res = self.create_res(block,height)
            host = addr[0]
            port = addr[1]
            ic('-'*50)
            ic(f"Sending STATS_REPLY to {host}:{port}")
            ic('-'*50)
            self.socket.sendto(json.dumps(res).encode(), (host, port))
    
    def filter_stats(self, stats_replies):
        stats = {}
        for reply, addr in stats_replies:
            host, port = addr  # Extract host and port from addr
            ic(f"Received STATS_REPLY from {host}:{port}")
            stats[(host, port)] = {'height': reply['height'], 'hash': reply['hash']}
        return stats

    def find_priority_peers(self, stats):

        occurance = {}
        for peer, stat in stats.items():
            hash_value = stat['hash']
            height = stat['height']
            if hash_value in occurance:
                count, height, peers = occurance[hash_value]
                peers.append(peer)
                occurance[hash_value] = (count + 1, height, peers)
            else:
                occurance[hash_value] = (1, height, [peer])
    
        # Create a list to store peers with their height and count
        peer_list = []
        ic(occurance)

        #sort peers based on unique chains
        for hash_value, (count, height, peers) in occurance.items():
                peer_list.append((peers, height, count))

        # Sort by height first (descending) and then by count (descending)
        sorted_peers = sorted(peer_list, key=lambda x: (x[1], x[2]), reverse=True)
        return sorted_peers
    
   

        
    
    def get_priority_peers(self, stats_replies):

        stats = self.filter_stats(stats_replies)
        ordered_peers = self.find_priority_peers(stats)

        return ordered_peers

    # returns priority peers and other replies
    def execute(self):
        self.send_req()
        stats_replies = self.recv_res()
        priority_peers = self.get_priority_peers(stats_replies)
        ic('-'*50)
        ic("Priority peers:")
        for peer, height, count in priority_peers:

            ic(f"Peer: {peer}, Height: {height}, Count: {count}")
        ic('-'*50)
        return priority_peers 


    
