import json
import select
import time
import traceback
from announce import Announce
from gossip import Gossip
from stats import Stats
from blockchain import Blockchain
from block import Block
from get_block import GetBlock
import socket
import logging
from icecream import ic
from miner import Miner


# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define the log message format
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file named app.log
        logging.StreamHandler()           # Also log to the console
    ]
)


PORT =8784
BLOCKCHAIN = None

LAST_CONSENSUS_PERIOD = time.time()
CONSENSUS_PERIOD = 300  # Seconds

def test_gossip(sock,ip,port):

                gossip = Gossip(sock, ip, port, "Ramatjyot Singh")
                peers=gossip.execute()
                print(peers)
                return gossip,peers

def test_stats(sock,peers):
                stats = Stats(sock,peers)
                priority_peers = stats.execute()
                print(priority_peers)
                return stats,priority_peers




def test_get_blocks(priority_peer_groups, sock,gossip,stats):
    """
    Retrieves blockchain blocks from prioritized peer groups.

    Args:
        priority_peer_groups (dict): A dictionary where keys are blockchain heights (int)
                                     and values are lists of peer dictionaries with 'host' and 'port'.
        sock (socket.socket): The socket object used for network communication.
    """
    global BLOCKCHAIN
          
    

    for height, peers in priority_peer_groups.items():
        ic(f"Processing height: {height}")

        if BLOCKCHAIN is not None:
            if height <= BLOCKCHAIN.curr_height:
                break
            else:
                get_blocks = GetBlock(sock, BLOCKCHAIN, peers,gossip,stats)
                get_blocks.execute()
                if BLOCKCHAIN.is_valid():
                    ic(f"Validated blockchain at height {BLOCKCHAIN.curr_height}")
                    break
            
        # Validate that peers is a list
        if not isinstance(peers, list):
            ic(f"Invalid peers list for height {height}: {peers}")
            continue  # Skip to the next height

        
        BLOCKCHAIN = Blockchain(height)

        get_blocks = GetBlock(sock, BLOCKCHAIN, peers,gossip,stats)  
        get_blocks.execute()
    
        if BLOCKCHAIN.is_valid():
            ic(f"Validated blockchain at height {BLOCKCHAIN.curr_height}")

            return get_blocks
                    
        
            


def test_consensus(sock,ip,port):
    global BLOCKCHAIN
    gossip,peers = test_gossip(sock, ip, port)  # Fetch peers via gossip
    if peers:
        stats,priority_peer_group = test_stats(sock,peers)  # Prioritize peers

        ic("Handled prioritized peers.")
        ic(f"Peer group: {priority_peer_group}")
        if len(priority_peer_group) > 0:
            ic(f"Number of Priority Peers: {len(priority_peer_group)}")
            get_blocks = test_get_blocks(priority_peer_group, sock,gossip,stats)
            return gossip,stats,get_blocks

def test_handling_recvs(data, addr,  sock,ip,port, gossip,stats,get_block):
                    global BLOCKCHAIN
                    reply = json.loads(data)
                    peer={
                            'host':addr[0],
                            'port':addr[1]
                        }
                    ic(f"Received {reply['type']} from {addr[0]}:{addr[1]}")
                    if reply['type'] == 'GOSSIP'  or reply['type'] == 'GOSSIP_REPLY':
                                ic("Received GOSSIP request.")
                                gossip.handle_gossip(reply)
                    elif reply['type'] == 'ANNOUNCE':
                            ic("Received ANNOUNCE request.")
                            try:
                                
                                if BLOCKCHAIN:
                                    height = reply['height']
                                    if height > BLOCKCHAIN.curr_height:
                                        block = Block(reply['minedBy'], reply['messages'], reply['height'], reply['previous_hash'], reply['hash'], reply['nonce'], reply['timestamp'])
                                        if block is not None:
                                            BLOCKCHAIN.add_block(block,int(reply['height']))
                        

                            except Exception as e:
                                    ic(f"Error creating block: {e}")
                                    ic(traceback.format_exc())
                    elif reply['type'] == 'GET_BLOCK':
                                try:
                                    ic("Received GET_BLOCK request.")
                                    height = reply['height']
                                    if BLOCKCHAIN:

                                        get_block.send_res(peer, height)
                                        
                                except Exception as e:
                                    ic(f"Error handling GET_BLOCK: {e}")
                                    ic(traceback.format_exc())
                    elif reply['type'] == 'STATS':
                                try:
                                    ic("Received STATS request.")
                                    stats.send_res(BLOCKCHAIN, peer)
                                except Exception as e:
                                    ic(f"Error handling STATS: {e}")
                                    ic(traceback.format_exc())
                    elif reply['type'] == 'STATS_REPLY':
                        ic(f"Received STATS_REPLY from {addr[0]}:{addr[1]}")
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
                    elif reply['type'] == 'NEW_WORD':
                        ic("Received NEW_WORD request.")
                        try:
                            word = reply['word']
                            ic(f"Received new word: {word}")
                            return word
                        except Exception as e:
                            ic(f"Error handling NEW_WORD: {e}")
                            ic(traceback.format_exc())
                                         
                     
                        
def do_consenus(sock,ip,port):
      global LAST_CONSENSUS_PERIOD,BLOCKCHAIN
      curr_time = time.time()
      if curr_time - LAST_CONSENSUS_PERIOD > CONSENSUS_PERIOD:
            gossip,stats,get_block,BLOCKCHAIN =test_consensus(sock,ip,port)
            LAST_CONSENSUS_PERIOD = curr_time
            return  gossip,stats,get_block
      
if __name__ == "__main__":
    
    messages = []
    HOST = ''
    PORT = 8786
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        miner_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        miner_sock.bind((HOST, PORT))
        miner_sock.settimeout(1)
        miner_sock.listen(5)

       

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
            readables, writables, exceptions = select.select([sock], [sock,miner_sock], [sock,miner_sock], 1)
            # Exclude writable sockets if BLOCKCHAIN is not None

    

            # Handle writable sockets only if BLOCKCHAIN is None
        
            for writable_sock in writables:
                    if writable_sock == sock:
                        ic("Socket is writable.")
                        try:
                            if not BLOCKCHAIN:
                            
                                    gosip,stats,get_blocks= test_consensus(sock, ip, port)

                                    if BLOCKCHAIN:
                                        ic(f"Current Height: {BLOCKCHAIN.curr_height}")
                                        ic(f"Chain filled: {BLOCKCHAIN.is_chain_filled()}")

                            else:

                                gossip.background_task()  # Perform background tasks
                                gossip,stats,get_block = do_consenus(sock,ip,port)

                                data, addr = sock.recvfrom(4096)
                                word = test_handling_recvs(data, addr, sock, ip, port,gossip,stats,get_block)
                                messages.append(word)

                        except Exception as e:
                                ic(f"Error handling data: {e}")
                                ic(traceback.format_exc())
                                continue
                        except socket.timeout:
                                ic("Socket timed out.")
                                continue
                    elif writable_sock == miner_sock:
                        ic("Miner socket is writable.")
                        try:
                            conn, addr = miner_sock.accept()
                            
                            ic(f"Connected to {addr}")

                            if BLOCKCHAIN and BLOCKCHAIN.is_chain_filled():
                                gossip,peers = test_gossip(sock, ip, port)
                                last_block = BLOCKCHAIN.get_last_valid_block()
                                new_height = last_block.height + 1

                                
                                data = {
                                'height': new_height,
                                'previous_hash': last_block.hash
                                }
                                if messages:
                                    data['messages'] = messages
                                conn.sendall(json.dumps(data).encode('utf-8'))

                                data = conn.recv(4096)
                                mined_block = json.loads(data.decode('utf-8'))

                            
                                
                                if mined_block['height'] == new_height:
                                    BLOCKCHAIN.chain[new_height] = mined_block
                                    BLOCKCHAIN.curr_height = new_height 
                                    BLOCKCHAIN.total_height = new_height
                                    announce = Announce(sock,  mined_block, peers)
                                    ic(f"Block mined: {mined_block}")

                            
                            
                        except Exception as e:
                            ic(f"Error mining block: {e}")
                            ic(traceback.format_exc())
                            continue

            for bad_sock in exceptions:
                ic(f"Socket error: {bad_sock}")
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

            