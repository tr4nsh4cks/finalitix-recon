# Descifrar datostarjeta - Chris Veness AES-CTR correcto
# Referencia: https://www.movable-type.co.uk/scripts/aes.js
import base64, sys

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

def key_expansion(key):
    """AES key expansion. key is list of bytes (16/24/32)"""
    nBytes = len(key)
    Nk = nBytes // 4
    Nr = Nk + 6
    w = [list(key[i*4:(i+1)*4]) for i in range(Nk)]
    for i in range(Nk, 4 * (Nr + 1)):
        temp = list(w[-1])
        if i % Nk == 0:
            temp = [SBOX[temp[1]] ^ RCON[i//Nk], SBOX[temp[2]], SBOX[temp[3]], SBOX[temp[0]]]
        elif Nk > 6 and i % Nk == 4:
            temp = [SBOX[b] for b in temp]
        w.append([w[i-Nk][j] ^ temp[j] for j in range(4)])
    return w, Nr

def aes_encrypt_block(inp, w, Nr):
    """Encrypt 16-byte block. inp: list of 16 bytes, w: key schedule"""
    s = [[0]*4 for _ in range(4)]
    for r in range(4):
        for c in range(4):
            s[r][c] = inp[r + 4*c]
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
        if rnd < Nr:
            # MixColumns
            for c in range(4):
                s0,s1,s2,s3 = s[0][c],s[1][c],s[2][c],s[3][c]
                s[0][c] = xtime(s0)^xtime(s1)^s1^s2^s3
                s[1][c] = s0^xtime(s1)^xtime(s2)^s2^s3
                s[2][c] = s0^s1^xtime(s2)^xtime(s3)^s3
                s[3][c] = xtime(s0)^s0^s1^s2^xtime(s3)
        # AddRoundKey
        for r in range(4):
            for c in range(4):
                s[r][c] ^= w[rnd*4 + c][r]
    return [s[r][c] for c in range(4) for r in range(4)]

def veness_derive_key(password, nBits=256):
    """Chris Veness key derivation for AES-CTR:
    1. pwBytes = first nBits/8 char codes of password
    2. key16 = AES_encrypt(pwBytes[0..15], keyExpansion(pwBytes))
    3. For AES-256: actual_key = key16 + key16 (32 bytes)
    """
    nBytes = nBits // 8
    pwBytes = [ord(c) & 0xff for c in password]
    # Pad to nBytes if needed
    if len(pwBytes) < nBytes:
        pwBytes = pwBytes + [0] * (nBytes - len(pwBytes))
    else:
        pwBytes = pwBytes[:nBytes]
    
    # Step 1: keyExpansion of pwBytes (32 bytes for AES-256)
    w_pw, Nr_pw = key_expansion(pwBytes)
    
    # Step 2: AES cipher of first 16 bytes of pwBytes
    key16 = aes_encrypt_block(pwBytes[:16], w_pw, Nr_pw)
    
    # Step 3: Build actual key (double for AES-256)
    actual_key = key16 + key16[:nBytes - 16]
    
    # Step 4: Key schedule for actual key
    w_final, Nr_final = key_expansion(actual_key)
    
    return w_final, Nr_final

def veness_aes_ctr_decrypt(ciphertext_b64, password, nBits=256):
    """Chris Veness AES-CTR decryption
    
    Ciphertext format (after Base64 + unescape(encodeURIComponent(...))):
    - First 8 bytes: nonce (counterBlock[0..7])
    - Remaining bytes: ciphertext XOR keystream
    
    UTF-8 consideration: the output goes through encodeURIComponent which
    expands chars ≥ 128 to multi-byte UTF-8. So we need to decode the
    Base64 bytes as UTF-8 to get the original char codes.
    """
    try:
        ct = ciphertext_b64.strip()
        pad = len(ct) % 4
        if pad:
            ct += '=' * (4 - pad)
        raw_bytes = base64.b64decode(ct)
    except Exception as e:
        return f"B64_ERR: {e}"
    
    # Try to decode as UTF-8 to get original char codes
    try:
        chars = raw_bytes.decode('utf-8')
        char_codes = [ord(c) for c in chars]
    except:
        # Fallback: treat as raw bytes
        char_codes = list(raw_bytes)
    
    if len(char_codes) < 8:
        return "TOO_SHORT"
    
    # Extract nonce (first 8 chars → counterBlock bytes 0-7)
    nonce = char_codes[:8]
    cipher_chars = char_codes[8:]
    
    if not cipher_chars:
        return "NO_CIPHERTEXT"
    
    # Build key schedule
    w, Nr = veness_derive_key(password, nBits)
    
    # CTR decryption
    block_size = 16  # bytes
    plain_chars = []
    n_blocks = (len(cipher_chars) + block_size - 1) // block_size
    
    for b in range(n_blocks):
        # Reconstruct counter block
        counter_block = list(nonce) + [0]*8
        # Set counter (block number)
        # counterBlock[15-c] = (b >> c*8) & 0xff for c in 0..3
        for c in range(4):
            counter_block[15 - c] = (b >> (c * 8)) & 0xff
        # counterBlock[11-c] = (b // 2^32 >> c*8) for c in 0..3 → 0 for small b
        for c in range(4):
            counter_block[11 - c] = 0
        
        # Encrypt counter block
        keystream = aes_encrypt_block(counter_block, w, Nr)
        
        block_start = b * block_size
        block_end = min(block_start + block_size, len(cipher_chars))
        for i in range(block_end - block_start):
            plain_chars.append(cipher_chars[block_start + i] ^ keystream[i])
    
    # Decode plain_chars as char codes → string
    # In Veness, plaintext is stored as JS char codes (0-65535 range typically)
    try:
        # Convert char codes back to bytes, then decode as UTF-8
        plain_bytes = bytes(c & 0xff for c in plain_chars)
        return plain_bytes.decode('utf-8')
    except:
        try:
            return bytes(c & 0xff for c in plain_chars).decode('latin-1')
        except:
            return repr(bytes(c & 0xff for c in plain_chars))


# ==================== TEST ====================
LLAVE_TDC_PROD = '8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA'

# Known card numbers from pedidos (raw, un-encrypted) for validation
# These are from the 16-digit PAN entries in pedidos:
# id=43006, tipo=Mastercard, numero=4415457908567699, cliente=56594, mes=05, ao=15

# All sample encrypted values from datostarjeta
samples = [
    (1, 'visa', 'vHPKSjAwMDD/opBAQngTntm38mQ/amIA', 'Juan M Gonzalez Nava'),
    (2, 'mastercard', 'vHPKSlhYWFgS9uhlteyENDBkIL9WWKAb', 'Juan M Gonzalez Nava'),
    (3, 'Visa', 'vHPKSnZ2dnZsMXuSgB4=', '546 546 54'),
    (4, 'Visa', 'vHPKSpycnJwpwpeW2VxRMnI=', '654 654 654'),
    (411715, 'Amex', 'eLPSVaOjo6NkY4jy+Nafepcz2JgypSA=', 'ALEJANDRA MAYA PARRILLA'),
    (411714, 'Mastercard', 'GK/SVURERESHXY4b7Bb6bWVMZ8igURvl', 'alejandro cruz'),
    (411711, 'Visa', 'EKfSVSAgICBGEwGp4rpq5TsHuYWeVZED', 'katytc'),
]

print("=== VENESS AES-CTR Decrypt con LLAVE_TDC_PROD ===")
for (id_, tipo, enc, nombre) in samples:
    result = veness_aes_ctr_decrypt(enc, LLAVE_TDC_PROD)
    # Analyze result
    is_numeric = all(c in '0123456789 -' for c in result.strip())
    print(f"id={id_} tipo={tipo} nombre={nombre}")
    print(f"  enc ({len(enc)}): {enc}")
    print(f"  dec ({len(result)}): {result!r}")
    print(f"  looks_numeric: {is_numeric}")
    print()

# Print raw bytes of nonce to understand structure
print("\n=== RAW BYTES ANALYSIS ===")
for enc_b64 in ['vHPKSjAwMDD/opBAQngTntm38mQ/amIA', 'vHPKSlhYWFgS9uhlteyENDBkIL9WWKAb']:
    raw = base64.b64decode(enc_b64 + '==')
    print(f"enc: {enc_b64}")
    print(f"  raw_hex: {raw.hex()}")
    print(f"  len: {len(raw)}")
    try:
        as_utf8 = raw.decode('utf-8')
        print(f"  as_utf8 char_codes: {[ord(c) for c in as_utf8]}")
    except Exception as e:
        print(f"  utf8_decode_err: {e}")
    try:
        as_latin = raw.decode('latin-1')
        print(f"  as_latin char_codes: {[ord(c) for c in as_latin]}")
    except:
        pass
    print()
