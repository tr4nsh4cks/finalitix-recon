"""Scan all hunt_*.txt files for secrets; print condensed hits per file."""
import os, re, io, sys, glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

NOISE = re.compile(r"(pear|/doc/|node_modules|openssl\.cnf|nsswitch|pam\.d|pwquality|management\.properties|THIRDPARTY|README|jmxremote|\.markdown|/etc/services|/etc/rpc|namespace\.init|/etc/default/nss)", re.I)
INTERESTING = re.compile(
    r"(password\s*[:=]|passwd|secret\s*[:=]|api[_-]?key\s*[:=]|BEGIN [A-Z ]*PRIVATE KEY|"
    r"Nic3\.|N3iUendbBbKpxFgk|wUt22Us2CUh|pySY8|nNzy|JenkisLegasy|dtvV50vwfGq5CO9|"
    r"env-generator|\.dockercfg|docker/config\.json|id_rsa|rootpw|"
    r"DB_HOST|DB_PASSWORD|DB_USERNAME|mongodb://|mysql://|jdbc:|amqp://|redis://)",
    re.I,
)

for f in sorted(glob.glob(os.path.join(HERE, "hunt_*.txt"))):
    raw = open(f, "rb").read().decode("utf-8", errors="replace")
    lines = [re.sub(r"^[\x00-\x08]+", "", l) for l in raw.splitlines()]
    hits = []
    for i, line in enumerate(lines):
        if INTERESTING.search(line) and not NOISE.search(line):
            ctx = lines[max(0, i - 1):i + 2]
            hits.append(" | ".join(c.strip() for c in ctx if c.strip()))
    name = os.path.basename(f)
    if hits:
        print(f"\n### {name} ({len(hits)} hits)")
        seen = set()
        for h in hits:
            if h not in seen:
                seen.add(h)
                print("  ", h[:250])
    else:
        print(f"--- {name}: clean")
