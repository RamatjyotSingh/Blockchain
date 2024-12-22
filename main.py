from protocol import Protocol
from peer import Peer
from request_handler import RequestHandler
import traceback

class Main:
    
    def __init__(self):
        self.protocol = Protocol()
        self.peer = Peer(self.protocol)
        self.request_handler = RequestHandler(self.protocol.socket,self.protocol.gossip,self.protocol.stats,self.protocol.get_block,self.protocol.announce,self.protocol.consensus,self.protocol.blockchain)
        
    def run(self):
        built = False

        while True:
            try:

                if not built:

                    built = self.peer.build_chain()

                self.peer.do_background_tasks()
                self.request_handler.handle()
                
            except Exception as e:
                print(f"Error: {e}")
                print(traceback.format_exc())
                continue

if __name__ == "__main__":
    main = Main()
    main.run()
