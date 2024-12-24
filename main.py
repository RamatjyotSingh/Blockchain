import argparse
from protocol import Protocol
from peer import Peer
from request_handler import RequestHandler
from miner_master import MinerMaster
import traceback

class Main:
    
    def __init__(self):
        self.protocol = Protocol()
        self.peer = Peer(self.protocol)
        self.miner_master = MinerMaster(self.protocol)
        
    def run(self):
        built = False

        while True:
            try:

                if not built:

                    built = self.peer.build_chain()

                self.peer.do_background_tasks()
                request_handler = RequestHandler(self.protocol.socket,self.protocol.gossip,self.protocol.stats,self.protocol.get_block,self.protocol.announce,self.protocol.consensus,self.protocol.blockchain)
                word = request_handler.handle()
               
                self.miner_master.manage_miners(word,self.protocol.gossip.known_peers)
                
                    
            except Exception as e:
                print(f"Error: {e}")
                print(traceback.format_exc())
                continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blockchain Node")
    parser.add_argument("--modify-params", action="store_true", help="Modify class-level parameters")
    args = parser.parse_args()

    main = Main()

    if args.modify_params:
        main.protocol.modify_params()

    main.run()