# **Blockchain Peer Implementation**

## **Overview**

This project implements a peer in a blockchain network that participates through GOSSIP protocols, synchronizes and validates the blockchain, handles mining via TCP-connected miners, and ensures consensus among peers. It employs proof-of-work for block validation, supporting efficient decentralized operations.

---

## **Features**

### **1. Peer Discovery and Network Joining**

- **GOSSIP Protocol**:
  - Announces the peer’s presence to the network by sending `GOSSIP` messages to known hosts and tracked peers.
  - Replies to `GOSSIP` messages with `GOSSIP-REPLY`.
  - Maintains a list of active peers, removing those inactive for over a minute.
- **Integration**:
  - GOSSIP serves as a keep-alive mechanism, sending updates every 30 seconds.
- **Code Highlights**:
  - **File**: `gossip.py`
  - **Key Methods**:
    - `handle_gossip`: Processes incoming GOSSIP messages and replies.
    - `clean_up`: Removes inactive peers from the list.
    - `keep_alive`: Sends periodic heartbeat messages.

---

### **2. Blockchain Synchronization**

- **Fetching Blocks**:
  - Retrieves blocks using the `GET_BLOCK` protocol from peers in a load-balanced, chunk-based manner.
  - Implements retry mechanisms for handling lost requests.
- **Chain Validation**:
  - Validates the blockchain using proof-of-work rules, ensuring hashes, nonces, and linkages meet the required difficulty level.
- **Integration**:
  - Synchronization is triggered upon network joining or during periodic consensus.
- **Code Highlights**:
  - **File**: `get_block.py`
  - **Key Methods**:
    - `send_req_to_all`: Sends `GET_BLOCK` requests to peers.
    - `recv_res`: Collects block responses.
  - **File**: `blockchain.py`
  - **Key Methods**:
    - `verify_block`: Validates individual blocks for proof-of-work and hash correctness.
    - `is_valid`: Ensures the integrity of the entire chain.

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
    - `find_priority_peers`: Identifies the most reliable peers for synchronization.

---

### **4. Decentralized Mining**

- **Efficient Mining**:
  - Miners use parallel processing to find a valid nonce for proof-of-work.
  - Mining is conducted through a separate TCP-connected program.
  - The peer validates and announces mined blocks.
- **Block Announcement**:
  - Uses the `ANNOUNCE` protocol to propagate newly mined blocks to peers.
- **Code Highlights**:
  - **File**: `miner.py`
  - **Key Methods**:
    - `mine_block`: Mines a block.
    - `report_block`: Sends the mined block to the peer.
  - **File**: `announce.py`
  - **Key Methods**:
    - `broadcast`: Propagates mined blocks using `ANNOUNCE`.

---

## **System Design**

### **Design Principles**

1. **Modular Structure**:
   - Each protocol (`GOSSIP`, `GET_BLOCK`, `STATS`, `ANNOUNCE`) is implemented in separate modules.
2. **Decentralized Operations**:
   - Supports peer-to-peer communication for synchronization and mining.
3. **Resilient Consensus**:
   - Ensures chain validity and resolves conflicts during updates.

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

- Announces the peer with the following message:

  ```json
  {
    "type": "GOSSIP",
    "host": "127.0.0.1",
    "port": 8784,
    "id": "unique-id",
    "name": "Peer Name"
  }
  ```

- Reply:

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
    "timestamp": 1699293759
  }
  ```

---

## **Execution Instructions**

### **Running the Peer**

Start the peer node:

```bash
python main.py
```

### **Running the Miner**

Connect a miner to the peer:

```bash
python miner.py --peer_host PEER_HOST --peer_port 8785
```

### **Changing Parameters**

Modify protocol parameters using the `--modify-params` command-line argument. This allows you to adjust the blockchain node’s behavior.

#### **Example Usage**

```bash
python main.py --modify-params
```

#### **Adjustable Parameters**

- **NAME**: Node name
- **MAX_PEERS**: Maximum number of peers to track
- **CLEAN_UP_INTERVAL**: Interval (seconds) to clean up peers
- **KEEP_ALIVE_INTERVAL**: Interval (seconds) for keep-alive messages
- **DIFFICULTY**: Block difficulty level
- **WELL_KNOWN_PEERS**: List of well-known peers
- **CHUNK_SIZE**: Block chunk size to receive from peers
- **RETRY_LIMIT**: Retry attempts before giving up
- **CONSENSUS_INTERVAL**: Seconds to wait before running consensus
- **TCPPort**: Port for miners

Follow the prompts to update parameter values.

---

## **File References**

### **Consensus Code**

- **File**: `protocol.py`
- **Description**:
  - `init_consensus`: Initializes the consensus module.
  - `announce_block`: Announces newly mined blocks to peers.

### **Peer Cleanup**

- **File**: `gossip.py`
- **Description**:
  - `clean_up`: Removes peers inactive for over a minute.
