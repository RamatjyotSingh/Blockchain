import json
import select
import traceback
from gossip import Gossip
from stats import Stats
from blockchain import Blockchain
from block import Block
from get_block import GetBlock
from icecream import ic
import socket


PORT =8784
BLOCKCHAIN = None

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

        for peer in peers:
            peer_host = peer.get('host')
            peer_port = peer.get('port')

            # Validate peer information
            if peer_host and peer_port:
                ic(f"Requesting blocks from Peer: {peer_host}:{peer_port}")
                try:
                    # Instantiate the Blockchain object with the current height
                    blockchain = Blockchain(height)

                    # Instantiate GetBlock with the socket, blockchain, and current peers
                    get_blocks = GetBlock(sock, blockchain, [peer])  # first list of priority peers
                    get_blocks.execute()
                    if blockchain.is_valid():
                        ic(f"Validated blockchain at height {height}")

                        return blockchain
                    
                    else:
                       
                        return BLOCKCHAIN # return either the prev blockchain or just none if th enew attempted blockchain is invalid
                       
                             
                         



                except Exception as e:
                    ic(f"Failed to get blocks from {peer_host}:{peer_port} - Error: {e}")
                    ic(traceback.format_exc())
            else:
                ic(f"Invalid peer information: {peer}")


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
                                block = Block(reply['minedBy'], reply['messages'], reply['height'], reply['hash'])

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
                                        give_block.send_res(peer)
                                        
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
                                    last_block = BLOCKCHAIN.get_last_block()
                                    if last_block is not None and last_block.hash != new_hash and last_block.height != new_height:
                                        ic(f"Received STATS_REPLY with new height: {new_height}")
                                        ic(f"Requesting blocks from peer: {peer}")
                                        test_consensus(sock,ip,port)
                                         
                        except Exception as e:
                            ic(f"Error handling STATS_REPLY: {e}")
                            ic(traceback.format_exc())
                        


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
        # Depending on your application's logic, you might want to remove this if redundant
        gossip.keep_alive()

        ic("Waiting for readable and writable sockets...")
        readables, writables, exceptions = select.select([sock], [sock], [sock], 1)
        ic(f"Readables: {readables}")
        ic(f"Writables: {writables}")
        ic(f"Exceptions: {exceptions}")

        for writable_sock in writables:
            if writable_sock == sock:
                ic("Socket is writable.")

                try:
                    

                    test_consensus(sock,ip,port)
                    break



                          
                except Exception as e:
                    ic(f"Error handling data: {e}")
                    ic(traceback.format_exc())
                    break
        else:
            # The for-loop completed without finding a break (i.e., len(priority_peer_group) == 0)
            continue  # Continue the while loop

        # for readable_sock in readables:
        #     if readable_sock == sock:
        #         ic("Socket is readable.")
        #         try:
        #             gossip.background_task()  # Perform background tasks
        #             data, addr = sock.recvfrom(4096)
        #             # test_handlying_recvs(data, addr, sock, ip, port, BLOCKCHAIN)
                           
        #         except Exception as e:
        #             ic(f"Error sending keep-alive: {e}")
        #             ic(traceback.format_exc())
        #             break

        # else:
        #     continue  # Continue the while loop if no break occurred

        # Optional: Define an exit condition to break the while loop
        # For example, after successfully handling peers and blocks
        # break