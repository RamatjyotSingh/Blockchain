
# def compute_hash(pre_hash_base, nonce_bytes):
#     """
#     Computes the SHA-256 hash by appending the nonce to the precomputed hash base.

#     Parameters:
#         pre_hash_base (bytes): The precomputed part of the hash (previous_hash, name, messages, timestamp).
#         nonce_bytes (bytes): The nonce value in bytes.

#     Returns:
#         str: The hexadecimal representation of the hash.
#     """
#     hash_copy = hashlib.sha256(pre_hash_base)
#     hash_copy.update(nonce_bytes)
#     return hash_copy.hexdigest()