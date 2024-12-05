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

def test_gossip(sock,ip,port):

                gossip = Gossip(sock, ip, port, "Ramatjyot Singh")
                peers=gossip.execute()
                print(peers)
                return peers

def test_stats(peers):
                stats = Stats(sock,peers)
                priority_peers = stats.execute()
                print(priority_peers)
                return priority_peers




def test_get_blocks(priority_peer_groups, sock):
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
                    get_blocks = GetBlock(sock, blockchain, [peer])  # Assuming GetBlock expects a list of peers
                    get_blocks.execute()
                    if blockchain.is_valid():
                        ic(f"Validated blockchain at height {height}")
                        return blockchain
                     

                    ic(f"Executed GetBlock for Peer: {peer_host}:{peer_port}")

                except Exception as e:
                    ic(f"Failed to get blocks from {peer_host}:{peer_port} - Error: {e}")
                    ic(traceback.format_exc())
            else:
                ic(f"Invalid peer information: {peer}")
           
                       



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
        gossip.first_gossip()
        while True:
            ic("Waiting for readable sockets...")
            readables, writables, exceptions = select.select([sock], [], [sock], 1)
            ic(f"Readables: {readables}")
            ic(f"Writables: {writables}")
            ic(f"Exceptions: {exceptions}")
            
            if not readables:
                ic("No readable sockets. Retrying...")
                continue  
            
            for readable_sock in readables:
                if readable_sock == sock:
                    ic("Socket is readable.")
                    try:
                        peers = test_gossip(sock, ip, port)  # Fetch peers via gossip
                        if peers:
                            priority_peer_group = test_stats(peers)  # Prioritize peers
                        
                            ic("Handled prioritized peers.")
                            ic(f"Peer group: {priority_peer_group}")
                            if len(priority_peer_group) > 0:
                                ic(len(priority_peer_group))
                                blockchain = test_get_blocks(priority_peer_group, sock)
                                ic(f"Blockchain: {blockchain}")
                                # Break out of the for-loop to proceed after finding peers
                                break
                    except Exception as e:
                        ic(f"Error handling data: {e}")
                        ic(traceback.format_exc())
                        break
            else:
                # The for-loop completed without finding a break (i.e., len(priority_peer_group) == 0)
                continue  # Continue the while loop
            
            # If the for-loop was broken (i.e., len(priority_peer_group) > 0), exit the while loop
            break