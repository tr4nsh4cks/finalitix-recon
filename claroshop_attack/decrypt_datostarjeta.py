# Descifrar datostarjeta con LLAVE_TDC_PROD (AES-256-CTR, Chris Veness)
# Implementacion Python del algoritmo Veness AES-CTR
import base64, sys

# AES S-Box and constants
SBOX = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16,
]

RCON = [0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36]

def xtime(a):
    return ((a << 1) ^ 0x1b) & 0xff if a & 0x80 else (a << 1) & 0xff

def mix_columns(s):
    # Mix columns for AES
    for c in range(4):
        s0 = s[0][c]; s1 = s[1][c]; s2 = s[2][c]; s3 = s[3][c]
        s[0][c] = xtime(s0) ^ xtime(s1) ^ s1 ^ s2 ^ s3
        s[1][c] = s0 ^ xtime(s1) ^ xtime(s2) ^ s2 ^ s3
        s[2][c] = s0 ^ s1 ^ xtime(s2) ^ xtime(s3) ^ s3
        s[3][c] = xtime(s0) ^ s0 ^ s1 ^ s2 ^ xtime(s3)

def aes_key_expansion(key, nBits):
    # nBits = 256 → Nk = 8, Nr = 14
    Nk = nBits // 32
    w = [[0]*4 for _ in range(Nb * (14 + 1) if nBits == 256 else Nb * (11 + 1) if nBits == 128 else Nb * (13 + 1))]
    return w

Nb = 4

def aes_cipher(inp, w, nRounds):
    # inp: list of 16 bytes
    # w: expanded key words
    # Returns 16 bytes
    s = [[inp[r + 4*c] for c in range(4)] for r in range(4)]
    # AddRoundKey 0
    for r in range(4):
        for c in range(4):
            s[r][c] ^= w[c][r]
    for rnd in range(1, nRounds):
        # SubBytes
        for r in range(4):
            for c in range(4):
                s[r][c] = SBOX[s[r][c]]
        # ShiftRows
        s[1] = [s[1][1], s[1][2], s[1][3], s[1][0]]
        s[2] = [s[2][2], s[2][3], s[2][0], s[2][1]]
        s[3] = [s[3][3], s[3][0], s[3][1], s[3][2]]
        # MixColumns (not in last round)
        if rnd < nRounds:
            mix_columns(s)
        # AddRoundKey
        for r in range(4):
            for c in range(4):
                s[r][c] ^= w[rnd*Nb + c][r]
    # Last round
    for r in range(4):
        for c in range(4):
            s[r][c] = SBOX[s[r][c]]
    s[1] = [s[1][1], s[1][2], s[1][3], s[1][0]]
    s[2] = [s[2][2], s[2][3], s[2][0], s[2][1]]
    s[3] = [s[3][3], s[3][0], s[3][1], s[3][2]]
    for r in range(4):
        for c in range(4):
            s[r][c] ^= w[nRounds*Nb + c][r]
    
    return [s[r][c] for c in range(4) for r in range(4)]


def aes_key_expansion_full(password, nBits):
    # Chris Veness: key from password char codes (first 32 bytes for AES-256)
    key = [ord(c) & 0xff for c in password]
    # Pad or truncate to nBits/8 bytes
    nBytes = nBits // 8
    if len(key) > nBytes:
        key = key[:nBytes]
    else:
        key = key + [0] * (nBytes - len(key))
    
    Nk = nBits // 32
    Nr = Nk + 6  # 14 for AES-256
    
    # w[i] = word (4 bytes)
    w = [None] * (Nb * (Nr + 1))
    for i in range(Nk):
        w[i] = [key[4*i], key[4*i+1], key[4*i+2], key[4*i+3]]
    
    for i in range(Nk, Nb * (Nr + 1)):
        temp = list(w[i-1])
        if i % Nk == 0:
            temp = [SBOX[temp[1]] ^ RCON[i//Nk], SBOX[temp[2]], SBOX[temp[3]], SBOX[temp[0]]]
        elif Nk > 6 and i % Nk == 4:
            temp = [SBOX[b] for b in temp]
        w[i] = [w[i-Nk][j] ^ temp[j] for j in range(4)]
    
    return w, Nr


def aes_encrypt_block(inp_bytes, w, Nr):
    """Encrypt a single 16-byte block using AES"""
    s = [[0]*4 for _ in range(4)]
    for r in range(4):
        for c in range(4):
            s[r][c] = inp_bytes[r + 4*c]
    
    # AddRoundKey 0
    for r in range(4):
        for c in range(4):
            s[r][c] ^= w[c][r]
    
    for rnd in range(1, Nr + 1):
        # SubBytes
        for r in range(4):
            for c in range(4):
                s[r][c] = SBOX[s[r][c]]
        # ShiftRows
        s[1] = [s[1][1], s[1][2], s[1][3], s[1][0]]
        s[2] = [s[2][2], s[2][3], s[2][0], s[2][1]]
        s[3] = [s[3][3], s[3][0], s[3][1], s[3][2]]
        # MixColumns (not in last round)
        if rnd < Nr:
            for c in range(4):
                s0, s1, s2, s3 = s[0][c], s[1][c], s[2][c], s[3][c]
                s[0][c] = xtime(s0) ^ xtime(s1) ^ s1 ^ s2 ^ s3
                s[1][c] = s0 ^ xtime(s1) ^ xtime(s2) ^ s2 ^ s3
                s[2][c] = s0 ^ s1 ^ xtime(s2) ^ xtime(s3) ^ s3
                s[3][c] = xtime(s0) ^ s0 ^ s1 ^ s2 ^ xtime(s3)
        # AddRoundKey
        for r in range(4):
            for c in range(4):
                s[r][c] ^= w[rnd * Nb + c][r]
    
    return [s[r][c] for c in range(4) for r in range(4)]


def veness_aes_ctr_decrypt(ciphertext_b64, password, nBits=256):
    """Chris Veness AES-CTR decryption"""
    try:
        # Add padding if needed
        ct = ciphertext_b64.strip()
        pad = len(ct) % 4
        if pad:
            ct += '=' * (4 - pad)
        cipher_bytes = list(base64.b64decode(ct))
    except Exception as e:
        return f"B64_ERR: {e}"
    
    w, Nr = aes_key_expansion_full(password, nBits)
    
    # CTR mode: counter starts at 0 (all zeros)
    counter_block = [0] * 16
    
    plain = []
    n_blocks = (len(cipher_bytes) + 15) // 16
    
    for b in range(n_blocks):
        # Encrypt counter block to get keystream
        cipher_counter = aes_encrypt_block(counter_block, w, Nr)
        
        # XOR with ciphertext to get plaintext
        block_start = b * 16
        block_end = min(block_start + 16, len(cipher_bytes))
        for i in range(block_end - block_start):
            plain.append(cipher_bytes[block_start + i] ^ cipher_counter[i])
        
        # Increment counter (big-endian)
        for i in range(15, -1, -1):
            counter_block[i] = (counter_block[i] + 1) & 0xff
            if counter_block[i] != 0:
                break
    
    try:
        return bytes(plain).decode('utf-8')
    except:
        return bytes(plain).decode('latin-1')


# Test with known samples from DB
LLAVE_TDC_PROD = '8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA'

# Sample encrypted card numbers from datostarjeta
samples = [
    # (id, tipo, encrypted_numero)
    (1, 'visa', 'vHPKSjAwMDD/opBAQngTntm38mQ/amIA'),
    (2, 'mastercard', 'vHPKSlhYWFgS9uhlteyENDBkIL9WWKAb'),
    (3, 'Visa', 'vHPKSnZ2dnZsMXuSgB4='),
    (4, 'Visa', 'vHPKSpycnJwpwpeW2VxRMnI='),
    (5, 'Visa', 'vHPKSre3t7e/dFCL3mU='),
    (6, 'Visa', 'vHPKStXV1dWiIuMjgXrAlg=='),
    (7, 'Visa', 'vHPKSgwMDAz+AulRwn/5EF64'),
    (411715, 'Amex', 'eLPSVaOjo6NkY4jy+Nafepcz2JgypSA='),
    (411714, 'Mastercard', 'GK/SVURERESHXY4b7Bb6bWVMZ8igURvl'),
    (411711, 'Visa', 'EKfSVSAgICBGEwGp4rpq5TsHuYWeVZED'),
]

print("=== DECRYPT datostarjeta con LLAVE_TDC_PROD ===")
print(f"Key: {LLAVE_TDC_PROD}")
print()

for (id_, tipo, enc) in samples:
    result = veness_aes_ctr_decrypt(enc, LLAVE_TDC_PROD, 256)
    # Check if it looks like a card number (digits/spaces)
    is_card = any(c.isdigit() for c in result) and len(result) <= 30
    print(f"id={id_} tipo={tipo}")
    print(f"  enc: {enc}")
    print(f"  dec: {result!r}")
    print(f"  card-like: {is_card}")
    print()

# Also test with LLAVE_TDC_DEV
LLAVE_TDC_DEV = 'K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4'
print("\n=== DECRYPT con LLAVE_TDC_DEV ===")
for (id_, tipo, enc) in samples[:3]:
    result = veness_aes_ctr_decrypt(enc, LLAVE_TDC_DEV, 256)
    print(f"id={id_}: {result!r}")

print("\n=== FIN ===")