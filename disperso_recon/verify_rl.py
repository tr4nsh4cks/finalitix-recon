"""Verify rate limit cleared."""
import paramiko
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('64.177.83.195', username='root', password='Nm9.#p)WzifT.fo2', timeout=15)
_, s, _ = c.exec_command('curl -sk -X POST https://soporte.disperso.com/api/auth/login -H "Content-Type: application/json" -d \'{"email":"probe@probe.com","password":"probe"}\' -w "\\nHTTP_CODE:%{http_code}" --max-time 10 2>&1')
print(s.read().decode().strip()[:300])
c.close()
