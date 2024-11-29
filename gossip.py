import time
import uuid
import json

class Gossip:

    SEEN_PEERS = {}
    KNOWN_PEER = {'host': 'silicon.cs.umanitoba.ca', 'port': 8999}
    MAX_PEERS = 3

    def __init__(self, socket,host,port,name):
        self.socket = socket
        self.host = host
        self.port = port
        self.name = name
        self.peers = {}
        self.my_peer = None


 
    def create_req(self) :
        self.my_peer = str(uuid.uuid4())
        return {
            "type": "GOSSIP",
            "host": self.host,
            "port": self.port,
            "id": self.my_peer,
            "name": self.name
        }
    

    
    def create_res(self) :
        return {
            "type": "GOSSIP_REPLY",
            "host": self.host,
            "port": self.port,
            "name": self.name
        }
    
    def new_peer(self,id):

        return id not in Gossip.SEEN_PEERS and id != str(self.my_peer)
         
    
    def add_peer(self, peer_host, peer_port,peer_id):
        print('-'*50)
        print(f"Peers here: {self.peers}")
        print('-'*50)
        if peer_id and self.new_peer(peer_id):
            print('-'*50)
            print(f"Adding peer {peer_host}:{peer_port} with id {peer_id}")
            print('-'*50)
            if len(self.peers) <= Gossip.MAX_PEERS:
                print("Adding peer to peers")
                self.peers[peer_id] = {'host': peer_host, 'port': peer_port}
                Gossip.SEEN_PEERS[peer_id] = time.time() 
       
        

    def remove_peer(self, peer_id):

        if id in self.peers:
            del self.peers[peer_id]

        if id in Gossip.SEEN_PEERS:
            del Gossip.SEEN_PEERS[peer_id]
        

    
    def first_gossip(self):

        self.socket.sendto(json.dumps(self.create_req()).encode(), (Gossip.KNOWN_PEER['host'], Gossip.KNOWN_PEER['port']))
    

    def reply_gossip(self,gossip):

        peer_host,peer_port,peer_id = gossip['host'],gossip['port'],gossip['id']

        if self.new_peer(peer_id):
            print('-'*50)
            print(f"Replying to peer {peer_host}:{peer_port} with id {peer_id}")
            print('-'*50)
            self.add_peer(peer_host,peer_port,peer_id)
            self.socket.sendto(json.dumps(self.create_res()).encode(), (peer_host, peer_port))

    def forward_gossip(self,gossip):
        peer_id = gossip['id']
        if self.new_peer(peer_id):
            print('-'*50)
            print(f"Forwarding gossip from {gossip['host']}:{gossip['port']} with id {peer_id}")
            print('-'*50)
            self.add_peer(gossip['host'],gossip['port'],peer_id)
            for id, peer in self.peers.items():
                self.socket.sendto(json.dumps(gossip).encode(), (peer['host'], peer['port']))   
    
    def recv_gossip(self):
        self.socket.settimeout(5)  # Set a timeout of 5 seconds
        replies = []
        while True:
            try:
                reply, addr = self.socket.recvfrom(1024)
                replies.append((reply, addr))
            except TimeoutError:
                print("Socket timed out, no more data received.")
                break
        print('-'*50)
       
        return replies
    
    def execute(self):

        
        self.first_gossip()
        other_replies = []
        replies = self.recv_gossip()

        for reply, addr in replies:

            gossip = json.loads(reply.decode())

            notgossip = self.handle_gossip(gossip)

            if  notgossip:
                other_replies.append(notgossip)
                return None
      


        print('-'*50)
        print(f"Peers: {self.peers}")
        print('-'*50)
        print('-'*50)
        print(f"Seen Peers: {Gossip.SEEN_PEERS}")
        print('-'*50)
        print('-'*50)
        print(f"Other Replies: {other_replies}")
        print('-'*50)
        return other_replies
            
       
            
      
    def handle_gossip(self,gossip):
        reply_type = gossip['type']
        if reply_type == 'GOSSIP' :
            print('-'*50)
            print("here")
            self.reply_gossip(gossip)
            self.forward_gossip(gossip)
            return None

        elif reply_type == 'GOSSIP_REPLY':

            self.add_peer(gossip['host'],gossip['port'],None)
            return None
    def keep_alive(self):
      
        for id, peer in self.peers.items():
            self.socket.sendto(json.dumps(self.create_req()).encode(), (peer['host'], peer['port']))
          
    def clean_up(self):
        
        curr_time = time.time()
        for id, timestamp in Gossip.SEEN_PEERS.items():
            if curr_time - timestamp > 60:
                self.remove_peer(id)
        