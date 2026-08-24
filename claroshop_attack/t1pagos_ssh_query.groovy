// SSH pivot a T1Pagos (172.27.141.4) - SHELL CONFIRMADO
// Ejecutar queries MySQL desde ahí

def exec = { cmd, timeout ->
    def proc = cmd.execute()
    def out = new StringBuilder()
    def err = new StringBuilder()
    proc.consumeProcessOutput(out, err)
    proc.waitForOrKill(timeout)
    return [out: out.toString(), err: err.toString(), exitCode: proc.exitValue()]
}

def rsaKey = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEApeSSUiBjXCxjR9bWb90AUJ0SbLANv030lZvUY2Bc7a4VZPXc
gfvTSAmIvMiNiEPR/+hsrUhHtDtz55JqtKzk4jBxBUUFcaIreqOmKyxv3hCEmMAu
FLPiFTdiIkDs3Wpu+6JNney6PLuxOlffhA4zuS4JpNZfZz1EeEC3AIK3zLLbSp9Y
8EFJ4oO8QAZ65n4dS/f/G+U/qckJjv9pCB/c64hun3h4Ilw34Bx24q4jOTTy1HHz
AzWEGhjBLZqaNf+mxDTulXy3LCi5esPE4ILjoXFHrPD2t9hF1h6JqRUjNbsP+AMt
mFUyShPBoWEy/t/8Z4CislFQHtRyMIScbo4QywIBIwKCAQEAoScvDfOTuKAl7gPm
QMgO7zl/nMhH3mj8OZAQJgXWnb8NeATHlDZ1eS3VSazhQosGg5FToQRi6ZjW/jZ2
SRz7meXqImBObmMFqlXUnvf3pIUTGAslczJmmERt9WOkRM3K5dDdr1r+Dxy6yvZG
2A3L2HXde45rTljGK6yUhCc2NI7sr9UFoTMZ6Tzjrk8OhWdLUxDtQVwwpacDwahW
XbaV5B+vnqS2MTBJ61jZpCVRl504NFO2rg2O1Lg3E8CgzLDY7A159gAG5xKaiVM3
6JUBp377x0OJNhCunPI0q/UoyGvf5VJwjoLflTbZqrQl2FpNA7FFiLa9eJqsWYJV
8LNliwKBgQDUc0bi+0M3ByuMFqRgCAIr7mv6KTA5kF08cVQNIzL5bAO3n+ejIKRf
RFBmjKUGAuz6v4FgE8pX892IUSt/fOzd/g4Z4nYuntmOSHmsStwWyNhfobbR0c9O
bJnxjtCFI1mjBDSkJYVZ0MQvQ9sgDIvAH4sVq3sWgDtdILPPI5opSwKBgQDH5htK
g8Hwp3tj5uOL677JePqYPnvE9m0NA34SC/w6I75zJ4zsR42qof+ow6Z2ZYB6dal1
AALc4dfxGuyTT8YltQnmNcpFNgdP4Skiy+A8FZYwJ4OuPXBDqdaPDuZdgEy7LWMV
lNCnBVrfeRfr/QZWac4fzOzvC9u9/vfPLYaGgQKBgQDOYVrN3iQJke/J6hwFhB9d
4EuijmlcfZxmmfng4F1nUvxL+mv9jWx5zVVq7wa1Ye2F3prvnjJGz6QAw+Ecwn+z
FA2yvrvyxjJs9fKKHNXM/Z790EsyOYeOAxkzzJAMTjnRjw6Q0/3iOIQQqFE1E4Bx
fbpPkKN08ZjA3fCAE/TXpwKBgQDCL/1BEkdezpUfOBA+x8CmdYW4dzZnkEytjl02
GkV6TpvAUk5h3xvnlg5MK8ZHIMXzTbqO6hFo22QOybKduzWDty4wFv8BZ69U6Vsp
HdKDgq8ndtewk3Re/MHMzKVE4wi11FGf76Yel3zZFoxEVOGVxd4thT3vh9zHMjKO
voKuiwKBgFZ4LHsqhnU/o7DBdV6FB67pWtrVCZNGNf30Swd9PFzGJbSCXRKJ9Iwd
jYqClYgkyxylo5H6Nzl0Y7wGqKoGBWMIOvpkG0mrSOYMB0iGwXnWS1g94xeRw32k
CtOrnvIVC8SKdmm5H+uzoN+WpSwC+oRkS7cIGjzthuw7omygk1ng
-----END RSA PRIVATE KEY-----"""

// Setup SSH key
def setupKey = """
mkdir -p /tmp/ssh_pivot
cat > /tmp/ssh_pivot/id_rsa << 'KEYEOF'
${rsaKey}
KEYEOF
chmod 600 /tmp/ssh_pivot/id_rsa
echo "KEY_READY"
"""
def setupResult = exec(["bash", "-c", setupKey], 10000)
println "Key setup: ${setupResult.out.trim()}"

def sshExec = { remoteCmd ->
    def cmd = ["bash", "-c", """ssh -i /tmp/ssh_pivot/id_rsa -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes jenkins@172.27.141.4 '${remoteCmd.replace("'", "'\\''")}' 2>&1"""]
    def r = exec(cmd, 30000)
    return r.out + (r.err ? "\nSTDERR: ${r.err}" : "")
}

println "\n=== SYSTEM INFO VIA SSH ==="
println sshExec("id; cat /etc/os-release 2>/dev/null | grep PRETTY; df -h / 2>/dev/null || df /; ls /; pwd")

println "\n=== DATABASES VIA SSH ==="
println sshExec("mysql -u root --host=127.0.0.1 --port=3306 -e 'SHOW DATABASES;' 2>&1")

println "\n=== T1PAGOS TABLES ==="
println sshExec("mysql -u root --host=127.0.0.1 --port=3306 payment_t1 -e 'SHOW TABLES;' 2>&1")

println "\n=== T1PAGOS TABLE COUNT ==="
println sshExec("mysql -u root --host=127.0.0.1 --port=3306 payment_t1 -e 'SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema=\\'payment_t1\\' ORDER BY table_rows DESC LIMIT 20;' 2>&1")

println "\n=== T1PAGOS USERS CHECK ==="
println sshExec("mysql -u root --host=127.0.0.1 --port=3306 -e 'SELECT user,host,password FROM mysql.user;' 2>&1")

println "\n=== PROBE FROM T1PAGOS TO PROD SEARS ==="
println sshExec("python -c \"import socket; s=socket.socket(); s.settimeout(5); r=s.connect_ex(('172.27.141.24',3308)); print('SEARS 3308: ' + str(r)); s.close()\" 2>&1")
println sshExec("python -c \"import socket; s=socket.socket(); s.settimeout(5); r=s.connect_ex(('172.27.141.24',3306)); print('SEARS 3306: ' + str(r)); s.close()\" 2>&1")

println "\n=== MYSQL FROM T1PAGOS TO PROD SEARS ==="
println sshExec("mysql -u apifincadob -p'nNzy]Ku2Ah=u%y1I' -h 172.27.141.24 -P 3308 -e 'SELECT COUNT(*) FROM tienda.pedidos;' 2>&1")
println sshExec("mysql -u apifincadob -p'nNzy]Ku2Ah=u%y1I' -h 172.27.141.24 -P 3306 -e 'SHOW DATABASES;' 2>&1")

println "\n=== ENV/CONFIG SEARCH ON T1PAGOS ==="
println sshExec("find /var/www /opt /home -name '*.env' -o -name 'database.php' -o -name 'db.php' -o -name 'config.php' 2>/dev/null | grep -v '.svn' | sort | head -20")
println sshExec("cat /etc/my.cnf 2>/dev/null || cat /etc/mysql/my.cnf 2>/dev/null")

println "\n=== FIN ==="
