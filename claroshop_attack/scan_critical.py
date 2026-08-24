"""Scan gitlab_critical configs; print lines with creds/hosts/keys."""
import os, re, io, sys, glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "nexus_image_secrets", "gitlab_critical")

CRED = re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|private|DB_HOST|DB_USERNAME|DB_PASSWORD|"
                  r"USERVAR|dbasears|mrc-services|3306|3308|3310|27017|mongodb|mysql|jdbc|redis://|amqp|"
                  r"host\s*[:=]\s*['\"]?\d+\.\d+|\$\{[A-Z_]+\})")

for f in sorted(glob.glob(os.path.join(DIR, "*"))):
    text = open(f, encoding="utf-8", errors="replace").read()
    name = os.path.basename(f)
    if name.endswith(".key"):
        print(f"\n### {name}  [PRIVATE KEY FILE - {len(text)} bytes]")
        print("  " + text[:120].replace("\n", " "))
        continue
    lines = []
    for l in text.splitlines():
        ls = l.strip()
        if not ls or ls.startswith("#") or ls.startswith("*") or ls.startswith("//"):
            continue
        if CRED.search(ls):
            lines.append(ls)
    if lines:
        print(f"\n### {name}")
        for l in lines[:30]:
            print("  ", l[:230])
