#!/usr/bin/env python3
"""IntelX hunt for Financiera Independencia / Findep — SPEI/POCC certificates + creds.
Authorized pentest engagement. Phonebook (emails) + intelligent search (leaks/certs).
Output: independencia_attack/intelx_findep_results.json
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()

BASE = "https://2.intelx.io"
KEY = "6f65b43b-19df-4e12-aea3-115d793e9763"
HEADERS = {"x-key": KEY, "Content-Type": "application/json", "User-Agent": "IX-Python/1.0"}
OUT = Path(r"c:\xampp\htdocs\pentagi\independencia_attack\intelx_findep_results.json")

CERT_EXTS = (".pem", ".jks", ".pfx", ".p12", ".cer", ".key", ".crt", ".der", ".keystore", ".p7b", ".csr")

PHONEBOOK_DOMAINS = [
    "independencia.com.mx",
    "findep.mx",
    "findep.com.mx",
    "apoyofin.com",
]

INTEL_SEARCHES = [
    {"id": "spei", "term": "independencia.com.mx spei"},
    {"id": "keystore", "term": "independencia.com.mx keystore"},
    {"id": "certificado", "term": "independencia.com.mx certificado"},
    {"id": "findep_spei_cert", "term": "findep spei certificate"},
    {"id": "findep_pass", "term": "findep.mx password"},
    {"id": "domain_certs", "term": "independencia.com.mx", "filter_certs": True},
    {"id": "findep_domain", "term": "findep.mx"},
    {"id": "pocc", "term": "independencia.com.mx pocc"},
]


def credits():
    try:
        r = requests.get(f"{BASE}/authenticate/info", headers=HEADERS, timeout=30, verify=False)
        return r.status_code, r.json()
    except Exception as e:
        return None, {"error": str(e)}


# ---------------- Phonebook ----------------
def phonebook_search(term: str, target: int = 2, maxresults: int = 100):
    body = {"term": term, "maxresults": maxresults, "media": 0, "target": target, "timeout": 5, "terminate": []}
    r = requests.post(f"{BASE}/phonebook/search", headers=HEADERS, json=body, timeout=60, verify=False)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"raw": r.text[:500]}


def phonebook_results(search_id: str, max_wait: int = 40):
    deadline = time.time() + max_wait
    selectors = []
    last = None
    while time.time() < deadline:
        r = requests.get(
            f"{BASE}/phonebook/search/result",
            headers=HEADERS,
            params={"id": search_id, "limit": 1000, "offset": 0},
            timeout=60,
            verify=False,
        )
        try:
            data = r.json()
        except Exception:
            time.sleep(2)
            continue
        last = data
        selectors = data.get("selectors") or []
        status = data.get("status")
        # status 1 = done, 0 = in progress
        if status in (1, 2, 3) or selectors:
            if status in (1, 2, 3):
                break
        time.sleep(2)
    return selectors, last


# ---------------- Intelligent ----------------
def intel_start(term: str, maxresults: int = 100):
    body = {
        "term": term,
        "buckets": [],
        "lookuplevel": 0,
        "maxresults": maxresults,
        "timeout": 5,
        "datefrom": "",
        "dateto": "",
        "sort": 2,
        "media": 0,
        "terminate": [],
    }
    r = requests.post(f"{BASE}/intelligent/search", headers=HEADERS, json=body, timeout=60, verify=False)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"raw": r.text[:1000]}


def intel_poll(search_id: str, limit: int = 100, max_wait: int = 45):
    records = []
    last_status = None
    deadline = time.time() + max_wait
    while time.time() < deadline:
        r = requests.get(
            f"{BASE}/intelligent/search/result",
            headers=HEADERS,
            params={"id": search_id, "limit": limit, "offset": len(records)},
            timeout=60,
            verify=False,
        )
        try:
            data = r.json()
        except Exception:
            time.sleep(2)
            continue
        last_status = data.get("status")
        recs = data.get("records") or []
        records.extend(recs)
        if last_status in (1, 2, 3):
            break
        time.sleep(2 if not recs else 1)
    return last_status, records


def looks_like_cert(rec: dict) -> bool:
    name = str(rec.get("name") or rec.get("mediah") or "").lower()
    return any(ext in name for ext in CERT_EXTS)


def slim(rec: dict) -> dict:
    keep = ["systemid", "storageid", "name", "bucket", "date", "media", "mediah",
            "size", "type", "instore", "accesslevel", "xscore", "keyvalues"]
    return {k: rec.get(k) for k in keep if k in rec}


def main():
    started = datetime.now(timezone.utc).isoformat()
    sc0, creds_before = credits()
    print(f"[credits before] http={sc0} {json.dumps(creds_before)[:400]}", flush=True)

    out = {
        "target": "Financiera Independencia / Findep",
        "mission": "SPEI/POCC cert hunt + employee creds (authorized engagement)",
        "started_utc": started,
        "credits_before": creds_before,
        "phonebook": {},
        "intelligent": [],
    }

    # ---- Phonebook: emails (target=2) + urls (target=3) ----
    for domain in PHONEBOOK_DOMAINS:
        for target, label in ((2, "emails"), (3, "urls")):
            key = f"{domain}:{label}"
            print(f"\n=== PHONEBOOK {key} ===", flush=True)
            try:
                http, start = phonebook_search(domain, target=target)
            except Exception as e:
                out["phonebook"][key] = {"error": str(e)}
                print(f"  START FAIL: {e}", flush=True)
                continue
            sid = (start or {}).get("id")
            print(f"  start http={http} id={sid}", flush=True)
            if not sid:
                out["phonebook"][key] = {"start_http": http, "start": start, "error": "no id"}
                continue
            selectors, raw = phonebook_results(sid)
            values = [s.get("selectorvalue") for s in selectors if s.get("selectorvalue")]
            out["phonebook"][key] = {
                "start_http": http,
                "count": len(values),
                "selectors": values,
                "raw_status": (raw or {}).get("status"),
            }
            print(f"  -> {len(values)} selectors", flush=True)
            for v in values:
                print(f"     {v}", flush=True)
            time.sleep(1)

    # ---- Intelligent searches ----
    seen_storage = set()
    cert_hits = []
    for spec in INTEL_SEARCHES:
        print(f"\n=== INTEL {spec['id']}: {spec['term']!r} ===", flush=True)
        entry = {"id": spec["id"], "term": spec["term"]}
        try:
            http, start = intel_start(spec["term"])
        except Exception as e:
            entry["error"] = str(e)
            out["intelligent"].append(entry)
            print(f"  START FAIL: {e}", flush=True)
            continue
        sid = (start or {}).get("id")
        entry["start_http"] = http
        print(f"  start http={http} id={sid}", flush=True)
        if not sid:
            entry["error"] = "no search id"
            entry["start_response"] = start
            out["intelligent"].append(entry)
            continue
        status, records = intel_poll(sid)
        entry["poll_status"] = status
        entry["record_count"] = len(records)
        slimmed = [slim(r) for r in records]
        entry["records"] = slimmed
        certs = [r for r in slimmed if looks_like_cert(r)]
        entry["cert_like"] = certs
        print(f"  records={len(records)} cert_like={len(certs)}", flush=True)
        for r in slimmed[:30]:
            print(f"     [{r.get('bucket')}] {str(r.get('name'))[:110]}", flush=True)
        for r in certs:
            sid_ = r.get("storageid")
            if sid_ and sid_ not in seen_storage:
                seen_storage.add(sid_)
                cert_hits.append({"from_search": spec["id"], **r})
                print(f"     CERT-HIT {r.get('name')} storageid={sid_}", flush=True)
        out["intelligent"].append(entry)
        time.sleep(1.2)

    sc1, creds_after = credits()
    print(f"\n[credits after] http={sc1} {json.dumps(creds_after)[:400]}", flush=True)

    out["credits_after"] = creds_after
    out["unique_cert_hits"] = cert_hits
    out["finished_utc"] = datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nSAVED {OUT} cert_hits={len(cert_hits)}", flush=True)


if __name__ == "__main__":
    main()
