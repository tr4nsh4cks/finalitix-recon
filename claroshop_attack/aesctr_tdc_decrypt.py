#!/usr/bin/env python3
# aesctr_tdc_decrypt.py — ClaroShop tienda.datostarjeta numero/mes decrypter
# Port of tienda\Librerias\Encrypt\AesCtr (AES-256-CTR, Chris Veness style)
# Key: llave_encriptacion_tdc = K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4 (first 32 bytes used)
#
# PHP key derivation (AesCtr::encrypt/decrypt):
#   pwBytes = first nBits/8 bytes of password            -> 32 bytes for 256
#   k1      = Aes::cipher(pwBytes, keyExpansion(pwBytes)) -> AES-256 ECB encrypt of pwBytes[0:16] under key pwBytes
#   key     = k1 || k1[0 : nBytes-16]                     -> k1 duplicated = 32 bytes
# CTR block: 8-byte nonce (prepended to ciphertext) || 4 zero bytes || 32-bit BE block counter
#   -> equivalent to pycryptodome AES.MODE_CTR with nonce=ct[0:8], initial_value=0
import base64, sys, json
from Crypto.Cipher import AES

KEY = b'K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4'

def _derive_key(password: bytes, nbits: int = 256) -> bytes:
    nbytes = nbits // 8
    pw = password[:nbytes]
    k1 = AES.new(pw, AES.MODE_ECB).encrypt(pw[:16])
    return k1 + k1[:nbytes - 16]

def decrypt(b64: str, password: bytes = KEY) -> str:
    raw = base64.b64decode(b64)
    nonce, body = raw[:8], raw[8:]
    return AES.new(_derive_key(password), AES.MODE_CTR, nonce=nonce, initial_value=0).decrypt(body).decode('utf-8', 'replace')

def encrypt(plain: str, password: bytes = KEY) -> str:
    import os, struct
    nonce = os.urandom(8)  # PHP: [ms(2)|rnd(2)|sec(4)] — any 8 bytes work for CTR
    ct = AES.new(_derive_key(password), AES.MODE_CTR, nonce=nonce, initial_value=0).encrypt(plain.encode())
    return base64.b64encode(nonce + ct).decode()

def selftest():
    for t in ['4111111111111111', '5491990031061824', '01', '12', 'a']:
        assert decrypt(encrypt(t)) == t, t
    print('[SELFTEST OK] round-trip encrypt->decrypt consistent')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
        selftest(); sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == '--file':
        # input: jsonl/csv with base64 values, one per line (or json list)
        with open(sys.argv[2], encoding='utf-8') as fh:
            for line in fh:
                v = line.strip().strip(',').strip('"')
                if not v:
                    continue
                try:
                    print(f'{v}\t{decrypt(v)}')
                except Exception as e:
                    print(f'{v}\t[ERR {e}]')
        sys.exit(0)
    if len(sys.argv) > 1:
        print(decrypt(sys.argv[1]))
    else:
        selftest()
