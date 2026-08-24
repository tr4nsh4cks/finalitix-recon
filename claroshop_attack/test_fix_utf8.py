import sys
sys.stdout.reconfigure(encoding='utf-8')

def fix_double_utf8(s):
    if not s or not isinstance(s, str):
        return s
    # Try fixing double-encoded UTF-8
    try:
        if 'Ã' in s or 'Â' in s or 'â' in s:
            fixed = s.encode('latin1').decode('utf-8')
            return fixed
    except Exception:
        pass
    return s

test_str1 = "Polanco V SecciÃ³n"
test_str2 = "Ciudad de MÃ©xico"
test_str3 = "Gustavo Ezequiel Saldaña Bautista"
test_str4 = "AmpliaciÃ³n Granada"

print("1:", fix_double_utf8(test_str1))
print("2:", fix_double_utf8(test_str2))
print("3:", fix_double_utf8(test_str3))
print("4:", fix_double_utf8(test_str4))
