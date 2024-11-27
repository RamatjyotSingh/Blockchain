class Stats:
    def create_req():
        return {
            'type': 'STATS'
        } 
    def create_res(block):
        return {

            "type":"STATS_REPLY",
            "height":block.height,
            "hash":block.hash
            
             }