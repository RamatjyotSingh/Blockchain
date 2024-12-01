import json


class GetBlock:

    def __init__(self, blockchain,socket):
        self.blockchain = blockchain
        self.socket = socket

    def create_req(self,height):

        return{
            "type":"GET_BLOCK",
            "height":height
        }
    
    def create_res(self,height):

        block = self.blockchain.get_block_by_height(height)

        if block is None:
            return {
                "type": "GET_BLOCK_REPLY",
                "hash": None,
                "height": None,
                "messages": None,
                "mined_by": None,
                "nonce": None,
                "timestamp": None
            }
        return {
            "type": "GET_BLOCK_REPLY",
            "hash": block.hash,
            "height": block.height,
            "messages": block.messages,
            "mined_by": block.name,
            "nonce": block.nonce,
            "timestamp": block.timestamp
        }
    
    def send_req(self,peers,height):

        for peer in peers:
            host = peer['host']
            port = peer['port']
            req = self.create_req(height)
            self.socket.sendto(json.dumps(req).encode(), (host, port))

    def recv_res(self):
        self.socket.settimeout(5)
        block_replies = []
        other_replies = []

        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                reply = json.loads(data)

                if reply['type'] == 'GET_BLOCK_REPLY':

                    block_replies.append((reply,addr))

                else :

                    other_replies.append((reply,addr))
            except TimeoutError:
                break

        return block_replies,other_replies

    def execute(self,height):

        peers = self.blockchain.get_peers()
        self.send_req(peers,height)
        block_replies,other_replies = self.recv_res()

        for reply,addr in block_replies:

            assert reply['type'] == 'GET_BLOCK_REPLY'
            assert height == reply['height']

            block = self.blockchain.create_block(reply['hash'],reply['height'],reply['messages'],reply['mined_by'],reply['nonce'],reply['timestamp'])

            if block is None:
                continue
            # verify block should be in create_block()

            self.blockchain.add_block(block)
            # verify new link  should be in add_block()

        return other_replies