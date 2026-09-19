import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("64.177.80.208", username="root", password="Rc*7aREY35U{YB3A", timeout=15)

# Check if still running and get any log output
_, out, _ = ssh.exec_command(
    "pgrep -a python3 | grep spray; "
    "cat /root/disperso_spray_r2.json 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(\"HITS:\", d[\"hits\"], \"TRIED:\", d[\"tried\"])' 2>/dev/null || echo NO_JSON_YET",
    timeout=10
)
print(out.read().decode())
ssh.close()
