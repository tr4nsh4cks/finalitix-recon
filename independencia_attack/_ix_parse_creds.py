import json
from pathlib import Path

for name in [
    "intelx_findep_results_final.json",
    "intelx_findep_results.json",
    "intelx_findep_results_copy.json",
]:
    p = Path(r"c:\xampp\htdocs\pentagi\independencia_attack") / name
    if not p.exists():
        print("MISSING", name)
        continue
    print("FILE", name, "bytes", p.stat().st_size, "mtime", p.stat().st_mtime)
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print("  parse fail", e)
        continue
    print("  intel", len(d.get("intelligent") or []), "dl", len(d.get("downloaded_files") or []), "creds", len(d.get("credentials") or []))
    print("  finished", d.get("finished_utc"), "summary", bool(d.get("summary")))
    pairs = {}
    for c in d.get("credentials") or []:
        ident = (c.get("email") or c.get("username") or "").strip()
        pw = (c.get("password") or "").strip()
        url = c.get("url") or ""
        if ident and pw:
            key = (ident.lower(), pw, url)
            pairs[key] = {
                "identity": ident,
                "password": pw,
                "url": url,
                "source": c.get("source"),
            }
    print("  unique ident:pw:url", len(pairs))
    for k, v in list(pairs.items())[:40]:
        print(f"    {v['identity']}:{v['password']}  url={v.get('url','')[:80]}  src={(v.get('source') or '')[:60]}")

    # calidad desktop file snippet
    for f in d.get("downloaded_files") or []:
        n = (f.get("name") or "").lower()
        if "contrase" in n or "usuarios y" in n:
            print("\n=== USUARIOS Y CONTRASENAS snippet ===")
            print((f.get("snippet") or "")[:4000])
            print("=== END SNIPPET ===")
