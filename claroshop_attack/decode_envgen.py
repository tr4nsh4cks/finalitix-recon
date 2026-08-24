"""Decode all base64 env blobs from env-generator.sh and save them."""
import re, base64, json, os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "nexus_image_secrets")
os.makedirs(OUTDIR, exist_ok=True)

src = open(os.path.join(HERE, "env-generator.sh"), encoding="utf-8").read()

# blocks like: 'name') \n Xecho 'B64...'
blocks = re.findall(r"'(\w+)'\)\s*\n\s*\w*echo\s*'([A-Za-z0-9+/=\s]+?)'\s*\n\s*;;", src)
print(f"BLOCKS FOUND: {len(blocks)}")

summary = {}
for name, b64 in blocks:
    b64clean = re.sub(r"\s", "", b64)
    try:
        decoded = base64.b64decode(b64clean).decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[{name}] DECODE ERR: {e}")
        continue
    outpath = os.path.join(OUTDIR, f"env_{name}.env")
    with open(outpath, "w", encoding="utf-8", newline="\n") as f:
        f.write(decoded)
    # parse key creds
    creds = {}
    for line in decoded.splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            if any(s in k.upper() for s in ["PASS", "USER", "HOST", "KEY", "DATABASE", "PORT", "URL"]):
                creds[k.strip()] = v.strip()
    summary[name] = creds
    print(f"\n### {name} -> {outpath}")
    for k, v in creds.items():
        print(f"  {k}={v}")

# also grab trailing function defs (xecho/pecho/etc) to understand deploy targets
funcs = re.findall(r"^(\w*echo)\s*\(\).*?^\}", src, re.S | re.M)
with open(os.path.join(OUTDIR, "envgen_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=1, ensure_ascii=False)
print(f"\nSAVED summary -> {OUTDIR}\\envgen_summary.json")
print("\n=== FUNCTIONS/DEPLOY LOGIC (tail of script) ===")
tail = src[src.find(";;") * 0:]  # full script tail after last block
print(src[-1800:])
