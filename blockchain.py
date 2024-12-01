from block import Block

class Blockchain:

    def __init__(self,protocol):

        self.chain = []
        self.protocol = protocol
        self.height = 0

    def add_block(self,block):

        self.chain.append(block)
        self.height += 1
    
    def get_block_by_height(self,height):
        return self.chain[height]

        

    