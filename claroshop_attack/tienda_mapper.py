# -*- coding: utf-8 -*-
"""Mapeo de tablas tienda DEV Sears via Jenkins Groovy -> Docker exec PHP -> MySQL."""
import base64, json, sys, io, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jenkins_exec import jenkins_exec

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GROOVY_TEMPLATE = r'''
import groovy.json.JsonOutput
import groovy.json.JsonSlurper

def dockerExec(String cmd) {
    def create = new URL("http://172.27.140.148:4243/containers/5b32e909c295/exec").openConnection()
    create.setRequestMethod("POST")
    create.setDoOutput(true)
    create.setConnectTimeout(10000)
    create.setReadTimeout(30000)
    create.setRequestProperty("Content-Type", "application/json")
    def body = JsonOutput.toJson([AttachStdout:true, AttachStderr:true, Tty:true, Cmd:["sh","-c",cmd]])
    create.getOutputStream().write(body.getBytes("UTF-8"))
    def resp = new JsonSlurper().parseText(create.getInputStream().getText("UTF-8"))
    def execId = resp.Id
    def start = new URL("http://172.27.140.148:4243/exec/${execId}/start").openConnection()
    start.setRequestMethod("POST")
    start.setDoOutput(true)
    start.setConnectTimeout(10000)
    start.setReadTimeout(120000)
    start.setRequestProperty("Content-Type", "application/json")
    def startBody = JsonOutput.toJson([Detach:false, Tty:true])
    start.getOutputStream().write(startBody.getBytes("UTF-8"))
    return start.getInputStream().getText("UTF-8")
}

def b64 = "__B64__"
def cmd = "echo " + b64 + " | base64 -d > /tmp/q.php && php /tmp/q.php"
println "===BEGIN==="
println dockerExec(cmd)
println "===END==="
'''

def run_php(php_code, tag=""):
    b64 = base64.b64encode(php_code.encode('utf-8')).decode()
    groovy = GROOVY_TEMPLATE.replace("__B64__", b64)
    out = jenkins_exec(groovy)
    if "===BEGIN===" in out:
        out = out.split("===BEGIN===", 1)[1]
        if "===END===" in out:
            out = out.split("===END===", 1)[0]
    out = out.strip()
    if tag:
        print(f"[{tag}] bytes={len(out)}")
    return out

DB = "tienda"
DBH = "172.27.141.6"
DBU = "apifincadodev"
DBP = "1q2w3e4r5t6y"
DBPORT = 3308

PHP_HEAD = f'''<?php
error_reporting(0);
$m = new mysqli('{DBH}','{DBU}','{DBP}','{DB}',{DBPORT});
if ($m->connect_error) {{ die("CONN_ERR: ".$m->connect_error); }}
$m->set_charset('utf8mb4');
'''
PHP_FOOT = "?>"

# ---------- STEP 1: inventario completo + columnas fecha ----------
step1 = PHP_HEAD + r'''
$tables = [];
$r = $m->query("SELECT TABLE_NAME, TABLE_ROWS, ENGINE, CREATE_TIME, UPDATE_TIME FROM information_schema.TABLES WHERE TABLE_SCHEMA='tienda' ORDER BY TABLE_ROWS DESC");
while($row=$r->fetch_assoc()) $tables[]=$row;
$datecols = [];
$r = $m->query("SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND DATA_TYPE IN ('date','datetime','timestamp') ORDER BY TABLE_NAME, ORDINAL_POSITION");
while($row=$r->fetch_assoc()) $datecols[$row['TABLE_NAME']][]=$row;
echo json_encode(['tables'=>$tables,'datecols'=>$datecols], JSON_UNESCAPED_UNICODE);
''' + PHP_FOOT

print("[*] STEP 1: inventario de tablas...")
raw = run_php(step1, "step1")
try:
    data = json.loads(raw)
except Exception as e:
    print("PARSE ERR:", e)
    print(raw[:2000])
    sys.exit(1)

tables = data['tables']
datecols = data['datecols']
print(f"[+] Total tablas en '{DB}': {len(tables)}")

# ---------- STEP 2: fecha mas reciente para tablas >100 filas ----------
big_tables = [t for t in tables if (t['TABLE_ROWS'] or 0) and int(t['TABLE_ROWS']) > 100]
print(f"[*] STEP 2: fechas recientes en {len(big_tables)} tablas >100 filas...")

tbl_list = [t['TABLE_NAME'] for t in big_tables]
step2 = PHP_HEAD + r'''
$names = json_decode('__TBLJSON__', true);
$datecols = json_decode('__DCJSON__', true);
$prio = ['created_at','updated_at','created','updated','fecha_creacion','fecha_modificacion','fecha_registro','fecha_alta','fecha','date_created','date_updated','date','ts','timestamp','last_update'];
$out = [];
foreach ($names as $t) {
    $cols = isset($datecols[$t]) ? $datecols[$t] : [];
    $chosen = null;
    foreach ($prio as $p) {
        foreach ($cols as $c) { if (strtolower($c['COLUMN_NAME'])===$p) { $chosen=$c['COLUMN_NAME']; break 2; } }
    }
    if (!$chosen && count($cols)>0) $chosen = $cols[0]['COLUMN_NAME'];
    $rec = ['table'=>$t, 'date_col'=>$chosen, 'max_date'=>null];
    if ($chosen) {
        $q = "SELECT MAX(`".$chosen."`) AS mx FROM `".$t."`";
        $r = @$m->query($q);
        if ($r) { $row=$r->fetch_assoc(); $rec['max_date']=$row['mx']; }
    }
    $out[] = $rec;
}
echo json_encode($out, JSON_UNESCAPED_UNICODE);
'''.replace('__TBLJSON__', json.dumps(tbl_list)).replace('__DCJSON__', json.dumps(datecols)) + PHP_FOOT

raw2 = run_php(step2, "step2")
try:
    dates = json.loads(raw2)
except Exception as e:
    print("PARSE ERR step2:", e)
    print(raw2[:2000])
    dates = []
date_map = {d['table']: d for d in dates}

# ---------- STEP 3: ranking ----------
HIGH_PAT = ['pedido','order','datos_pedido','cliente','customer','pago','payment','transaccion','transaction','tarjeta','card','monedero','wallet','venta','sale','factura','invoice','billing','direccion','address','usuario','user','cuenta','account','credito','credit','cupon','coupon','descuento','discount','devolucion','refund','return','envio','shipping','carrito','cart','checkout','compra','purchase']
MED_PAT = ['producto','product','foto','photo','imagen','image','log','historial','history','inventario','inventory','stock','precio','price','sku','categoria','category','marca','brand','review','comentario','rating','wishlist','favorito','banner','promo']

def rank_table(name):
    n = name.lower()
    for p in HIGH_PAT:
        if p in n: return 'ALTO'
    for p in MED_PAT:
        if p in n: return 'MEDIO'
    return 'BAJO'

ranked = []
for t in tables:
    name = t['TABLE_NAME']
    rows = int(t['TABLE_ROWS'] or 0)
    d = date_map.get(name, {})
    ranked.append({
        'table': name,
        'rows': rows,
        'engine': t.get('ENGINE'),
        'create_time': t.get('CREATE_TIME'),
        'update_time': t.get('UPDATE_TIME'),
        'rank': rank_table(name),
        'date_col': d.get('date_col'),
        'max_date': d.get('max_date'),
        'has_aug2026': bool(d.get('max_date') and str(d.get('max_date')).startswith('2026-08')),
    })

rank_val = {'ALTO': 0, 'MEDIO': 1, 'BAJO': 2}
ranked.sort(key=lambda x: (rank_val[x['rank']], -x['rows']))

aug_tables = [r for r in ranked if r['has_aug2026']]
high_tables = [r for r in ranked if r['rank'] == 'ALTO']
print(f"[+] Ranking: ALTO={len(high_tables)} MEDIO={sum(1 for r in ranked if r['rank']=='MEDIO')} BAJO={sum(1 for r in ranked if r['rank']=='BAJO')}")
print(f"[+] Tablas con datos AGOSTO 2026: {len(aug_tables)}")

# ---------- STEP 4: samples top 20 ALTO ----------
top20 = [r['table'] for r in high_tables[:20]]
print(f"[*] STEP 4: samples de top {len(top20)} tablas ALTO...")
step4 = PHP_HEAD + r'''
$names = json_decode('__TBLJSON__', true);
$out = [];
foreach ($names as $t) {
    $r = @$m->query("SELECT * FROM `".$t."` ORDER BY 1 DESC LIMIT 20");
    $rows = [];
    if ($r) {
        while($row=$r->fetch_assoc()) {
            foreach($row as $k=>$v) {
                if (is_string($v) && strlen($v)>300) $row[$k]=substr($v,0,300).'...[TRUNC]';
            }
            $rows[]=$row;
        }
    }
    $out[$t]=$rows;
}
echo json_encode($out, JSON_UNESCAPED_UNICODE);
'''.replace('__TBLJSON__', json.dumps(top20)) + PHP_FOOT

raw4 = run_php(step4, "step4")
try:
    samples = json.loads(raw4)
except Exception as e:
    print("PARSE ERR step4:", e)
    print(raw4[:2000])
    samples = {}

# ---------- Guardar ----------
result = {
    'target': f'mysql://{DBH}:{DBPORT}/{DB}',
    'total_tables': len(tables),
    'tables_gt_100_rows': len(big_tables),
    'august_2026_tables': [r['table'] for r in aug_tables],
    'ranked_tables': ranked,
    'samples_top20_alto': samples,
}
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev_sears_tienda_tables_ranked.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"[+] Guardado: {out_path}")

# Resumen en consola
print("\n===== TOP 30 TABLAS (rank/rows/max_date) =====")
for r in ranked[:30]:
    print(f"{r['rank']:5} {r['rows']:>12,} {r['table'][:50]:50} {str(r.get('max_date'))[:19]}")
print("\n===== TABLAS CON DATOS AGOSTO 2026 =====")
for r in aug_tables[:40]:
    print(f"{r['rank']:5} {r['rows']:>12,} {r['table'][:50]:50} {str(r.get('max_date'))[:19]}")
