import socket
import time
import uuid
import json
from icecream import ic


class Gossip:

    #could have made peer an object but json is fine too lazy to do that
    WELL_KNOWN_PEER = {

        'host': '130.179.28.37',
        'port': 8999,
        'last_seen': int(time.time())

        }


    MAX_PEERS = 4

    CLEAN_UP_INTERVAL = 60
    KEEP_ALIVE_INTERVAL = 30


    def __init__(self, socket,host,port,name):

        self.socket = socket
        self.host = host
        self.port = port
        self.name = name
        self.id = None

        self.last_keep_alive = time.time()
        self.last_clean_up = time.time()

        self.known_peers = [ self.WELL_KNOWN_PEER ]
        self.seen_peers = set()

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

        ic('-'*50)
        ic(f"Peers here: {self.known_peers}")
        ic('-'*50)


        if peer_id and self.new_req(peer_id) and len(self.known_peers) < Gossip.MAX_PEERS:

            ic('-'*50)
            ic(f"Adding peer {peer_host}:{peer_port} with id {peer_id}")
            ic('-'*50)

            self.update_peer(peer_host,peer_port)

            ic("Adding peer to peers")

    def update_peer(self,peer_host,peer_port):

        is_new = self.new_known_peer(peer_host,peer_port)

        if is_new:

            peer = {

                'host': peer_host,
                'port': peer_port,
                'last_seen': int(time.time())

            }
            assert len(self.known_peers) < Gossip.MAX_PEERS
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

            ic('-'*50)
            ic(f"Removing known peer {peer['host']}:{peer['port']} ")
            ic('-'*50)


    def first_gossip(self):

        self.socket.sendto(json.dumps(self.create_req()).encode(), (Gossip.WELL_KNOWN_PEER['host'], Gossip.WELL_KNOWN_PEER['port']))


    def reply_gossip(self,gossip):

        try:

            peer_host,peer_port,peer_id = gossip['host'],gossip['port'],gossip['id']

        except KeyError:

            ic("Invalid gossip received")
            ic(gossip)

            return

        if self.new_req(peer_id) :

            ic('-'*50)
            ic(f"Replying to peer {peer_host}:{peer_port} with id {peer_id}")
            ic('-'*50)
            self.socket.sendto(json.dumps(self.create_res()).encode(), (peer_host, peer_port))

            self.track_peer(peer_host,peer_port,peer_id)

    def forward_gossip(self,gossip):

        try:

            gossip_host,gossip_port,gossip_id = gossip['host'],gossip['port'],gossip['id']

        except KeyError:

                ic("Invalid gossip received")
                ic(gossip)

                return

        if self.new_req(gossip_id):
            ic('-'*50)
            ic(f"Forwarding gossip from {gossip_host}:{gossip_port} with id {gossip_id}")
            ic('-'*50)
            self.track_peer(gossip_host,gossip_port,gossip_id)

            for peer in self.known_peers:

                host,port = peer['host'],peer['port']

                if host != gossip_host and port != gossip_port:

                    self.socket.sendto(json.dumps(gossip).encode(), (host, port))


    def recv_gossips(self,msg_count=100):

        socket.timeout(5)  # Set a timeout of 5 seconds
        msges = 0
        gossip_replies = []

        while msges < msg_count:

            try:
                data, addr = self.socket.recvfrom(1024)
                ic(data,addr)
                msges+=1
                reply = json.loads(data)
                ic(f"Received {reply['type']} from {addr[0]}:{addr[1]}")

                if reply['type'] == 'GOSSIP' or reply['type'] == 'GOSSIP_REPLY':

                    gossip_replies.append((reply, addr))

            except (TimeoutError, socket.timeout):
                ic("Socket timed out, no more data received.")
                break

            except json.JSONDecodeError:
                ic("Received malformed JSON data.")
                continue  # Continue processing other incoming messages


            except Exception  :
                ic('breaking out from loop')
                break


        ic('-'*50)

        return gossip_replies

    # retuns the known peer and other replies
    def execute(self):

        current_time = time.time()

        # Check if it's time to send keep_alive messages
        if current_time - self.last_keep_alive >= self.KEEP_ALIVE_INTERVAL:

            ic("Executing keep_alive")
            self.keep_alive()
            self.last_keep_alive = current_time


        # Check if it's time to perform clean_up
        if current_time - self.last_clean_up >= self.CLEAN_UP_INTERVAL:

            ic("Executing clean_up")
            self.clean_up()
            self.last_clean_up = current_time

        self.first_gossip()

        gossip_replies = self.recv_gossips()

        for gossip, addr in gossip_replies:


            self.handle_gossip(gossip)




        ic('-'*50)
        ic(f"Peers: {self.known_peers}")
        ic('-'*50)
        ic(f"Seen Peers: {self.seen_peers}")
        ic('-'*50)

        # ic(f"Other Replies: {other_replies}")
        # ic('-'*50)

        return self.known_peers



    def handle_gossip(self,gossip):

        reply_type = gossip['type']

        if reply_type == 'GOSSIP' :


            self.reply_gossip(gossip)
            self.forward_gossip(gossip)



        elif reply_type == 'GOSSIP_REPLY':

            if  Gossip.MAX_PEERS > len(self.known_peers)  :
                ic('-'*50)
                ic(len(self.known_peers))
                ic('-'*50)
                ic(Gossip.MAX_PEERS)

                self.update_peer(gossip['host'],gossip['port'])

    def keep_alive(self):


        for  peer in self.known_peers:
            self.socket.sendto(json.dumps(self.create_req()).encode(), (peer['host'], peer['port']))

    def clean_up(self):

        curr_time = time.time()

        if curr_time - self.last_clean_up > 60:

            self.seen_peers.clear()

        peers_to_remove = [peer for peer in self.known_peers if curr_time - peer['last_seen'] > 60]
        for peer in peers_to_remove:
            self.remove_peer(peer)


