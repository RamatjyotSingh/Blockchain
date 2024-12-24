import socket
import time
import uuid
import json
import logging
from icecream import ic
# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define the log message format
    handlers=[
        logging.FileHandler("gossip.log"),  # Log to a file named app.log
        logging.StreamHandler()           # Also log to the console
    ]
)

class Gossip:


    def __init__(self, socket, name , well_known_peers, max_peers, clean_up_interval, keep_alive_interval):

        self.socket = socket
        self.host, self.port = self.socket.getsockname()
        self.name = name
        self.id = None
        self.current_time = time.time()
        self.last_keep_alive = time.time()
        self.last_clean_up = time.time()
        
        self.known_peers = well_known_peers
        self.seen_peers = set()
        self.MAX_PEERS = max_peers
        self.CLEAN_UP_INTERVAL = clean_up_interval
        self.KEEP_ALIVE_INTERVAL = keep_alive_interval


    def create_req(self) :

        self.id = str(uuid.uuid4())

        return {

            "type": "GOSSIP",
            "host": self.host,
            "port": self.port,
            "id": self.id,
            "name": self.name

        }



    def create_res(self) :

        return {

            "type": "GOSSIP_REPLY",
            "host": self.host,
            "port": self.port,
            "name": self.name

        }

    def new_req(self, peer_id):

        if peer_id in self.seen_peers:

            return False

        self.seen_peers.add(peer_id)

        return True




    def new_known_peer(self,peer_host,peer_port):

        return self.find_known_peer(peer_host,peer_port) is None




    def find_known_peer(self,peer_host,peer_port):

            peer = next((peer for peer in self.known_peers if peer.get('host') == peer_host and peer.get('port') == peer_port), None)

            return peer





    def track_peer(self, peer_host, peer_port,peer_id):

        # print('-'*50)
        # print(f"Peers here: {self.known_peers}")
        # print('-'*50)


        if peer_id and self.new_req(peer_id) and len(self.known_peers) < self.MAX_PEERS:

            # print('-'*50)
            # print(f"Adding peer {peer_host}:{peer_port} with id {peer_id}")
            # print('-'*50)

            self.update_peer(peer_host,peer_port)

            print("Adding peer to peers")

    def update_peer(self,peer_host,peer_port):

        is_new = self.new_known_peer(peer_host,peer_port)

        if is_new:

            peer = {

                'host': peer_host,
                'port': peer_port,
                'last_seen': int(time.time())

            }
            assert len(self.known_peers) < self.MAX_PEERS
            self.known_peers.append(peer)

        else:

            self.update_peer_time(peer_host,peer_port)


    def update_peer_time(self,peer_host,peer_port):

        peer = self.find_known_peer(peer_host,peer_port)

        if peer:

            peer['last_seen'] = time.time()

    def remove_peer(self, peer):

        peer_host,peer_port = peer['host'],peer['port']

        known_peer = self.find_known_peer(peer_host,peer_port)





        if known_peer:

            self.known_peers.remove(known_peer)

            # print('-'*50)
            print(f"Removing known peer {peer['host']}:{peer['port']} ")
            # print('-'*50)


    def first_gossip(self):

        for WELL_KNOWN_PEER in self.known_peers:
            self.socket.sendto(json.dumps(self.create_req()).encode(), (WELL_KNOWN_PEER['host'], WELL_KNOWN_PEER['port']))


    def reply_gossip(self,gossip):

        try:

            peer_host,peer_port,peer_id = gossip['host'],gossip['port'],gossip['id']

        except KeyError:

            logging.error("Invalid gossip received")
            logging.error(gossip)

            return

        if self.new_req(peer_id) :

            # print('-'*50)
            # print(f"Replying to peer {peer_host}:{peer_port} with id {peer_id}")
            # print('-'*50)
            self.socket.sendto(json.dumps(self.create_res()).encode(), (peer_host, peer_port))

            self.track_peer(peer_host,peer_port,peer_id)

    def forward_gossip(self,gossip):

        try:

            gossip_host,gossip_port,gossip_id = gossip['host'],gossip['port'],gossip['id']

        except KeyError:

                logging.error("Invalid gossip received")
                logging.error(gossip)

                return

        if self.new_req(gossip_id):
            # print('-'*50)
            # print(f"Forwarding gossip from {gossip_host}:{gossip_port} with id {gossip_id}")
            # print('-'*50)
            self.track_peer(gossip_host,gossip_port,gossip_id)

            for peer in self.known_peers:

                host,port = peer['host'],peer['port']

                if host != gossip_host and port != gossip_port:

                    self.socket.sendto(json.dumps(gossip).encode(), (host, port))


    def recv_gossips(self,msg_count=200):

        self.socket.settimeout(5)  # Set a timeout of 5 seconds
        gossip_replies = []
        msges =0
        while msges < msg_count:
            

            try:
                data, addr = self.socket.recvfrom(4096)
                msges += 1
                
                reply = json.loads(data)

                if reply['type'] == 'GOSSIP' or reply['type'] == 'GOSSIP_REPLY':

                    gossip_replies.append((reply, addr))

                else:
                    continue

            except (TimeoutError, socket.timeout):
                logging.error("Socket timed out, no more data received.")
                break

            except json.JSONDecodeError:
                logging.error("Received malformed JSON data.")
                continue  # Continue processing other incoming messages


            except Exception  :
                logging.error('breaking out from loop')
                break


        # print('-'*50)

        return gossip_replies

    # retuns the known peer and other replies
    def execute(self):

        

        self.first_gossip()

        gossip_replies = self.recv_gossips()

        for gossip, addr in gossip_replies:


            self.handle_gossip(gossip)




        # print('-'*50)
        print(f"Peers: {self.known_peers}")
        # print('-'*50)
        print(f"Seen Peers: {self.seen_peers}")
        # print('-'*50)

       
        return self.known_peers



    def handle_gossip(self,gossip):

        reply_type = gossip['type']

        if reply_type == 'GOSSIP' :


            self.reply_gossip(gossip)
            self.forward_gossip(gossip)



        elif reply_type == 'GOSSIP_REPLY':

            if  self.MAX_PEERS > len(self.known_peers)  :
                # print('-'*50)
                # print(len(self.known_peers))
                # # print('-'*50)
                # print(Gossip.MAX_PEERS)

                self.update_peer(gossip['host'],gossip['port'])
        else:
            return

    def keep_alive(self):
         
        if self.current_time - self.last_keep_alive >= self.KEEP_ALIVE_INTERVAL:

            print("Executing keep_alive")
            for  peer in self.known_peers:
                self.socket.sendto(json.dumps(self.create_req()).encode(), (peer['host'], peer['port']))
            self.last_keep_alive = self.current_time


        

    def clean_up(self):


        if self.current_time - self.last_clean_up >= self.CLEAN_UP_INTERVAL:
            
            print("Executing clean_up")

            self.seen_peers.clear()

        peers_to_remove = [peer for peer in self.known_peers if self.current_time - peer['last_seen'] > self.CLEAN_UP_INTERVAL]
        for peer in peers_to_remove:
            self.remove_peer(peer)

        self.last_clean_up = self.current_time

    def do_background_tasks(self):

        # Check if it's time to perform keep_alive
    
        self.keep_alive()


        # Check if it's time to perform clean_up

        self.clean_up()
