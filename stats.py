import json
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
        for peer in self.peers.values():  # Iterate over the values of the dictionary
            host = peer['host']
            port = peer['port']
            ic('-'*50)
            ic(f"Sending STATS to {host}:{port}")
            ic('-'*50)
            self.socket.sendto(json.dumps(req).encode(), (host, port))

    def recv_res(self):

        self.socket.settimeout(10)
        stats_replies = []
        other_replies = []

        while True:
            ic("Waiting for stat replies...")
            try:
                ic('here')
                data, addr = self.socket.recvfrom(1024)
                reply = json.loads(data)

                if reply['type'] == 'STATS_REPLY':
                    ic(f"Received {reply['type']} from {addr[0]}:{addr[1]}")

                    stats_replies.append((reply,addr))
                else:
                    other_replies.append((reply,addr))

            except TimeoutError:
                break

        return stats_replies, other_replies
    
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
        for hash_value, (count, height, peers) in occurance.items():
            for peer in peers:
                peer_list.append((peer, height, count))

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
        stats_replies, other_replies = self.recv_res()
        priority_peers = self.get_priority_peers(stats_replies)
        ic('-'*50)
        ic("Priority peers:")
        for peer, height, count in priority_peers:
            ic(f"Peer: {peer}, Height: {height}, Count: {count}")
        ic('-'*50)
        return priority_peers , other_replies


    
