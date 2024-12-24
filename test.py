import json
import select
import time
import traceback
from gossip import Gossip
from stats import Stats
from blockchain import Blockchain
from block import Block
from get_block import GetBlock
import socket
from icecream import ic




BLOCKCHAIN = None

LAST_CONSENSUS_PERIOD = time.time()
CONSENSUS_PERIOD = 300  # Seconds

def test_gossip(sock,ip,port):

                gossip = Gossip(sock, ip, port, "Ramatjyot Singh")
                peers=gossip.execute()
                print(peers)
                return peers

def test_stats(sock,peers):
                stats = Stats(sock,peers)
                priority_peers = stats.execute()
                print(priority_peers)
                return priority_peers




def test_get_blocks(priority_peer_groups, sock,BLOCKCHAIN=None):
    """
    Retrieves blockchain blocks from prioritized peer groups.

    Args:
        priority_peer_groups (dict): A dictionary where keys are blockchain heights (int)
                                     and values are lists of peer dictionaries with 'host' and 'port'.
        sock (socket.socket): The socket object used for network communication.
    """
    
          
    # Validate the input type
    if not isinstance(priority_peer_groups, dict):
        ic(f"Invalid type for priority_peer_groups: {type(priority_peer_groups)}. Expected dict.")
        return

    for height, peers in priority_peer_groups.items():
        ic(f"Processing height: {height}")

        if BLOCKCHAIN is not None:
            if height <= BLOCKCHAIN.curr_height:
                return BLOCKCHAIN
           
            
        # Validate that peers is a list
        if not isinstance(peers, list):
            ic(f"Invalid peers list for height {height}: {peers}")
            continue  # Skip to the next height

        try:  

            blockchain = Blockchain(height)

            get_blocks = GetBlock(sock, blockchain, peers)  
            get_blocks.execute()

        except Exception as e:
            ic(f"Error getting blocks: {e}")
            ic(traceback.format_exc())
            continue
        
        if blockchain.is_valid():
            
            ic(f"Validated blockchain at height {blockchain.curr_height}")

            return blockchain
                    
        
            


def test_consensus(sock,ip,port):
    global BLOCKCHAIN
    peers = test_gossip(sock, ip, port)  # Fetch peers via gossip
    if peers:
        priority_peer_group = test_stats(sock,peers)  # Prioritize peers

        ic("Handled prioritized peers.")
        ic(f"Peer group: {priority_peer_group}")
        if len(priority_peer_group) > 0:
            ic(f"Number of Priority Peers: {len(priority_peer_group)}")
            BLOCKCHAIN = test_get_blocks(priority_peer_group, sock,BLOCKCHAIN)
            return BLOCKCHAIN

def test_handling_recvs(data, addr,  sock,ip,port, BLOCKCHAIN):
                    
                    reply = json.loads(data)
                    peer={
                            'host':addr[0],
                            'port':addr[1]
                        }
                    ic(f"Received {reply['type']} from {addr[0]}:{addr[1]}")
                    if reply['type'] == 'GOSSIP'  or reply['type'] == 'GOSSIP_REPLY':
                                gossip = Gossip(sock, ip, port, "Ramatjyot Singh")
                                gossip.handle_gossip(reply)
                    elif reply['type'] == 'ANNOUNCE':
                            try:
                                last_block = BLOCKCHAIN.chain[-1]
                                block = Block(
                                        minedBy=reply['minedBy'],
                                        messages=reply['messages'],
                                        height=reply['height'],
                                        prev_hash=last_block.hash,
                                        hash=reply['hash'],
                                        nonce=reply['nonce'],
                                        timestamp=reply['timestamp']
                                        )

                                if block and BLOCKCHAIN:
                                    BLOCKCHAIN.add_block(block, reply['height'])

                            except Exception as e:
                                    ic(f"Error creating block: {e}")
                                    ic(traceback.format_exc())
                    elif reply['type'] == 'GET_BLOCK':
                                try:
                                    height = reply['height']
                                    if BLOCKCHAIN:

                                        give_block = GetBlock(sock, BLOCKCHAIN, [peer])
                                        give_block.send_res(peer, height)
                                        
                                except Exception as e:
                                    ic(f"Error handling GET_BLOCK: {e}")
                                    ic(traceback.format_exc())
                    elif reply['type'] == 'STATS':
                                try:
                                    stats = Stats(sock, [peer])
                                    stats.send_res(BLOCKCHAIN, peer)
                                except Exception as e:
                                    ic(f"Error handling STATS: {e}")
                                    ic(traceback.format_exc())
                    elif reply['type'] == 'STATS_REPLY':
                        try:
                            new_height = reply['height']
                            new_hash = reply['hash']
                            if BLOCKCHAIN:
                                    chain_length = len(BLOCKCHAIN.chain)
                                    last_block = BLOCKCHAIN.get_last_block()
                                    if last_block is not None and last_block.hash != new_hash and chain_length != new_height:
                                        ic(f"Received STATS_REPLY with new height: {new_height}")
                                        ic(f"Requesting blocks from peer: {peer}")
                                        test_consensus(sock,ip,port)
                        except Exception as e:
                            ic(f"Error handling STATS_REPLY: {e}")
                            ic(traceback.format_exc())

                    elif reply['type'] == 'CONSENSUS':
                        try:
                            ic("Received CONSENSUS request.")
                            test_consensus(sock,ip,port)
                        except Exception as e:
                            ic(f"Error handling CONSENSUS: {e}")
                            ic(traceback.format_exc())
                                         
                     
                        
def do_consenus(sock,ip,port):
      global LAST_CONSENSUS_PERIOD
      curr_time = time.time()
      if curr_time - LAST_CONSENSUS_PERIOD > CONSENSUS_PERIOD:
            test_consensus(sock,ip,port)
            LAST_CONSENSUS_PERIOD = curr_time
            return True
      

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    port = PORT

    try:
        sock.bind((ip, port))
        ic(f"Socket bound to {ip}:{port}")
    except Exception as e:
        ic(f"Failed to bind socket: {e}")
        exit(1)

    gossip = Gossip(sock, ip, port, "Ramatjyot Singh")
    # gossip.first_gossip()

    while True:
        

        ic("Waiting for readable and writable sockets...")
        readables, writables, exceptions = select.select([sock], [sock], [sock], 1)
        # Exclude writable sockets if BLOCKCHAIN is not None

        ic(f"Readables: {readables}")
        ic(f"Writables: {writables}")
        ic(f"Exceptions: {exceptions}")

        # Handle writable sockets only if BLOCKCHAIN is None
       
        for writable_sock in writables:
                if writable_sock == sock:
                    ic("Socket is writable.")
                    try:
                        if not BLOCKCHAIN:
                        
                                BLOCKCHAIN = test_consensus(sock, ip, port)

                                if BLOCKCHAIN:
                                    ic(f"Current Height: {BLOCKCHAIN.curr_height}")
                                    ic(f"Chain filled: {BLOCKCHAIN.is_chain_filled()}")

                        else:

                            gossip.background_task()  # Perform background tasks
                            do_consenus(sock,ip,port)

                            data, addr = sock.recvfrom(4096)
                            test_handling_recvs(data, addr, sock, ip, port, BLOCKCHAIN)
                            

                    except Exception as e:
                            ic(f"Error handling data: {e}")
                            ic(traceback.format_exc())
                            break
                    except socket.timeout:
                            ic("Socket timed out.")
                            break
            

        # # Handle readable sockets
        # for readable_sock in readables:
        #     if readable_sock == sock:
        #         ic("Socket is readable.")
        #         try:
        #             gossip.background_task()  # Perform background tasks
        #             data, addr = sock.recvfrom(4096)
        #             test_handling_recvs(data, addr, sock, ip, port, BLOCKCHAIN)
        #         except Exception as e:
        #             ic(f"Error receiving data: {e}")
        #             ic(traceback.format_exc())
        #             break

        