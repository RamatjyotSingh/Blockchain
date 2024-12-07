# **Blockchain Peer Implementation**

## **Overview**

This project implements a peer in a blockchain network. The peer participates in the network through GOSSIP protocols, synchronizes and validates the blockchain, handles mining via TCP-connected miners, and ensures consensus among peers. The system follows proof-of-work for block validation and supports efficient decentralized operations.

---

## **Features**

### **1. Peer Discovery and Network Joining**

- **GOSSIP Protocol**:
  - The peer announces its presence to the network by sending `GOSSIP` messages to known hosts and tracked peers.
  - Replies to `GOSSIP` messages with `GOSSIP-REPLY`.
  - Keeps a list of active peers, removing those inactive for over a minute.
- **Integration**:
  - GOSSIP is used as a keep-alive mechanism, sending updates every 30 seconds.
- **Code Highlights**:
  - **File**: `gossip.py`
  - **Key Methods**:
    - `handle_gossip`: Processes incoming GOSSIP messages and replies.
    - `clean_up`: Removes inactive peers from the list.
    - `keep_alive`: sends `heartbeat` messages.

---

### **2. Blockchain Synchronization**

- **Fetching Blocks**:
  - Retrieves blocks using the `GET_BLOCK` protocol from peers in a load-balanced, chunk-based manner.
  - Handles lost requests by retrying until the chain is complete.
- **Chain Validation**:
  - Validates the blockchain using proof-of-work rules, ensuring hashes, nonces, and linkages meet the required difficulty level.
- **Integration**:
  - Chain synchronization is triggered upon joining the network or during periodic consensus.
- **Code Highlights**:
  - **File**: `get_block.py`
  - **Key Methods**:
    - `send_req_to_all`: Sends `GET_BLOCK` requests to peers.
    - `recv_res`: Collects block responses.
  - **File**: `blockchain.py`
  - **Key Methods**:
    - `verify_block`: Validates individual blocks for proof-of-work and hash correctness.
    - `is_valid`: Ensures the entire chain’s integrity.
    - **File**: `test.py`
    - **Key Methods**:
      - `test_handling_recvs (lines 120-130)`: Adds newly mined blocks to the top of the chain. Each new block is verified upon addition. See the `Block` class for details.

---

### **3. Consensus Mechanism**

- **Chain Selection**:
  - Uses the `STATS` protocol to collect chain information (height and hash) from peers.
  - Selects the longest valid chain, breaking ties using hash majority.
- **Periodic Consensus**:
  - Runs a consensus process every 5 minutes or when a `CONSENSUS` message is received.
  - Updates the chain to match the majority.
- **Code Highlights**:
  - **File**: `stats.py`
  - **Key Methods**:
    - `send_req`: Sends `STATS` requests to peers.
    - `find_priority_peers`: Determines the most reliable peers for synchronization.
  - **File**: `test.py`
  - **Key Method**:
    - `test_consensus (line 96 -107)`: Coordinates the consensus process and chain updates .

---

### **4. Decentralized Mining**

- **Efficient Mining**:
  - Miners use parallel processing to find a valid nonce for proof-of-work.
  - Mining is done through a separate TCP-connected program.
  - The mined block is sent to the peer, which validates and announces it.
- **Block Announcement**:
  - Uses the `ANNOUNCE` protocol to propagate newly mined blocks to peers.
- **Code Highlights**:
  - **File**: `miner.py`
  - **Key Methods**:
    - `mine_block`: Mines a block using `multiprocessing`.
    - `report_block`: Sends the mined block back to the peer.
  - **File**: `announce.py`
  - **Key Methods**:
    - `broadcast`: Propagates mined blocks using `ANNOUNCE`.
  - **File**: `block.txt`
    - **Description**: Contains a record of some of the blocks that have been mined.

---

## **System Design**

### **Design Principles**

1. **Modular Structure**:
   - Each protocol (`GOSSIP`, `GET_BLOCK`, `STATS`, `ANNOUNCE`) is implemented in separate modules.
2. **Decentralized Operations**:
   - Supports peer-to-peer communication for synchronization and mining.
3. **Resilient Consensus**:
   - Ensures chain validity and conflict resolution during chain updates.

### **Challenges and Solutions**

1. **Lost Messages**:
   - Implemented retry mechanisms for block requests and consensus operations.
2. **Efficient Mining**:
   - Used parallel processing to optimize nonce calculations.
3. **Dynamic Peers**:
   - Regularly updates peer lists using GOSSIP and removes inactive peers.

---

## **Protocol Overview**

### **1. GOSSIP**

- Sends a JSON message to announce the peer:

  ```json
  {
    "type": "GOSSIP",
    "host": "127.0.0.1",
    "port": 8784,
    "id": "unique-id",
    "name": "Peer Name"
  }
  ```

- Replies with:

  ```json
  {
    "type": "GOSSIP_REPLY",
    "host": "127.0.0.1",
    "port": 8784,
    "name": "Peer Name"
  }
  ```

### **2. GET_BLOCK**

- Requests a block at a specific height:

  ```json
  {
    "type": "GET_BLOCK",
    "height": 5
  }
  ```

- Reply:

  ```json
  {
    "type": "GET_BLOCK_REPLY",
    "height": 5,
    "hash": "block-hash",
    "messages": ["message1", "message2"],
    "minedBy": "Miner Name",
    "nonce": "12345",
    "timestamp": 1699293749
  }
  ```

### **3. STATS**

- Request:

  ```json
  {
    "type": "STATS"
  }
  ```

- Reply:

  ```json
  {
    "type": "STATS_REPLY",
    "height": 10,
    "hash": "chain-hash"
  }
  ```

### **4. ANNOUNCE**

- Propagates newly mined blocks:

  ```json
  {
    "type": "ANNOUNCE",
    "height": 11,
    "minedBy": "Miner Name",
    "nonce": "67890",
    "messages": ["new message"],
    "hash": "block-hash",
    "timestamp": 1699293750
  }
  ```

---

## **Execution Instructions**

### **Running the Peer**

Start the peer node:

```bash
python test.py 
```

### **Running the Miner**

Connect a miner to the peer:

```bash
python miner.py --peer_host PEER_HOST --peer_port 8786 --processes NUM_PROCESS
```

---

## **File References**

### **Consensus Code**

- **File**: `test.py`
- **Description**:
  - The `test_consensus` method collects chain statistics, validates the chain, and updates the node to the longest valid chain.

### **Peer Cleanup**

- **File**: `gossip.py`
- **Description**:
  - The `clean_up` method removes peers that have been inactive for over a minute.

the assignment was rushed at last minute please go easy on me
