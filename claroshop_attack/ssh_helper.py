"""SSH helper for ClaroShop dump analysis on Hetzner server."""
import paramiko
import sys
import time

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

def get_client():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=USER, password=PASS, timeout=30, banner_timeout=30)
    return c

def run(client, cmd, timeout=120):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    rc = stdout.channel.recv_exit_status()
    return rc, out, err

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "uname -a"
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    c = get_client()
    rc, out, err = run(c, cmd, timeout)
    print(f"[rc={rc}]")
    if out:
        print(out)
    if err:
        print("--- STDERR ---")
        print(err)
    c.close()
