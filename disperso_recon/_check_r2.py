import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("64.177.80.208", username="root", password="Rc*7aREY35U{YB3A", timeout=15)

_, out, _ = ssh.exec_command("ps aux | grep spray_r2 | grep -v grep; cat /root/disperso_spray_r2.json 2>/dev/null || echo NO_RESULTS_YET", timeout=15)
print(out.read().decode())
ssh.close()
