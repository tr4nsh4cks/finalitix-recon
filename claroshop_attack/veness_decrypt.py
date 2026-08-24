"""
Corrected Python implementation of Chris Veness AES-CTR (PHP port).

Key insights vs. typical failed attempts:
1. Veness derives the cipher key by AES-encrypting the password ITSELF:
     pw_bytes = first nBits/8 bytes of password
     derived  = AES_ECB(key=pw_bytes).encrypt(pw_bytes[:16])
     key      = derived + derived[:nBytes-16]   (expand to 16/24/32 bytes)
2. Ciphertext = base64( 8-byte nonce || AES-CTR keystream XOR plaintext )
   - nonce goes in counter_block[0:8]
   - block counter goes in counter_block[8:16], LITTLE-ENDIAN per 32-bit word:
       counter_block[15-c]   = (block_num >> (c*8)) & 0xff   for c in 0..3
       counter_block[11-c]   = ((block_num // 2**32) >> (c*8)) & 0xff
3. The crew key '8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA' is 33 chars — Veness at
   256 bits silently uses only the first 32 bytes.
"""
import base64

try:
    from Crypto.Cipher import AES
except ImportError:
    raise SystemExit("pip install pycryptodome")

KEY = "8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA"


def veness_derive_key(password: str, nbits: int = 256) -> bytes:
    nbytes = nbits // 8
    pw = bytes(ord(password[i]) & 0xFF for i in range(nbytes))
    derived = AES.new(pw, AES.MODE_ECB).encrypt(pw[:16])
    return derived + derived[: nbytes - 16]


def veness_decrypt(b64_ciphertext: str, password: str = KEY, nbits: int = 256) -> bytes:
    raw = base64.b64decode(b64_ciphertext)
    key = veness_derive_key(password, nbits)
    cipher = AES.new(key, AES.MODE_ECB)
    counter_block = bytearray(16)
    counter_block[:8] = raw[:8]  # nonce from first 8 bytes
    out = bytearray()
    nblocks = (len(raw) - 8 + 15) // 16
    for b in range(nblocks):
        for c in range(4):
            counter_block[15 - c] = (b >> (c * 8)) & 0xFF
        hi = b // 0x100000000
        for c in range(4):
            counter_block[11 - c] = (hi >> (c * 8)) & 0xFF
        keystream = cipher.encrypt(bytes(counter_block))
        chunk = raw[8 + b * 16 : 8 + (b + 1) * 16]
        out.extend(x ^ y for x, y in zip(chunk, keystream))
    return bytes(out)


def veness_encrypt_fixed_nonce(plaintext: bytes, password: str, nbits: int,
                               nonce_ms: int, nonce_rnd: int, nonce_sec: int) -> str:
    """Deterministic encrypt replicating Veness with a fixed nonce (test vectors)."""
    key = veness_derive_key(password, nbits)
    cipher = AES.new(key, AES.MODE_ECB)
    cb = bytearray(16)
    for i in range(2):
        cb[i] = (nonce_ms >> (i * 8)) & 0xFF
    for i in range(2):
        cb[2 + i] = (nonce_rnd >> (i * 8)) & 0xFF
    for i in range(4):
        cb[4 + i] = (nonce_sec >> (i * 8)) & 0xFF
    out = bytearray(cb[:8])
    nblocks = (len(plaintext) + 15) // 16
    for b in range(nblocks):
        for c in range(4):
            cb[15 - c] = (b >> (c * 8)) & 0xFF
            cb[11 - c] = 0
        ks = cipher.encrypt(bytes(cb))
        chunk = plaintext[b * 16 : (b + 1) * 16]
        out.extend(x ^ y for x, y in zip(chunk, ks))
    return base64.b64encode(bytes(out)).decode()


if __name__ == "__main__":
    import sys

    print(f"key length: {len(KEY)} chars")
    print(f"derived_key_256_hex={veness_derive_key(KEY, 256).hex()}")
    print(f"derived_key_128_hex={veness_derive_key(KEY, 128).hex()}")
    print(f"derived_key_192_hex={veness_derive_key(KEY, 192).hex()}")
    print()

    # Cross-validation against PHP fixed-nonce vector
    PHP_VECTOR = "AQACAAMAAAA6ChkuVNcfFrp84BeaEa5k"
    PHP_PLAIN = b"4111111111111111"
    dec = veness_decrypt(PHP_VECTOR, KEY, 256)
    print(f"[X-VALIDATE PHP vector] decrypt -> {dec!r}  {'MATCH-OK' if dec == PHP_PLAIN else 'MISMATCH-FAIL'}")

    enc = veness_encrypt_fixed_nonce(PHP_PLAIN, KEY, 256, 1, 2, 3)
    print(f"[X-VALIDATE py->php   ] encrypt -> {enc}  {'MATCH-OK' if enc == PHP_VECTOR else 'MISMATCH-FAIL'}")
    print()

    # CLI: decrypt samples passed as args at all key sizes
    for ct in sys.argv[1:]:
        print(f"sample: {ct}")
        for bits in (256, 192, 128):
            try:
                d = veness_decrypt(ct, KEY, bits)
                printable = all(32 <= x < 127 for x in d)
                print(f"  {bits}-bit -> {d!r} {'PRINTABLE' if printable else 'binary'}")
            except Exception as e:
                print(f"  {bits}-bit -> ERROR {e}")
