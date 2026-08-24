import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aesctr_tdc_decrypt import decrypt
import base64

samples = [
    'L7nSVdHR0dF/VLlW9yCgBC9SZOQ=',
    'eLPSVaOjo6NkY4jy+Nafepcz2JgypSA=',
    'T6rSVVZWVlaw9G6mohmb5q9E3Hk=',
    '163SVdra2tq4DF0DBUPMIw+8Wns=',
]

print("=== DECRYPTION TEST ===")
for s in samples:
    try:
        raw = base64.b64decode(s)
        print(f"\nEncrypted: {s}")
        print(f"  Raw hex: {raw.hex()}")
        print(f"  Nonce(8): {raw[:8].hex()}")
        print(f"  Body({len(raw)-8}): {raw[8:].hex()}")
        result = decrypt(s)
        is_card = all(c.isdigit() for c in result if c != '\ufffd')
        print(f"  Decrypted: {repr(result)}")
        print(f"  Looks like card: {is_card}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n=== SELFTEST ===")
from aesctr_tdc_decrypt import selftest
selftest()
