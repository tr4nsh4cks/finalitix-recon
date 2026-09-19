import json
from pathlib import Path

d = json.loads(
    Path(r"c:\xampp\htdocs\pentagi\independencia_attack\intelx_findep_results_copy.json").read_text(
        encoding="utf-8"
    )
)

for e in d["intelligent"]:
    if e["id"] == "intel_calidad":
        print("=== CALIDAD ===")
        for r in e.get("records") or []:
            print(
                json.dumps(
                    {
                        k: r.get(k)
                        for k in [
                            "name",
                            "bucket",
                            "size",
                            "date",
                            "systemid",
                            "storageid",
                            "xscore",
                        ]
                    },
                    ensure_ascii=False,
                )
            )
            print("---")

print("\n=== INDEP interesting ===")
for e in d["intelligent"]:
    if e["id"] != "intel_independencia":
        continue
    for r in e.get("records") or []:
        name = (r.get("name") or "").lower()
        bucket = r.get("bucket") or ""
        size = r.get("size") or 0
        if (
            "leaks.logs" in bucket
            or size < 80000
            or any(k in name for k in ["password", "kube", "jks", "pem", "vpn", "keystore", "yml"])
        ):
            print(f"[{bucket}] {size} {r.get('name')}")

print("\n=== FINDEP buckets ===")
for e in d["intelligent"]:
    if e["id"] != "intel_findep":
        continue
    buckets = {}
    for r in e.get("records") or []:
        b = r.get("bucket") or "?"
        buckets[b] = buckets.get(b, 0) + 1
        name = (r.get("name") or "").lower()
        if "leaks.logs" in (r.get("bucket") or "") or any(
            k in name for k in ["password", "kube", "jks", "pem", "vpn"]
        ):
            print("HIT", r.get("bucket"), r.get("size"), r.get("name"))
    print("bucket counts", buckets)

print("\n=== email sample ===")
emails = d["phonebook"]["pb_emails"]["selectors"]
print("n=", len(emails))
for x in emails[:15]:
    print(x)
print("soto?", [e for e in emails if "soto" in e.lower()][:20])
print("escamilla?", [e for e in emails if "escamilla" in e.lower()][:20])
print("fisa?", [e for e in emails if "fisa" in e.lower()][:20])
