# -*- coding: utf-8 -*-
"""Samples extra: clientes, lista_direcciones, datos_clientes (PII directa, rank ALTO)."""
import base64, json, sys, io, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tienda_dates import run_php

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

base = os.path.dirname(os.path.abspath(__file__))

php = r'''<?php
error_reporting(0);
$m = new mysqli('172.27.141.6','apifincadodev','1q2w3e4r5t6y','tienda',3308);
if ($m->connect_error) { die("CONN_ERR: ".$m->connect_error); }
$m->set_charset('utf8mb4');
$names = ['clientes','lista_direcciones','datos_clientes'];
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
?>'''

raw = run_php(php)
extra = json.loads(raw)

with open(os.path.join(base, 'dev_sears_tienda_tables_ranked.json'), encoding='utf-8') as f:
    data = json.load(f)
data['samples_extra_pii'] = extra
with open(os.path.join(base, 'dev_sears_tienda_tables_ranked.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

for t, rows in extra.items():
    if rows:
        print(f"{t}: {len(rows)} filas — cols: {', '.join(list(rows[0].keys())[:20])}")
        r = rows[0]
        keys = [k for k in r.keys() if any(p in k.lower() for p in ('mail','nombre','telefono','phone','rfc','curp','pass'))]
        for k in keys[:6]:
            v = str(r[k])
            print(f"   {k} = {v[:40]}")
print("[+] JSON actualizado con samples_extra_pii")
