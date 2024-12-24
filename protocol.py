import argparse
from    consensus import Consensus
from stats import Stats
from announce import Announce
from get_block import GetBlock
from gossip import Gossip
from blockchain import Blockchain
import socket
import time

class Protocol:

    def __init__(self, name="Ramatjyot Singh", port=8784,tcp_port=8785 ,max_peers=4, clean_up_interval=60, keep_alive_interval=30, difficulty=8, well_known_peers=None, chunk_size=150, retry_limit=3,consensus_interval=600):
        self.name = name
        self.PORT = port
        self.MAX_PEERS = max_peers
        self.CLEAN_UP_INTERVAL = clean_up_interval
        self.KEEP_ALIVE_INTERVAL = keep_alive_interval
        self.DIFFICULTY = difficulty
        self.WELL_KNOWN_PEERS = well_known_peers if well_known_peers else [{
            'host': '130.179.28.37',
            'port': 8999,
            'last_seen': int(time.time())
        }]
        self.CHUNK_SIZE = chunk_size
        self.RETRY_LIMIT = retry_limit
        self.CONSENSUS_INTERVAL = consensus_interval
        self.setup_sock()
        self.blockchain = None
        self.consensus = None
        self.stats = None
        self.announce = None
        self.get_block = None
        self.gossip = None
        self.TCPPort = tcp_port
      

    def setup_sock(self):
        '''
        Creates and returns UDP socket and binds it to the given port.
        '''
        ip = socket.gethostbyname(socket.gethostname())
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, self.PORT))
        host, port = self.socket.getsockname()
        self.socket.settimeout(5)
        print(f"Socket is bound to IP: {host}, Port: {port}")
        
    def init_blockchain(self, total_height):
        """
        Initializes the blockchain with the given total height and difficulty.
        This method should only be called after obtaining stats from other nodes.
        
        Args:
            total_height (int): The total height of the blockchain.
        
        Raises:
            AssertionError: If the stats module is not initialized.
        """
        assert self.stats is not None, "Stats module must be initialized before blockchain."

        self.blockchain = Blockchain(total_height, self.DIFFICULTY)
    
    def init_gossip(self):
        """
        Initializes the gossip protocol with the default name "Ramatjyot Singh" unless modified through --modify-params.
        
        """
        self.gossip = Gossip(self.socket, self.name, self.WELL_KNOWN_PEERS, self.MAX_PEERS, self.CLEAN_UP_INTERVAL, self.KEEP_ALIVE_INTERVAL)
    
    def init_stats(self, peers):

        """
        Initializes the stats module with the given peers.
        This method should only be called after gossiping with other nodes and tracking them.
        
        Args:
            peers (list): A list of peers tracked by the gossip module.
        
        Raises:
            AssertionError: If the gossip module is not initialized.
        """
        assert self.gossip is not None, "Gossip module must be initialized before stats."
        self.stats = Stats(self.socket, peers)
    
    def init_get_block(self, priority_peers):
        """
        Initializes the get_block module with the given priority peers.
        This method should only be called after initializing the blockchain.
        
        Args:
            priority_peers (list): A list of priority peers for block retrieval, obtained through the stats module.
        
        Raises:
            AssertionError: If the blockchain module is not initialized.
        """
        assert self.blockchain is not None, "Blockchain module must be initialized before get_block."
        self.get_block = GetBlock(self.socket, priority_peers, self.blockchain, self.gossip, self.stats, self.CHUNK_SIZE, self.RETRY_LIMIT)

   



    def create_miner_socket(self):

        self.TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCPsocket.bind((socket.gethostbyname(socket.gethostname()), self.TCPPort))
        self.TCPsocket.listen(5)
        self.TCPsocket.setblocking(False)
        print(f"Miner Master is listening on IP: {socket.gethostbyname(socket.gethostname())}, Port: {self.TCPPort}")
        return self.TCPsocket
   

    def announce_block(self, block, peers):
        """
        Announces a new block to the given peers.
        
        Args:
            block (Block): The block to be announced.
            peers (list): A list of peers to announce the block to.
        """
        self.announce = Announce(self.socket, block, peers)
        self.blockchain.add_block_from_reply(block) # Add the block to the blockchain
    

    def init_consensus(self,MyPeer):
        """
        Initializes the consensus module.
        
        Args:
            MyPeer (Peer): The peer object representing the current node.
        """
        self.consensus = Consensus(MyPeer, self.CONSENSUS_INTERVAL)

    def get_socket(self):
        return self.socket

    def modify_params(self):

        print("\n--- Modify Class-Level Constants ---")
        print("WARNING: You are about to modify class-level constants. This provides great flexibility to adjust the behavior of the blockchain. However, incorrect parameters may cause the program to crash or behave unexpectedly. Do you wish to proceed? (y/n)")
        choice = input().strip().lower()
        if choice == 'n':
            return
        elif choice == 'y':
            while True:
            
                try:
                
                    print("Available parameters to change:")
                    print("1. Change NAME (Node name)")
                    print("2. Change MAX_PEERS (Maximum number of peers to track)")
                    print("3. Change CLEAN_UP_INTERVAL (Interval in seconds to clean up peers)")
                    print("4. Change KEEP_ALIVE_INTERVAL (Interval in seconds to send keep-alive messages)")
                    print("5. Change DIFFICULTY (Block difficulty level to accept)")
                    print("6. Change WELL_KNOWN_PEERS (List of well-known peers)")
                    print("7. Change CHUNK_SIZE (Size of chunks of blocks to recv from peers)")
                    print("8. Change RETRY_LIMIT (Number of retry attempts from peers before giving up)")
                    print("9. Change Consensus Interval(Number of seconds to wait before running consensus)")
                    print("10. Change Port for Miner")
                    print("11. Exit")
                    param_choice = input("Enter your choice: ").strip()

                    if param_choice == '1':
                        new_value = input("Enter new value for NAME: ").strip()
                        self.name = new_value
                        print(f"NAME set to {self.name}")
                    elif param_choice == '2':
                        new_value = int(input("Enter new value for MAX_PEERS: ").strip())
                        self.MAX_PEERS = new_value
                        print(f"MAX_PEERS set to {self.MAX_PEERS}")
                    elif param_choice == '3':
                        new_value = int(input("Enter new value for CLEAN_UP_INTERVAL (seconds): ").strip())
                        self.CLEAN_UP_INTERVAL = new_value
                        print(f"CLEAN_UP_INTERVAL set to {self.CLEAN_UP_INTERVAL} seconds")
                    elif param_choice == '4':
                        new_value = int(input("Enter new value for KEEP_ALIVE_INTERVAL (seconds): ").strip())
                        self.KEEP_ALIVE_INTERVAL = new_value
                        print(f"KEEP_ALIVE_INTERVAL set to {self.KEEP_ALIVE_INTERVAL} seconds")
                    elif param_choice == '5':
                        new_value = int(input("Enter new value for DIFFICULTY: ").strip())
                        self.DIFFICULTY = new_value
                        print(f"DIFFICULTY set to {self.DIFFICULTY}")
                    elif param_choice == '6':
                        new_peers = input("Enter new well-known peers in the format 'host:port,host:port' ").strip()
                        self.WELL_KNOWN_PEERS = [{'host': host, 'port': int(port), 'last_seen': int(time.time())} for host, port in (peer.split(':') for peer in new_peers.split(','))]
                        print(f"WELL_KNOWN_PEERS set to {self.WELL_KNOWN_PEERS}")
                    elif param_choice == '7':
                        new_value = int(input("Enter new value for CHUNK_SIZE: ").strip())
                        self.CHUNK_SIZE = new_value
                        print(f"CHUNK_SIZE set to {self.CHUNK_SIZE}")
                    elif param_choice == '8':
                        new_value = int(input("Enter new value for RETRY_LIMIT: ").strip())
                        self.RETRY_LIMIT = new_value
                        print(f"RETRY_LIMIT set to {self.RETRY_LIMIT}")
                    elif param_choice == '9':
                        new_value = int(input("Enter new value for Consensus Interval: ").strip())
                        self.CONSENSUS_INTERVAL = new_value
                        print(f"Consensus Interval set to {self.CONSENSUS_INTERVAL}")
                    elif param_choice == '10':
                        new_value = int(input("Enter new value for Port for Miner: ").strip())
                        self.TCPPort = new_value
                        print(f"Port for Miner set to {self.TCPPort}")
                    elif param_choice == '11':
                        print("Exiting menu.")
                        break
                    else:
                        print("Invalid choice. Please try again.")
                        continue
                        
                    print("Do you want to modify more parameters? (y/n)")
                    choice = input().strip().lower()
                    if choice == 'n':
                        break
                    elif choice == 'y':
                        continue

                except ValueError:
                    print("Invalid input. Please try again.")
        else:
            print("Invalid choice. Please try again.")

