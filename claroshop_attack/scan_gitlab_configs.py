"""Scan saved gitlab configs for credentials; print condensed."""
import os, re, io, sys, glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "nexus_image_secrets", "gitlab_configs")

CRED = re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|user(name)?\s*[:=]|host\s*[:=]|jdbc|mongodb://|mysql://|amqp|redis|url\s*[:=])")

for f in sorted(glob.glob(os.path.join(DIR, "*"))):
    text = open(f, encoding="utf-8", errors="replace").read()
    lines = [l for l in text.splitlines() if CRED.search(l) and l.strip() and not l.strip().startswith("#")]
    if not lines:
        continue
    print(f"\n### {os.path.basename(f)}")
    for l in lines[:25]:
        print("  ", l.strip()[:220])
