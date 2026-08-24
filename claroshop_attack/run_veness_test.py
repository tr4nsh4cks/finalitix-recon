"""Upload Veness PHP implementation to server and run validation."""
import paramiko
import os

HOST = "157.180.98.220"
USER = "root"
PASS = "?hK7L3jH76vRT7"

LOCAL_DIR = r"c:\xampp\htdocs\pentagi\claroshop_attack"
FILES = ["Aes.php", "AesCtr.php", "veness_test.php"]

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

sftp = c.open_sftp()
try:
    sftp.mkdir("/root/veness")
except IOError:
    pass
for f in FILES:
    sftp.put(os.path.join(LOCAL_DIR, f), f"/root/veness/{f}")
    print(f"uploaded {f}")
sftp.close()

extra_args = " ".join(__import__("sys").argv[1:])
stdin, stdout, stderr = c.exec_command(f"cd /root/veness && php veness_test.php {extra_args}", timeout=120)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
import sys as _s
_safe = lambda t: t.encode("utf-8", errors="replace").decode("utf-8")
_buf = _safe(out) + ("\n--- STDERR ---\n" + _safe(err) if err else "")
_s.stdout.buffer.write(_buf.encode("utf-8", errors="replace"))
_s.stdout.buffer.write(b"\n")
c.close()
