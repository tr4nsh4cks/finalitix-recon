#!/usr/bin/env python3
"""FINDEP IntelX continuation: remaining searches + file/read of stealer hits."""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = "https://2.intelx.io"
KEY = "6f65b43b-19df-4e12-aea3-115d793e9763"
HEADERS = {"x-key": KEY, "Content-Type": "application/json", "User-Agent": "IX-Python/1.0"}
H_GET = {"x-key": KEY, "User-Agent": "IX-Python/1.0"}
DIR = Path(r"c:\xampp\htdocs\pentagi\independencia_attack")
SRC = DIR / "intelx_findep_results_copy.json"
OUT = DIR / "intelx_findep_results.json"
OUT2 = DIR / "intelx_findep_results_final.json"

REMAINING = [
    {"id": "intel_at_independencia", "term": "@independencia.com.mx", "buckets": ["leaks.logs"]},
    {"id": "intel_indep_logs", "term": "independencia.com.mx", "buckets": ["leaks.logs"]},
    {"id": "intel_calidad_logs", "term": "calidad-architect.com", "buckets": ["leaks.logs"]},
    {"id": "intel_findep_logs", "term": "findep.mx", "buckets": ["leaks.logs"]},
    {"id": "intel_kubeconfig", "term": "kubeconfig independencia", "buckets": []},
    {"id": "intel_fisa", "term": "fisa.independencia", "buckets": []},
    {"id": "intel_spei", "term": "spei independencia.com.mx", "buckets": []},
    {"id": "intel_jks", "term": "jks independencia", "buckets": []},
    {"id": "intel_pem", "term": "pem independencia", "buckets": []},
    {"id": "intel_soto", "term": "Luis Rodrigo Soto Solorzano", "buckets": []},
    {"id": "intel_escamilla", "term": "Roman Escamilla independencia", "buckets": []},
    {"id": "intel_archive_189", "term": "189.157.121.189", "buckets": ["leaks.logs"]},
    {"id": "intel_passwords_indep", "term": "Passwords.txt independencia.com.mx", "buckets": ["leaks.logs"]},
]

EMAIL_PASS_RE = re.compile(
    r"(?i)([a-z0-9._%+\-]+@(?:independencia\.com\.mx|findep\.mx|calidad-architect\.com))\s*[:|;,\t ]+\s*(\S+)"
)
URL_USER_PASS_RE = re.compile(r"(?i)(https?://[^\s]+)\s*[:|\t]\s*([^\s:]+)\s*[:|\t]\s*(.+)")
STEALER_BLOCK_RE = re.compile(
    r"(?is)(?:URL|Host|Hostname)\s*[:=]\s*(\S+).*?(?:Username|User|Login|Email)\s*[:=]\s*(\S+).*?(?:Password|Pass|Pwd)\s*[:=]\s*(\S+)"
)
EMAIL_RE = re.compile(r"(?i)([a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,})")
TARGET_DOMAINS = ("independencia.com.mx", "findep.mx", "calidad-architect.com", "fisa.independencia")


def log(msg: str) -> None:
    print(msg, flush=True)


def credits():
    r = requests.get(f"{BASE}/authenticate/info", headers=H_GET, timeout=30, verify=False)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"raw": r.text[:400]}


def credit_paths(info: dict) -> dict:
    paths = (info or {}).get("paths") or {}
    out = {}
    for k in (
        "/intelligent/search",
        "/phonebook/search",
        "/file/read",
        "/file/view",
        "/file/preview",
    ):
        v = paths.get(k)
        if isinstance(v, dict):
            out[k] = {"Credit": v.get("Credit"), "CreditMax": v.get("CreditMax")}
    return out


def save(obj: dict) -> None:
    raw = json.dumps(obj, indent=2, ensure_ascii=False, default=str)
    for p in (OUT2, OUT):
        try:
            p.write_text(raw, encoding="utf-8")
        except Exception as e:
            log(f"  save fail {p.name}: {e}")


def intel_start(term: str, buckets: list | None, maxresults: int = 80):
    body = {
        "term": term,
        "buckets": buckets or [],
        "lookuplevel": 0,
        "maxresults": maxresults,
        "timeout": 8,
        "datefrom": "",
        "dateto": "",
        "sort": 2,
        "media": 0,
        "terminate": [],
    }
    r = requests.post(f"{BASE}/intelligent/search", headers=HEADERS, json=body, timeout=45, verify=False)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"raw": r.text[:500]}


def intel_result(search_id: str, limit: int = 80):
    r = requests.get(
        f"{BASE}/intelligent/search/result",
        headers=H_GET,
        params={"id": search_id, "limit": limit, "offset": 0},
        timeout=45,
        verify=False,
    )
    try:
        data = r.json()
    except Exception:
        return None, []
    return data.get("status"), data.get("records") or []


def slim(rec: dict) -> dict:
    keep = ["systemid", "storageid", "name", "bucket", "date", "size", "mediah", "xscore"]
    return {k: rec.get(k) for k in keep if k in rec}


def file_get(rec: dict, mode: str = "read", preview_lines: int = 400) -> tuple[str, str, int]:
    sid = rec.get("systemid") or ""
    storage = rec.get("storageid") or ""
    bucket = rec.get("bucket") or ""
    if mode == "preview":
        urls = [
            (f"{BASE}/file/preview", {"f": 0, "l": preview_lines, "storageid": storage, "bucket": bucket, "systemid": sid}),
        ]
    elif mode == "view":
        urls = [
            (f"{BASE}/file/view", {"f": 0, "storageid": storage, "bucket": bucket, "systemid": sid}),
        ]
    else:
        urls = [
            (f"{BASE}/file/read", {"type": 0, "systemid": sid, "bucket": bucket, "storageid": storage}),
            (f"{BASE}/file/read", {"type": 0, "storageid": storage, "bucket": bucket}),
        ]
    last = "empty"
    for url, params in urls:
        try:
            r = requests.get(url, headers=H_GET, params=params, timeout=70, verify=False)
            last = f"{url.rsplit('/',1)[-1]}:{r.status_code}:{len(r.text)}"
            if r.status_code == 200 and r.text and not r.text.strip().startswith('{"error"'):
                return r.text, url.rsplit("/", 1)[-1], r.status_code
            if r.status_code == 200 and r.text:
                return r.text, url.rsplit("/", 1)[-1], r.status_code
        except Exception as e:
            last = str(e)[:120]
    return "", last, 0


def extract_creds(content: str, source: str, term: str) -> list[dict]:
    found = []
    seen = set()
    # URL:user:pass and email:pass
    for i, line in enumerate(content.splitlines()):
        ll = line.lower()
        if not any(d in ll for d in TARGET_DOMAINS) and "kube" not in ll and "-----begin" not in ll:
            continue
        entry = {
            "term": term,
            "source": source,
            "line_num": i + 1,
            "match_line": line.strip()[:500],
        }
        m = EMAIL_PASS_RE.search(line)
        if m:
            entry["email"] = m.group(1)
            entry["password"] = m.group(2).strip("\"'` ")
        m2 = URL_USER_PASS_RE.search(line)
        if m2:
            entry["url"] = m2.group(1)
            entry["username"] = m2.group(2)
            entry["password"] = m2.group(3).strip()
        emails = EMAIL_RE.findall(line)
        if emails:
            entry["emails_on_line"] = emails
        key = (entry.get("email"), entry.get("username"), entry.get("password"), entry["match_line"][:80])
        if key not in seen:
            seen.add(key)
            found.append(entry)

    # Stealer block format
    for m in STEALER_BLOCK_RE.finditer(content):
        url, user, pw = m.group(1), m.group(2), m.group(3)
        blob = f"{url} {user} {pw}".lower()
        if not any(d in blob for d in TARGET_DOMAINS):
            continue
        entry = {
            "term": term,
            "source": source,
            "url": url,
            "username": user,
            "password": pw,
            "match_line": f"{url}:{user}:{pw}"[:500],
        }
        found.append(entry)
    return found


def flags_of(content: str) -> dict:
    low = content.lower()
    flags = {
        "kubeconfig": ("clusters:" in low and "apiVersion:" in content) or "client-key-data" in low,
        "gcp_sa_json": "service_account" in low and "private_key" in low,
        "begin_cert": "-----begin" in low,
        "jks": any(x in low for x in [".jks", "keystore", "storepass", "keypass"]),
        "vpn": any(x in low for x in ["anyconnect", "forticlient", "globalprotect", "vpn."]),
        "spring": "spring:" in low and "password:" in low,
        "spei": any(x in low for x in ["spei", "banxico", "pocc"]),
    }
    return {k: v for k, v in flags.items() if v}


PRIORITY_READS = [
    # calidad-architect GOLD
    {
        "name": "[MX]189.157.121.189.rar/Important Files/Desktop/usuarios y contraseñas.txt",
        "bucket": "leaks.logs",
        "systemid": "8d3441be-b43f-4708-8669-31e599d1f38e",
        "storageid": "e9d15ad3c85ec394cb3b45f587e35f6f1923bfdb8c94b292cbc356b00831e3bcd6efb656d509c66bcd9e005b90812bc65edb7484a7e7851839753dfb26be1443",
        "size": 8559,
        "term": "calidad-architect.com",
        "mode": "read",
    },
    {
        "name": "MX[C6AB7ABB...] Autofills Chrome 2022-09-12",
        "bucket": "leaks.logs",
        "systemid": "1ee60c67-c009-45a3-88e0-e9ebe42f3832",
        "storageid": "f9099b0533f98071453a450996bc08e622a3255122f8e08c73167f86c48532bd11f4fb82157ab297166701205a757904326a494c6f3752bf3ad682bf21a02aaf",
        "size": 17333,
        "term": "calidad-architect.com",
        "mode": "read",
    },
    {
        "name": "MX[C6AB7ABB...] Autofills Chrome 2022-09-13",
        "bucket": "leaks.logs",
        "systemid": "18a01412-fce7-47d4-8bdb-e66bfd75fe40",
        "storageid": "bd92f38b9cae74231a63be65cefa1d04b4fd624175260fc996e260f8643d36c764c25103fbb939908b1ad85e01a075b5eebe0d61f38fb579d7196bad44917000",
        "size": 17655,
        "term": "calidad-architect.com",
        "mode": "read",
    },
    {
        "name": "[MX]ipv64675eb72af Cookies Opera GX",
        "bucket": "leaks.logs",
        "systemid": "c26e1f27-2bd4-4c59-9ec7-6bc621d312f1",
        "storageid": "715830a79f17c8502f56df05e15be634efc9612fae831e60a95bf48a1166b9e71bd93c3db0f6fd2e09269c661d8b210f2027c2a8898dd72d9aa6b3e0442374c3",
        "size": 92846,
        "term": "calidad-architect.com",
        "mode": "read",
    },
    {
        "name": "Exploit.in/70.txt part6 (independencia combo)",
        "bucket": "leaks.public.general",
        "systemid": "8a268362-1d12-499d-a679-ff81670ceb8f",
        "storageid": "c1bea411b9b1bb244f8d0e9e601e7db1517a072db73ed23aae067fcf1ce0042e8a55f5a07de724990b32cb50cef0e42494f9508962d9315f032e9bc203019421",
        "size": 4194298,
        "term": "independencia.com.mx",
        "mode": "preview",
    },
    {
        "name": "50M Link Login Pass part263",
        "bucket": "leaks.private.general",
        "systemid": "9f39e5ae-5106-4bf0-bb7b-912f26e1777b",
        "storageid": "a9be2cfb47cb7b690c5d40b53166d6f42d1e178ef3f2d6af7f5a3f335d2c879d9b5f4f1d664ae4054d3468a04740771cf82b8fc248cf9660b3efad25daae4268",
        "size": 4194271,
        "term": "independencia.com.mx",
        "mode": "preview",
    },
    {
        "name": "Cit0day alura.net decrypted",
        "bucket": "leaks.private.general",
        "systemid": "3beec065-1a6b-4ab0-ae81-5fd56378d38c",
        "storageid": "ed2ae90f41e8e672deaff79afeb92599fc1a46a837428a373a1afc6818c335c8d1f360da42879d12fd5f4bc94cf8f98c38e62417c6b3a7bddd8d49254bd9c0c6",
        "size": 2109538,
        "term": "independencia.com.mx",
        "mode": "preview",
    },
    {
        "name": "Cit0day realtimepublishers decrypted 62.681",
        "bucket": "leaks.private.general",
        "systemid": "f36df5d7-4c0a-4868-878f-6c63ab3ed81d",
        "storageid": "ae9e8cef41fc02392aaa45940063f1760b16ea74e05cafaccae4f6aa80b0df2734d0b8ca458e36fbefe28c082eadc1cd315d91ba6478c8b9037006c25782dc32",
        "size": 1963659,
        "term": "independencia.com.mx",
        "mode": "preview",
    },
    {
        "name": "Exploit.in/32.txt part3",
        "bucket": "leaks.public.general",
        "systemid": "31836fad-a79e-4ef9-8887-7e4f0cb6cb9d",
        "storageid": "93b8d23fcca19bdb7061c5278b5e2c8c1d8b120cd6a522916a62ecbd210b50c42d467a7d56c47e0424123b6fc42054b6e0caf6b8e01be16b16eb13a3d5090770",
        "size": 4194274,
        "term": "independencia.com.mx",
        "mode": "preview",
    },
]


def main():
    started = datetime.now(timezone.utc).isoformat()
    if SRC.exists():
        out = json.loads(SRC.read_text(encoding="utf-8"))
        log(f"loaded salvage {SRC.name} intel={len(out.get('intelligent') or [])}")
    elif OUT.exists():
        out = json.loads(OUT.read_text(encoding="utf-8"))
        log(f"loaded {OUT.name}")
    else:
        out = {"phonebook": {}, "intelligent": []}

    out["continued_utc"] = started
    out.setdefault("downloaded_files", [])
    out.setdefault("credentials", [])
    out.setdefault("k8s_gcp_hits", [])
    out.setdefault("cert_keystore_refs", [])
    out.setdefault("vpn_refs", [])
    out.setdefault("credits_usage", [])

    sc0, creds_before = credits()
    log(f"[credits before continue] {json.dumps(credit_paths(creds_before))}")
    out["credits_before_continue"] = credit_paths(creds_before)

    done_ids = {e.get("id") for e in (out.get("intelligent") or [])}
    all_records: dict[str, dict] = {}
    for e in out.get("intelligent") or []:
        for r in e.get("records") or []:
            key = r.get("systemid") or r.get("storageid")
            if key:
                all_records[key] = {"record": r, "terms": [e.get("term")]}

    # ---- remaining intelligent ----
    for spec in REMAINING:
        if spec["id"] in done_ids:
            log(f"skip already done {spec['id']}")
            continue
        log(f"\n=== INTEL {spec['id']}: {spec['term']!r} buckets={spec['buckets'] or 'ALL'} ===")
        http, start = intel_start(spec["term"], spec["buckets"])
        sid = (start or {}).get("id")
        log(f"  start http={http} id={sid}")
        if http != 200 or not sid:
            if spec["buckets"]:
                log("  retry ALL buckets")
                http, start = intel_start(spec["term"], [])
                sid = (start or {}).get("id")
                log(f"  retry http={http} id={sid}")
        entry = {"id": spec["id"], "term": spec["term"], "buckets": spec["buckets"], "start_http": http}
        if not sid:
            entry["error"] = "no id"
            entry["start"] = start
            out["intelligent"].append(entry)
            save(out)
            continue
        time.sleep(6)
        status, records = intel_result(sid)
        if not records and status not in (1, 2, 3):
            time.sleep(5)
            status, records = intel_result(sid)
        entry["poll_status"] = status
        entry["record_count"] = len(records)
        entry["records"] = [slim(r) for r in records]
        log(f"  records={len(records)} status={status}")
        for r in entry["records"][:25]:
            log(f"     [{r.get('bucket')}] {str(r.get('name'))[:110]} size={r.get('size')}")
        for r in records:
            key = r.get("systemid") or r.get("storageid")
            if key and key not in all_records:
                all_records[key] = {"record": r, "terms": [spec["term"]]}
            elif key:
                all_records[key]["terms"].append(spec["term"])
        out["intelligent"].append(entry)
        save(out)
        time.sleep(0.8)

    # extra reads from new leaks.logs records
    extra = []
    for info in all_records.values():
        rec = info["record"]
        name = (rec.get("name") or "").lower()
        bucket = rec.get("bucket") or ""
        size = rec.get("size") or 0
        if bucket == "leaks.logs" and size < 250000:
            if any(k in name for k in ["password", "pass.txt", "contrase", "login", "credential", "autofill", "user.txt", "all passwords"]):
                extra.append(rec)
        if any(k in name for k in ["kubeconfig", ".jks", ".pem", ".pfx", "application.yml", "service-account"]):
            extra.append(rec)

    # ---- file reads ----
    log("\n=== FILE READ / PREVIEW ===")
    to_read = list(PRIORITY_READS)
    seen_sys = {x["systemid"] for x in PRIORITY_READS}
    for rec in extra:
        sid = rec.get("systemid")
        if sid and sid not in seen_sys:
            seen_sys.add(sid)
            to_read.append(
                {
                    "name": rec.get("name"),
                    "bucket": rec.get("bucket"),
                    "systemid": sid,
                    "storageid": rec.get("storageid"),
                    "size": rec.get("size"),
                    "term": "extra-logs",
                    "mode": "read" if (rec.get("size") or 0) < 300000 else "preview",
                }
            )

    for spec in to_read[:30]:
        log(f"\n  {spec['mode'].upper()} {str(spec.get('name'))[:100]}")
        content, via, code = file_get(spec, spec.get("mode") or "read")
        if not content:
            log(f"    FAIL {via}")
            out["downloaded_files"].append({**{k: spec[k] for k in spec if k != "storageid"}, "error": via})
            save(out)
            continue
        log(f"    OK via={via} chars={len(content)} http={code}")
        fl = flags_of(content)
        snippet = content[:4000]
        item = {
            "name": spec.get("name"),
            "bucket": spec.get("bucket"),
            "systemid": spec.get("systemid"),
            "term": spec.get("term"),
            "via": via,
            "chars": len(content),
            "flags": fl,
            "snippet": snippet,
        }
        # keep hits containing target domains even in snippet
        low = content.lower()
        item["contains_independencia"] = "independencia" in low
        item["contains_findep"] = "findep" in low
        item["contains_calidad"] = "calidad-architect" in low
        out["downloaded_files"].append(item)
        if fl.get("kubeconfig") or fl.get("gcp_sa_json"):
            out["k8s_gcp_hits"].append({**item, "snippet": content[:8000]})
            log(f"    *** K8s/GCP {list(fl)}")
        if fl.get("begin_cert") or fl.get("jks") or fl.get("spei"):
            out["cert_keystore_refs"].append({"name": spec.get("name"), "flags": fl, "match": snippet[:800]})
        if fl.get("vpn"):
            out["vpn_refs"].append({"name": spec.get("name"), "match": snippet[:800]})
        creds = extract_creds(content, str(spec.get("name")), str(spec.get("term")))
        if creds:
            log(f"    creds={len(creds)}")
            for c in creds[:12]:
                log(f"      {c.get('match_line','')[:180]}")
            out["credentials"].extend(creds)
        else:
            # dump lines with target domain even without pass
            hits = [ln.strip()[:250] for ln in content.splitlines() if any(d in ln.lower() for d in TARGET_DOMAINS)]
            if hits:
                log(f"    domain-lines={len(hits)}")
                for h in hits[:8]:
                    log(f"      {h}")
                item["domain_lines"] = hits[:50]
        save(out)
        time.sleep(0.4)

    # unique pairs
    pairs = []
    seen = set()
    emails = set()
    for e in (out.get("phonebook") or {}).get("pb_emails", {}).get("selectors") or []:
        emails.add(e.lower())
    for c in out.get("credentials") or []:
        ident = (c.get("email") or c.get("username") or "").strip()
        pw = (c.get("password") or "").strip()
        if ident:
            emails.add(ident.lower())
        if ident and pw:
            key = (ident.lower(), pw)
            if key not in seen:
                seen.add(key)
                pairs.append(
                    {
                        "identity": ident,
                        "password": pw,
                        "url": c.get("url"),
                        "source": c.get("source"),
                        "term": c.get("term"),
                    }
                )
        for em in c.get("emails_on_line") or []:
            emails.add(em.lower())

    out["unique_email_password"] = pairs
    out["unique_emails"] = sorted(emails)
    sc1, creds_after = credits()
    out["credits_after"] = credit_paths(creds_after)
    out["credits_after_raw_http"] = sc1
    out["finished_utc"] = datetime.now(timezone.utc).isoformat()
    out["summary"] = {
        "phonebook_emails": len((out.get("phonebook") or {}).get("pb_emails", {}).get("selectors") or []),
        "phonebook_domains": len((out.get("phonebook") or {}).get("pb_domains", {}).get("selectors") or []),
        "intelligent_searches": len(out.get("intelligent") or []),
        "intelligent_records_total": sum((e.get("record_count") or 0) for e in (out.get("intelligent") or [])),
        "files_downloaded": len(out.get("downloaded_files") or []),
        "credential_blocks": len(out.get("credentials") or []),
        "unique_email_password": len(pairs),
        "unique_emails": len(emails),
        "k8s_gcp_hits": len(out.get("k8s_gcp_hits") or []),
        "cert_keystore_refs": len(out.get("cert_keystore_refs") or []),
        "vpn_refs": len(out.get("vpn_refs") or []),
        "credits_before_continue": credit_paths(creds_before),
        "credits_after": credit_paths(creds_after),
    }
    save(out)
    log("\n========== SUMMARY ==========")
    log(json.dumps(out["summary"], indent=2, default=str))
    log("PAIRS:")
    for p in pairs:
        log(f"  {p['identity']}:{p['password']}  src={p.get('source')}")
    if not pairs:
        log("  (none)")


if __name__ == "__main__":
    main()
