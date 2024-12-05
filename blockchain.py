from block import Block

class Blockchain:

    def __init__(self,total_height):

        self.chain = []
        self.init_chain(total_height)
        # self.create_genesis_block()
        self.curr_height = 0

        self.total_height = total_height

    def add_block(self, block, height):
        if self.verify_block(block, height):
            self.chain[height] = block
        else:
            print("Block verification failed.")
    
    def verify_block(self, block, height):
        if height > 0:
            prev_block = self.get_block_by_height(height-1)
            if not prev_block or block.previous_hash != prev_block.hash:
                return False
        return block.verify_self()
    
    def get_block_by_height(self, height):
        if 0 <= height < len(self.chain):
            return self.chain[height]
        else:
            print(f"Height {height} is out of bounds.")
            return None

    def init_chain(self,total_height):

        for i in range(total_height):
            self.chain.append(None)

    def get_curr_height(self):
        return self.curr_height
    
    def is_chain_filled(self,):

        for block in self.chain:
            if block is None:
                return False
        return True
    
    def is_chunk_filled(self, chunk_size):
        height = self.get_curr_height()
        end_height = height + chunk_size
        end_height = min(end_height, self.total_height)  # Prevent overflow
        
        for i in range(height + 1, end_height + 1):
            if i >= len(self.chain) or self.chain[i] is None:
                return False
        
        return True
    
    def increment_height_by_chunk(self,chunk_size):

        if self.is_chunk_filled(chunk_size):
            self.curr_height += chunk_size
        

        
    def create_block(self,hash,height,messages,mined_by,nonce,timestamp):

        if self.chain[height] is not None:
            return None
        
        if height == 0:
            prev_hash = None
        else:
            
            prev_hash = self.chain[height-1].hash


        block = Block(mined_by,messages,height,prev_hash,hash,nonce,timestamp)

        return block
        
    def get_chain(self):
        return self.chain
            
        
#unnecessary genesis block creation
    def create_genesis_block(self):

        genesis_block = Block(
               
                hash='2483cc5c0d2fdbeeba3c942bde825270f345b2e9cd28f22d12ba347300000000',
                height=0,
                messages=['3010 rocks',
                          'Warning:',
                          'Procrastinators',
                          'will be sent back',
                          'in time to start',
                          'early.'],
                previous_hash=None,
                minedBy='Prof!',
                nonce='7965175207940',
                timestamp=1699293749
            )

        self.chain.append(genesis_block)
        self.curr_height = 0
        print("Genesis block created:")
        print(genesis_block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            if not self.verify_block(self.chain[i], i):
                return False
        return True