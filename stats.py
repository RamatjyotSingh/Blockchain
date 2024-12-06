import json
import socket
import logging
from icecream import ic
# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define the log message format
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file named app.log
        logging.StreamHandler()           # Also log to the console
    ]
)

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
            "height":block.height+1,
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

    def recv_res(self,max_msges=200):

        self.socket.settimeout(5)  # Set a timeout of 5 seconds
        stats_replies = []
        msges = 0
        while msges < max_msges:
            try:
                data, addr = self.socket.recvfrom(1024)
                msges += 1
                reply = json.loads(data)
                reply_type = reply['type'] 
                if reply_type == 'STATS_REPLY':
                    ic(f"Received {reply_type} from {addr[0]}:{addr[1]}")

                    stats_replies.append((reply,addr))
                else :
                    continue
               

           
            except (TimeoutError, socket.timeout):
                logging.error("Socket timed out, no more data received.")
                break

            except Exception  :
                logging.error('breaking out from loop')
                break

           

        return stats_replies
    
    def send_res(self,blockchain,peer):

        if  blockchain.is_chain_filled():
            last_block = blockchain.chain[-1]
            res = self.create_res(last_block)
            host = peer['host']
            port = peer['port']
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
            try:
                hash_value = stat['hash']
                if hash_value == None:
                    continue
                height = stat['height']
                if hash_value in occurance:
                    count, height, peers = occurance[hash_value]
                    peers.append(peer)
                    occurance[hash_value] = (count + 1, height, peers)
                else:
                    occurance[hash_value] = (1, height, [peer])
            except Exception as e:
                logging.error(f"Invalid stat: {stat}")
                logging.error(f"Error: {e}")
                
                # Handle the invalid stat appropriately
    
        # Create a list to store peers with their height and count
        peer_list = []
        ic(occurance)

        #sort peers based on unique chains
        for hash_value, (count, height, peers) in occurance.items():
                peer_list.append((peers, height, count))

        # Sort by height first (descending) and then by count (descending)
        sorted_peers = sorted(peer_list, key=lambda x: (x[1], x[2]), reverse=True)
        return sorted_peers
    
   

        
    
    def get_priority_peer_group(self, stats_replies):
        stats = self.filter_stats(stats_replies)
        ordered_peers = self.find_priority_peers(stats)
    
        priority_peer_groups = {}
        for peer_entries, height, count in ordered_peers:
            peer_list = []
            for peer_host, peer_port in peer_entries:
                peer_list.append({'host': peer_host, 'port': peer_port})
            ic(f"Peers: {peer_list}")
    
            if isinstance(height, int):
                priority_peer_groups[height] = peer_list
            else:
                logging.error(f"Invalid height type: {height} (Type: {type(height)})")
                # Handle the invalid height appropriately
    
        return priority_peer_groups


    # returns priority peers and other replies
    def execute(self):
        self.send_req()
        stats_replies = self.recv_res()
        priority_peer_groups = self.get_priority_peer_group(stats_replies)
        # ic('-'*50)
        ic("Priority peers:")
       
        return priority_peer_groups


    
