#include <stdio.h>
#include <stdint.h>
#include <cuda_runtime.h>
#include <string.h>
#include <stdbool.h>

#define SHA256_BLOCK_SIZE 32
#define MAX_NONCE 0xFFFFFFFF

// Define missing macros
#define ROTRIGHT(word, bits) (((word) >> (bits)) | ((word) << (32 - (bits))))
#define CH(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))

// SHA-256 constants
__device__ __constant__ uint32_t k[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

// Atomic flag to signal found nonce
__device__ bool found = false;

// Device-compatible strlen function
__device__ size_t device_strlen(const char* str) {
    size_t len = 0;
    while (str[len] != '\0') {
        len++;
    }
    return len;
}

__device__ void sha256_transform(uint32_t state[8], const uint8_t data[64]) {
    uint32_t a, b, c, d, e, f, g, h, t1, t2, m[64];

    // Parse first 16 words
    for (int i = 0, j = 0; i < 16; ++i, j += 4)
        m[i] = (data[j] << 24) | (data[j + 1] << 16) | (data[j + 2] << 8) | (data[j + 3]);

    // Extend the first 16 words into the remaining 48 words
    for (int i = 16; i < 64; ++i)
        m[i] = ROTRIGHT(m[i - 15], 7) ^ ROTRIGHT(m[i - 15], 18) ^ (m[i - 15] >> 3) +
               m[i - 7] + ROTRIGHT(m[i - 2], 17) ^ ROTRIGHT(m[i - 2], 19) ^ (m[i - 2] >> 10) +
               m[i - 16];

    a = state[0];
    b = state[1];
    c = state[2];
    d = state[3];
    e = state[4];
    f = state[5];
    g = state[6];
    h = state[7];

    for (int i = 0; i < 64; ++i) {
        t1 = h + (ROTRIGHT(e, 6) ^ ROTRIGHT(e, 11) ^ ROTRIGHT(e, 25)) +
             CH(e, f, g) + k[i] + m[i];
        t2 = (ROTRIGHT(a, 2) ^ ROTRIGHT(a, 13) ^ ROTRIGHT(a, 22)) +
             MAJ(a, b, c);
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }

    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
    state[4] += e;
    state[5] += f;
    state[6] += g;
    state[7] += h;
}

__device__ void sha256_init(uint32_t state[8]) {
    state[0] = 0x6a09e667;
    state[1] = 0xbb67ae85;
    state[2] = 0x3c6ef372;
    state[3] = 0xa54ff53a;
    state[4] = 0x510e527f;
    state[5] = 0x9b05688c;
    state[6] = 0x1f83d9ab;
    state[7] = 0x5be0cd19;
}

__device__ void sha256_final(uint32_t state[8], uint8_t hash[32]) {
    for (int i = 0; i < 8; ++i) {
        hash[i * 4]     = (state[i] >> 24) & 0xff;
        hash[i * 4 + 1] = (state[i] >> 16) & 0xff;
        hash[i * 4 + 2] = (state[i] >> 8) & 0xff;
        hash[i * 4 + 3] = state[i] & 0xff;
    }
}

__device__ void sha256_compute(uint32_t state[8], const uint8_t data[], size_t len) {
    size_t i;
    uint8_t block[64];
    size_t processed = 0;

    while (processed + 64 <= len) {
        memcpy(block, data + processed, 64);
        sha256_transform(state, block);
        processed += 64;
    }

    // Handle remaining data and padding (simplified for nonce hashing)
    memset(block, 0, 64);
    memcpy(block, data + processed, len - processed);
    // Primitively handle padding (not complete)
    sha256_transform(state, block);
}

__global__ void mineBlockKernel(const char* input, size_t input_len, uint32_t* nonce, uint8_t* hash, uint32_t difficulty) {
    uint32_t idx = blockIdx.x * blockDim.x + threadIdx.x;
    uint32_t step = gridDim.x * blockDim.x;
    uint32_t localNonce = idx;

    uint32_t state[8];
    uint8_t localHash[32];

    // Initialize SHA-256 state
    sha256_init(state);

    // Precompute the static part of the data (input)
    // Assuming input is already properly formatted for hashing
    // Append nonce to input
    uint8_t data[64];
    memset(data, 0, 64);
    size_t copy_len = input_len < 64 ? input_len : 64;
    memcpy(data, input, copy_len);

    while (!found && localNonce < MAX_NONCE) {
        // Copy nonce into data
        memcpy(data + copy_len, &localNonce, sizeof(localNonce));

        // Compute SHA-256
        uint32_t temp_state[8];
        memcpy(temp_state, state, sizeof(uint32_t) * 8);
        sha256_compute(temp_state, data, copy_len + sizeof(localNonce));
        sha256_final(temp_state, localHash);

        // Check difficulty
        bool isValid = true;
        for (uint32_t i = 0; i < difficulty; ++i) {
            if (localHash[i] != 0) {
                isValid = false;
                break;
            }
        }

        if (isValid) {
            if (!atomicExch((int*)&found, 1)) { // Set found to true atomically
                *nonce = localNonce;
                memcpy(hash, localHash, SHA256_BLOCK_SIZE);
            }
            break;
        }

        localNonce += step;
    }
}

extern "C" bool mineBlock(const char* input, size_t input_len, uint8_t* output_hash, uint32_t* output_nonce, uint32_t difficulty) {
    char* d_input;
    uint8_t* d_hash;
    uint32_t* d_nonce;

    // Allocate device memory
    cudaError_t err;
    err = cudaMalloc((void**)&d_input, input_len);
    if (err != cudaSuccess) {
        printf("CUDA malloc failed for input: %s\n", cudaGetErrorString(err));
        return false;
    }

    err = cudaMalloc((void**)&d_hash, SHA256_BLOCK_SIZE);
    if (err != cudaSuccess) {
        printf("CUDA malloc failed for hash: %s\n", cudaGetErrorString(err));
        cudaFree(d_input);
        return false;
    }

    err = cudaMalloc((void**)&d_nonce, sizeof(uint32_t));
    if (err != cudaSuccess) {
        printf("CUDA malloc failed for nonce: %s\n", cudaGetErrorString(err));
        cudaFree(d_input);
        cudaFree(d_hash);
        return false;
    }

    // Initialize 'found' flag to false
    bool h_found = false;
    err = cudaMemcpyToSymbol(found, &h_found, sizeof(bool));
    if (err != cudaSuccess) {
        printf("CUDA memcpy to symbol failed: %s\n", cudaGetErrorString(err));
        cudaFree(d_input);
        cudaFree(d_hash);
        cudaFree(d_nonce);
        return false;
    }

    // Copy input data to device
    err = cudaMemcpy(d_input, input, input_len, cudaMemcpyHostToDevice);
    if (err != cudaSuccess) {
        printf("CUDA memcpy failed for input: %s\n", cudaGetErrorString(err));
        cudaFree(d_input);
        cudaFree(d_hash);
        cudaFree(d_nonce);
        return false;
    }

    // Kernel launch configuration
    int blockSize = 256;
    int numBlocks = 256; // Adjust based on GPU's capability

    // Launch the mining kernel
    mineBlockKernel<<<numBlocks, blockSize>>>(d_input, input_len, d_nonce, d_hash, difficulty);

    // Wait for GPU to finish
    err = cudaDeviceSynchronize();
    if (err != cudaSuccess) {
        printf("CUDA kernel failed: %s\n", cudaGetErrorString(err));
        cudaFree(d_input);
        cudaFree(d_hash);
        cudaFree(d_nonce);
        return false;
    }

    // Check if a nonce was found
    err = cudaMemcpy(output_nonce, d_nonce, sizeof(uint32_t), cudaMemcpyDeviceToHost);
    if (err != cudaSuccess) {
        printf("CUDA memcpy failed for nonce: %s\n", cudaGetErrorString(err));
        cudaFree(d_input);
        cudaFree(d_hash);
        cudaFree(d_nonce);
        return false;
    }

    // If a nonce was found, copy the hash
    if (*output_nonce != 0) {
        err = cudaMemcpy(output_hash, d_hash, SHA256_BLOCK_SIZE, cudaMemcpyDeviceToHost);
        if (err != cudaSuccess) {
            printf("CUDA memcpy failed for hash: %s\n", cudaGetErrorString(err));
            cudaFree(d_input);
            cudaFree(d_hash);
            cudaFree(d_nonce);
            return false;
        }
    }

    // Free device memory
    cudaFree(d_input);
    cudaFree(d_hash);
    cudaFree(d_nonce);

    // Return whether a valid nonce was found
    return (*output_nonce != 0);
}