import base64, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from Crypto.Cipher import AES

KEY_PROD = b'8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA'
KEY_DEV  = b'K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4'

def derive_key(password, nbits=256):
    nbytes = nbits // 8
    pw = password[:nbytes]
    k1 = AES.new(pw, AES.MODE_ECB).encrypt(pw[:16])
    return k1 + k1[:nbytes - 16]

def decrypt(b64, password):
    raw = base64.b64decode(b64)
    nonce, body = raw[:8], raw[8:]
    return AES.new(derive_key(password), AES.MODE_CTR, nonce=nonce, initial_value=0).decrypt(body)

samples = [
    ("vHPKSjAwMDD/opBAQngTntm38mQ/amIA", "Juan M Gonzalez Nava", "01", "13"),
    ("vHPKSlhYWFgS9uhlteyENDBkIL9WWKAb", "Juan M Gonzalez Nava", "02", "09"),
    ("vHPKSnZ2dnZsMXuSgB4=", "546 546 54", "01", "08"),
    ("vHPKSpycnJwpwpeW2VxRMnI=", "654 654 654", "01", "08"),
    ("vHPKSre3t7e/dFCL3mU=", "54 65 465", "01", "08"),
]

print("=" * 70)
print("DECRYPT TEST: datostarjeta samples con key PROD y DEV")
print("=" * 70)

for b64, nombre, mes, ao in samples:
    print(f"\nB64: {b64}")
    print(f"  Nombre: {nombre} | Mes: {mes} | Ao: {ao}")
    for label, key in [("PROD", KEY_PROD), ("DEV", KEY_DEV)]:
        try:
            result = decrypt(b64, key)
            printable = result.decode("utf-8", "replace")
            is_pan = all(c.isdigit() for c in printable.strip()) and 12 <= len(printable.strip()) <= 19
            tag = "PAN VALIDO" if is_pan else ("DIGITOS" if printable.strip().isdigit() else "BASURA")
            print(f"  {label}: [{printable}] -> {tag}")
        except Exception as e:
            print(f"  {label}: ERR {e}")

print("\n" + "=" * 70)
