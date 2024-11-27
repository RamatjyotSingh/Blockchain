class Announce:
    def create_req(block):
        return {
            'type': 'ANNOUNCE',
            "height":block.height,
            "minedBy": block.name,
            "nonce": block.nonce,
            "messages": block.messages,
            "hash": block.hash,
            "timestamp": block.timestamp
        }