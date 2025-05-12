import numpy as np
from ciphers.gamma import RandGen

IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17,  9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]
IP_INV = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41,  9, 49, 17, 57, 25
]
E = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10,11,12,13,
    12,13,14,15,16,17,
    16,17,18,19,20,21,
    20,21,22,23,24,25,
    24,25,26,27,28,29,
    28,29,30,31,32,1
    ]
P = [
    16,7,20,21,
    29,12,28,17,
    1,15,23,26,
    5,18,31,10,
    2,8,24,14,
    32,27,3,9,
    19,13,30,6,
    22,11,4,25
]
PC1 = [
    57,49,41,33,25,17,9,
    1,58,50,42,34,26,18,
    10,2,59,51,43,35,27,
    19,11,3,60,52,44,36,
    63,55,47,39,31,23,15,
    7,62,54,46,38,30,22,
    14,6,61,53,45,37,29,
    21,13,5,28,20,12,4
]
PC2 = [
    14,17,11,24,1,5,
    3,28,15,6,21,10,
    23,19,12,4,26,8,
    16,7,27,20,13,2,
    41,52,31,37,47,55,
    30,40,51,45,33,48,
    44,49,39,56,34,53,
    46,42,50,36,29,32
]
SHIFT_SCHEDULE = [
    1, 1, 2, 2, 2, 2, 2, 2,
    1, 2, 2, 2, 2, 2, 2, 1
]
S_BOX = [
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7], [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8], [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0], [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13 ]],       
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10], [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5], [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15], [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9 ]],
    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8], [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1], [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7], [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12 ]],
    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15], [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9], [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4], [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14 ]],
    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9], [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6], [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14], [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3 ]],
    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11], [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8], [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6], [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13 ]],
    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1], [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6], [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2], [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12 ]],
    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7], [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2], [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8], [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11 ]]
]

def pad_pkcs5(data: bytes, block_size: int = 8) -> bytes:
    padding_len = block_size - (len(data) % block_size)
    return data + bytes([padding_len] * padding_len)

def unpad_pkcs5(padded: bytes) -> bytes:
    padding_len = padded[-1]
    if padding_len < 1 or padding_len > 8:
        raise ValueError('Некорректный паддинг')
    return padded[:-padding_len]

def permute(bits, table):
    table = np.asarray(table) - 1
    return bits[table]

def xor(bits1, bits2):
    return np.bitwise_xor(bits1, bits2)

def shift_left(bits, n):
    return np.roll(bits, -n)

def add_parity_bits(key56bits):
    key_with_parity = []
    for i in range(0, 56, 7):
        block = key56bits[i:i+7]
        parity_bit = np.uint8(0 if np.sum(block) % 2 else 1)
        key_with_parity.extend(block.tolist() + [parity_bit])
    return np.array(key_with_parity, dtype=np.uint8)

def generate_keys(key64):
    key56 = permute(key64, PC1)
    C, D = key56[:28], key56[28:]
    keys = []
    for shift in SHIFT_SCHEDULE:
        C = shift_left(C, shift)
        D = shift_left(D, shift)
        keys.append(permute(np.concatenate((C, D)), PC2))
    return keys

def sbox_substitution(bits):
    result = []
    for i in range(8):
        block = bits[i*6:(i+1)*6]
        row = (block[0] << 1) | block[5]
        col = (block[1] << 3) | (block[2] << 2) | (block[3] << 1) | block[4]
        val = S_BOX[i][row][col]
        result.extend([int(b) for b in format(val, '04b')])
    return np.array(result, dtype=np.uint8)

def f(R, K):
    return permute(sbox_substitution(xor(permute(R, E), K)), P)

def des_round(L, R, K):
    return R, xor(L, f(R, K))

def des_block_encrypt(block64, keys):
    block = permute(block64, IP)
    L, R = block[:32], block[32:]
    for K in keys:
        L, R = des_round(L, R, K)
    return permute(np.concatenate((R, L)), IP_INV)

def des_block_decrypt(block64, keys):
    return des_block_encrypt(block64, keys[::-1])

def encode(data: bytes, key):
    keys = generate_keys(key)
    data = pad_pkcs5(data)
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))

    num_blocks = len(bits) // 64
    encrypted_bits = np.empty_like(bits)

    for block_idx in range(num_blocks):
        start = block_idx * 64
        end = start + 64
        block = bits[start:end]
        encrypted_bits[start:end] = des_block_encrypt(block, keys)

    return np.packbits(encrypted_bits).tobytes()

def decode(enc_data: bytes, key):
    keys = generate_keys(key)
    bits = np.unpackbits(np.frombuffer(enc_data, dtype=np.uint8))

    num_blocks = len(bits) // 64
    decrypted_bits = np.empty_like(bits)

    for block_idx in range(num_blocks):
        start = block_idx * 64
        end = start + 64
        block = bits[start:end]
        decrypted_bits[start:end] = des_block_decrypt(block, keys)

    decrypted_bytes = np.packbits(decrypted_bits).tobytes()
    return unpad_pkcs5(decrypted_bytes)

def generate_des_key(seed, a, c, m):
    lcg = RandGen(seed=seed, a=a, c=c, m=m)
    key56 = []
    for i in range(7):
        byte = lcg.gen()
        key56.extend([int(b) for b in format(byte, '08b')])
    key56 = key56[:56]
    return add_parity_bits(np.array(key56, dtype=np.uint8))

