import subprocess, json, sys, csv, io
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def log(msg): print(f"[*] {msg}", flush=True)

with open('pld_tokens.json') as f:
    tokens = json.load(f)
ID_TOKEN = tokens['id_token']
PLD_GW = "https://0b8yuzev63.execute-api.us-east-1.amazonaws.com/prod"

def api(method, path, payload=None, timeout=15):
    cmd = [
        'curl.exe', '-s', '-m', str(timeout), '--noproxy', '*',
        '-X', method,
        '-H', f'Authorization: Bearer {ID_TOKEN}',
        '-H', 'Content-Type: application/json',
    ]
    if payload:
        cmd.extend(['-d', json.dumps(payload)])
    cmd.extend(['-w', '\n__HTTP_CODE:%{http_code}__', f'{PLD_GW}{path}'])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
    output = r.stdout
    if '__HTTP_CODE:' in output:
        parts = output.rsplit('__HTTP_CODE:', 1)
        body = parts[0].strip()
        code = parts[1].replace('__', '').strip()
    else:
        body = output.strip()
        code = '?'
    try:
        data = json.loads(body) if body else {}
    except:
        data = {'raw': body[:1000]}
    return code, data

# 1. usersAmount — saldos por usuario
log("=== SALDOS POR USUARIO ===")
code, data = api('GET', '/api/v1/transaction/usersAmount')
if data.get('success') and data.get('result', {}).get('data'):
    accounts = data['result']['data']
    log(f"Total cuentas: {len(accounts)}")

    with open('pld_saldos_cuentas.json', 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)

    log(f"\n{'USERNAME':<25} {'CLABE/CUENTA':<22} {'RAZON SOCIAL':<30} {'TX':<5} {'MONTO TOTAL':>15}")
    log("-" * 100)

    total_monto = 0
    for acc in sorted(accounts, key=lambda x: float(x.get('total_amount') or 0), reverse=True):
        username = acc.get('username', '?')
        cuenta = acc.get('account_number', '?')
        razon = (acc.get('razon_social') or '?')[:28]
        tx_count = acc.get('transaction_count', 0)
        monto = float(acc.get('total_amount') or 0)
        total_monto += monto
        log(f"  {username:<23} {cuenta:<22} {razon:<30} {tx_count:<5} ${monto:>14,.2f}")

    log("-" * 100)
    log(f"  TOTAL OPERADO: ${total_monto:>14,.2f}")
    log(f"  Cuentas únicas: {len(accounts)}")
else:
    log(f"Error: {code} | {json.dumps(data)[:500]}")

# 2. transaction/paginated — primeras 3 páginas
log("\n\n=== TRANSACCIONES DETALLADAS (paginadas) ===")
all_tx = []
for page in range(1, 6):
    code, data = api('POST', '/api/v1/transaction/paginated', {"page": page, "limit": 50})
    if data.get('success') and data.get('result', {}).get('data'):
        rows = data['result']['data']
        all_tx.extend(rows)
        total_rows = data['result'].get('total_rows', '?')
        total_pages = data['result'].get('total_pages', '?')
        log(f"  Pagina {page}/{total_pages}: {len(rows)} registros (total: {total_rows})")
    else:
        log(f"  Pagina {page}: {code} | no data")
        break

if all_tx:
    with open('pld_transacciones_detalle.json', 'w', encoding='utf-8') as f:
        json.dump(all_tx, f, indent=2, ensure_ascii=False)
    log(f"\nTotal transacciones extraidas: {len(all_tx)}")

    log(f"\n{'ID':<6} {'FECHA':<12} {'USUARIO':<22} {'DESTINO':<22} {'MONTO':>14} {'STATUS':<12}")
    log("-" * 95)
    for tx in all_tx[:30]:
        tx_id = tx.get('id', '?')
        fecha = (tx.get('create_date') or '?')[:10]
        user_id = (tx.get('user_id') or '?')[:20]
        dest = str(tx.get('dest_account_id') or tx.get('dest_bank_account') or '?')[:20]
        monto = float(tx.get('amount') or 0)
        status = tx.get('status', '?')
        log(f"  {tx_id:<6} {fecha:<12} {user_id:<22} {dest:<22} ${monto:>13,.2f} {status:<12}")

# 3. months — resumen mensual
log("\n\n=== RESUMEN MENSUAL ===")
code, data = api('GET', '/api/v1/transaction/months')
if data.get('success') and data.get('result', {}).get('data'):
    months = data['result']['data']
    meses = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    log(f"  {'MES':<6} {'TRANSACCIONES':>14} {'INUSUALES':>10} {'NO RECONOCIDAS':>16} {'NO APROBADAS':>14}")
    for m in months:
        mes_num = m.get('month', 0)
        mes_name = meses[mes_num] if 0 < mes_num <= 12 else str(mes_num)
        log(f"  {mes_name:<6} {m.get('transacciones', 0):>14} {m.get('inusuales', 0):>10} {m.get('no_reconocidas', 0):>16} {m.get('no_aprobadas', '0'):>14}")

# 4. inicios-sesion con diferentes user_ids
log("\n\n=== INICIOS DE SESION ===")
user_ids_to_try = []
for tx in all_tx:
    uid = tx.get('user_id')
    if uid and uid not in user_ids_to_try:
        user_ids_to_try.append(uid)
    if len(user_ids_to_try) >= 5:
        break

for uid in user_ids_to_try[:3]:
    code, data = api('GET', f'/api/v1/report/inicios-sesion?userId={uid}&startDate=2025-01-01&endDate=2026-07-25')
    if data.get('success') and data.get('result'):
        result = data['result']
        if isinstance(result, str):
            lines = result.strip().split('\n')
            log(f"  {uid[:20]}: {len(lines)} registros de login")
        else:
            log(f"  {uid[:20]}: {json.dumps(result)[:200]}")
    else:
        log(f"  {uid[:20]}: {code} | {json.dumps(data)[:200]}")

log("\nFIN.")
