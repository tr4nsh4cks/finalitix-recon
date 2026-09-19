import json
from pathlib import Path

d = json.loads(
    Path(r"c:\xampp\htdocs\pentagi\independencia_attack\intelx_findep_results_copy.json").read_text(
        encoding="utf-8"
    )
)

print("=== INDEP combo-like / small / logs ===")
for e in d["intelligent"]:
    if e["id"] != "intel_independencia":
        continue
    for r in e.get("records") or []:
        name = r.get("name") or ""
        nl = name.lower()
        bucket = r.get("bucket") or ""
        size = r.get("size") or 0
        keep = False
        if "leaks.logs" in bucket:
            keep = True
        if any(k in nl for k in ["pass", "combo", "cit0day", "exploit.in", "dehashed", "mailpass", "login"]):
            keep = True
        if size < 100000:
            keep = True
        if keep:
            print(
                json.dumps(
                    {
                        "name": name[:160],
                        "bucket": bucket,
                        "size": size,
                        "systemid": r.get("systemid"),
                        "storageid": r.get("storageid"),
                    },
                    ensure_ascii=False,
                )
            )

print("\n=== FINDEP leaks.logs small ===")
for e in d["intelligent"]:
    if e["id"] != "intel_findep":
        continue
    for r in e.get("records") or []:
        if (r.get("bucket") or "") == "leaks.logs" and (r.get("size") or 0) < 200000:
            print(
                json.dumps(
                    {
                        "name": (r.get("name") or "")[:160],
                        "size": r.get("size"),
                        "systemid": r.get("systemid"),
                        "storageid": r.get("storageid"),
                    },
                    ensure_ascii=False,
                )
            )
