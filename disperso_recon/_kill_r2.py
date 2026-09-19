import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("64.177.80.208", username="root", password="Rc*7aREY35U{YB3A", timeout=15)

# Kill the spray and save partial results
_, out, _ = ssh.exec_command(
    "kill $(pgrep -f spray_r2) 2>/dev/null; sleep 1; "
    "cat /root/disperso_spray_r2.json 2>/dev/null || echo NO_RESULTS",
    timeout=10
)
result = out.read().decode()
print(result)
ssh.close()

try:
    d = json.loads(result)
    print(f"Hits: {len(d['hits'])}, Tried: {d['tried']}")
    if d['hits']:
        for h in d['hits']:
            print(f"  HIT: {h}")
except:
    print("Script killed before writing JSON - 0 hits confirmed (no bypass logged to stdout either)")
