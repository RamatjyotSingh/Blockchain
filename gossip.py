import uuid
import json

class Gossip:

    SEEN_PEERS = []
    KNOWN_PEER = {'host': 'silicon.cs.umanitoba.ca', 'port': 8998}
    MAX_PEERS = 3

    def __init__(self, socket,host,port,name):
        self.socket = socket
        self.host = host
        self.port = port
        self.name = name
        self.peers = {}

 
    def create_req(self) :
        return {
            "type": "GOSSIP",
            "host": self.host,
            "port": self.port,
            "id": uuid.uuid4().hex,
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
        return id not in Gossip.SEEN_PEERS
    
    def add_peer(self, peer_host, peer_port,peer_id):
        if self.new_peer(peer_id):
            if len(self.peers) <= Gossip.MAX_PEERS:
                self.peers[peer_id] = {'host': peer_host, 'port': peer_port}
            Gossip.SEEN_PEERS.append(peer_id)
       
        

    def remove_peer(self, peer_id):
         if id in self.peers:
            del self.peers[peer_id]
        

    
    def first_gossip(self):

        self.socket.sendto(json.dumps(self.create_req()).encode(), (Gossip.KNOWN_PEER['host'], Gossip.KNOWN_PEER['port']))
    

    def reply_gossip(self,peer_host,peer_port,peer_id):

        if self.new_peer(peer_id):
            self.add_peer(peer_host,peer_port,peer_id)
            self.socket.sendto(json.dumps(self.create_res()).encode(), (peer_host, peer_port))

    def forward_gossip(self,gossip):
        peer_id = gossip['id']
        if self.new_peer(peer_id):
            self.add_peer(gossip['host'],gossip['port'],peer_id)
            for id, peer in self.peers.items():
                self.socket.sendto(json.dumps(gossip).encode(), (peer['host'], peer['port']))   
    
    def execute(self):
        self.first_gossip()
        reply = self.socket.recv(1024)

        gossip = json.loads(reply.decode())
        reply_type = gossip['type']

        if reply_type == 'GOSSIP'.ignorecase() :

            self.reply_gossip(gossip['host'],gossip['port'],gossip['id'])
            self.forward_gossip(gossip)

        elif reply_type == 'GOSSIP_REPLY'.ignorecase():

            self.add_peer(gossip['host'],gossip['port'],gossip['id'])
            
        else:
            return
            