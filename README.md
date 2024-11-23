
# Blockchain Peer Implementation for Distributed Computing

This project is an implementation of a distributed blockchain peer, developed for a Distributed Computing course assignment. The peer communicates over a UDP network, maintains a synchronized blockchain, and ensures consensus through a proof-of-work mechanism.

## Features

- **Blockchain Creation and Validation**  

  Each block includes:
  - Miner name
  - Messages (up to 10, each ≤ 20 characters)
  - A nonce (up to 40 characters)
  - Cryptographic hash meeting a specified difficulty
  - Previous block hash (for chain validation)
  
- **Proof-of-Work Consensus**  

  The peer performs mining by finding a valid nonce to generate a hash with a specified number of leading ASCII zeroes (difficulty level).

- **Distributed Communication via UDP**  

  The peer interacts with the network using the following protocols:
  - **GOSSIP:** Announces presence and maintains a list of active peers.
  - **GET_BLOCK:** Retrieves blockchain data from other peers.
  - **STATS:** Requests and shares chain height and hash.

- **Mining Support**  

  Implements efficient mining using multithreading for parallel nonce computation.

- **Synchronization and Consensus**  

  - Maintains the longest valid chain.
  - Verifies incoming blocks before appending them to the chain.

## Requirements

- Python 3.7+
- Libraries: `hashlib`, `socket`, `json`, `concurrent.futures`, `time`, `os`

## How to Run

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/blockchain-peer.git
   cd blockchain-peer
   ```

2. Run the blockchain peer:

   ```bash
   python blockchain.py
   ```

3. Test UDP communication:
   - Example: Sending a `GOSSIP` message to the network:

     ```bash
     echo '{"type":"GOSSIP", "host":"<host>", "port":8999, "name":"MyPeer"}' | nc -u <host> <port>
     ```

## Key Components

### Blockchain (`blockchain.py`)

The `Block` class handles the creation and validation of individual blocks. Blocks are mined using a proof-of-work algorithm, ensuring the hash meets the required difficulty.

#### Key Constraints

- Messages: Max length of 20 characters.
- Blocks: Max of 10 messages.
- Nonce: String (up to 40 characters).
- Difficulty: Configurable with the `DIFFICULTY` constant (default: 8).

#### Example Block Creation

```python
block = Block("Alice", ["Hello, Bob!"], 0, "")
print(f"Block mined with hash: {block.block_hash}")
```

### Mining

The mining process uses `ThreadPoolExecutor` to compute valid hashes in parallel, significantly speeding up nonce discovery:

```python
with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    # Parallel hash computations for multiple nonces
```

### UDP Protocols

1. **GOSSIP:** Announces the peer's presence and maintains active connections.
2. **GET_BLOCK:** Requests a specific block by height from a peer.
3. **STATS:** Retrieves the height and hash of the peer's blockchain.

### Consensus

When receiving a `CONSENSUS` message or periodically, the peer:

1. Compares chain heights and hashes among peers.
2. Synchronizes with the longest valid chain.

#### File and Line Reference

- File: `blockchain.py`
- Consensus Logic: Lines **20–40** (update based on actual code location).

## Testing

### Example UDP Requests

- **Get Block:**

  ```bash
  echo '{"type":"GET_BLOCK", "height":0}' | nc -u <host> <port>
  ```

- **Gossip:**

  ```bash
  echo '{"type":"GOSSIP", "host":"<host>", "port":8999, "name":"TestPeer"}' | nc -u <host> <port>
  ```

- **Statistics:**

  ```bash
  echo '{"type":"STATS"}' | nc -u <host> <port>
  ```

## Performance Notes

- Mining time depends on difficulty (`DIFFICULTY` constant) and hardware capabilities.
- Uses multithreading to optimize nonce computation.

## Known Limitations

- The peer assumes all incoming blocks are valid; rigorous cryptographic verification is implemented but may have edge cases.
- Network latency or message loss can affect synchronization; retries are recommended.
