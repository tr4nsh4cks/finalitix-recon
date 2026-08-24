# -*- coding: utf-8 -*-
"""Fix step2: fechas recientes por tabla (PHP consulta information_schema directo)."""
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
    start.setReadTimeout(180000)
    start.setRequestProperty("Content-Type", "application/json")
    def startBody = JsonOutput.toJson([Detach:false, Tty:true])
    start.getOutputStream().write(startBody.getBytes("UTF-8"))
    return start.getInputStream().getText("UTF-8")
}

def b64 = "__B64__"
def cmd = "echo " + b64 + " | base64 -d > /tmp/q2.php && php /tmp/q2.php"
println "===BEGIN==="
println dockerExec(cmd)
println "===END==="
'''

def run_php(php_code):
    b64 = base64.b64encode(php_code.encode('utf-8')).decode()
    groovy = GROOVY_TEMPLATE.replace("__B64__", b64)
    out = jenkins_exec(groovy)
    if "===BEGIN===" in out:
        out = out.split("===BEGIN===", 1)[1]
        if "===END===" in out:
            out = out.split("===END===", 1)[0]
    return out.strip()

base = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base, 'dev_sears_tienda_tables_ranked.json'), encoding='utf-8') as f:
    data = json.load(f)

names = [t['table'] for t in data['ranked_tables'] if t['rows'] > 100]
print(f"[*] Consultando fechas en {len(names)} tablas...")

php = r'''<?php
error_reporting(0);
$m = new mysqli('172.27.141.6','apifincadodev','1q2w3e4r5t6y','tienda',3308);
if ($m->connect_error) { die("CONN_ERR: ".$m->connect_error); }
$m->set_charset('utf8mb4');
$names = json_decode('__TBLJSON__', true);
$out = [];
foreach ($names as $t) {
    $te = $m->real_escape_string($t);
    $r = @$m->query("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='tienda' AND TABLE_NAME='".$te."' AND DATA_TYPE IN ('datetime','timestamp','date')");
    $cols = [];
    if ($r) while($row=$r->fetch_assoc()) $cols[]=$row['COLUMN_NAME'];
    $best = null; $bestcol = null;
    foreach ($cols as $c) {
        $q = "SELECT MAX(`".$c."`) AS mx FROM `".$t."`";
        $rr = @$m->query($q);
        if ($rr) {
            $row = $rr->fetch_assoc();
            $v = $row['mx'];
            if ($v && ($best === null || strcmp(strval($v), strval($best)) > 0)) { $best = $v; $bestcol = $c; }
        }
    }
    $out[] = ['table'=>$t, 'date_col'=>$bestcol, 'max_date'=>$best];
}
echo json_encode($out, JSON_UNESCAPED_UNICODE);
?>'''.replace('__TBLJSON__', json.dumps(names))

raw = run_php(php)
try:
    dates = json.loads(raw)
except Exception as e:
    print("PARSE ERR:", e)
    print(raw[:3000])
    sys.exit(1)

date_map = {d['table']: d for d in dates}
aug = []
for t in data['ranked_tables']:
    d = date_map.get(t['table'])
    if d:
        t['date_col'] = d['date_col']
        t['max_date'] = d['max_date']
        t['has_aug2026'] = bool(d['max_date'] and str(d['max_date']).startswith('2026-08'))
    if t.get('has_aug2026'):
        aug.append(t['table'])

data['august_2026_tables'] = aug
with open(os.path.join(base, 'dev_sears_tienda_tables_ranked.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[+] Tablas con datos AGOSTO 2026: {len(aug)}")
print("\n===== TOP 40 POR FILAS (rank/rows/max_date/col) =====")
for t in sorted(data['ranked_tables'], key=lambda x: -x['rows'])[:40]:
    print(f"{t['rank']:5} {t['rows']:>12,} {t['table'][:48]:48} {str(t.get('max_date'))[:19]:19} {t.get('date_col')}")
print("\n===== AGOSTO 2026 =====")
for t in data['ranked_tables']:
    if t.get('has_aug2026'):
        print(f"{t['rank']:5} {t['rows']:>12,} {t['table'][:48]:48} {str(t.get('max_date'))[:19]}")
