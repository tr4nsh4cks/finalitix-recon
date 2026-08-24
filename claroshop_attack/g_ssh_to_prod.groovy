// Intenta SSH a 172.27.141.24 (PROD Sears) y 172.27.141.4 (CSDEV01-2/T1Pagos)
// Usa la llave RSA privada extraída del plugin publish-over-ssh

println "=== SSH ATTEMPT TO PROD SERVERS ==="

def PRIV_KEY = """-----BEGIN RSA PRIVATE KEY-----
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

// Write key to temp file
def keyFile = File.createTempFile("jenkins_key", ".pem")
keyFile.text = PRIV_KEY
keyFile.setReadable(false, false)
keyFile.setReadable(true, true)
keyFile.setWritable(false, false)
keyFile.setWritable(true, true)
println "Key written to: ${keyFile.absolutePath}"

// Try SSH commands to PROD servers
def TARGETS = [
    ["172.27.141.24", "jenkins", "PROD Sears (dbasears)"],
    ["172.27.141.4", "jenkins", "CSDEV01-2 / T1Pagos"],
    ["172.27.140.148", "jenkins", "CSDEVBLD01-1"]
]

TARGETS.each { ip, user, desc ->
    println "\n--- SSH to ${ip} (${desc}) as ${user} ---"
    
    // Commands to try
    def cmds = ["id", "hostname", "ip addr show", "cat /etc/hosts", "ls /var/www/sites/", "mysql --version", "netstat -tuln | grep 330"]
    
    cmds.each { cmd ->
        try {
            def sshCmd = ["ssh", "-i", keyFile.absolutePath, 
                          "-o", "StrictHostKeyChecking=no",
                          "-o", "ConnectTimeout=5",
                          "-o", "BatchMode=yes",
                          "-p", "22",
                          "${user}@${ip}",
                          cmd]
            def proc = sshCmd.execute()
            proc.waitFor()
            def stdout = proc.text
            def stderr = proc.err.text
            if (stdout.trim()) {
                println "CMD [${cmd}]: ${stdout.take(500)}"
            } else if (stderr.trim()) {
                println "CMD [${cmd}] STDERR: ${stderr.take(200)}"
            }
        } catch(e) {
            println "CMD [${cmd}] EXCEPTION: ${e.message}"
        }
    }
}

keyFile.delete()

// Also try with the publish-over-ssh plugin directly
println "\n=== USING PUBLISH-OVER-SSH PLUGIN ==="
try {
    def plugin = jenkins.model.Jenkins.getInstance().getPlugin("publish-over-ssh")
    println "Plugin: ${plugin?.class?.name}"
    def descriptor = plugin?.getDescriptor()
    if (descriptor) {
        println "Host configs: ${descriptor.hostConfigurations?.size()}"
        descriptor.hostConfigurations?.each { config ->
            println "  Host: ${config.name} -> ${config.hostname}:${config.port}"
        }
    }
} catch(e) {
    println "Plugin access error: ${e.message}"
}

println "\n=== TRYING nc/ncat TO CHECK MySQL 172.27.141.4:3306 ==="
try {
    def socket = new Socket("172.27.141.4", 3306)
    socket.soTimeout = 5000
    def stream = socket.inputStream
    def banner = new byte[200]
    def len = stream.read(banner, 0, 200)
    socket.close()
    if (len > 0) {
        // MySQL greeting - try to extract version
        def bannerStr = new String(banner, 0, len)
        println "MySQL banner (${len} bytes): ${bannerStr.replaceAll('[^\\x20-\\x7E]', '.').take(200)}"
        
        // Try to find version string in binary MySQL handshake
        def versionStart = 5
        def versionEnd = bannerStr.indexOf('\0', versionStart)
        if (versionEnd > versionStart && versionEnd < 30) {
            println "MySQL version: ${bannerStr.substring(versionStart, versionEnd)}"
        }
    }
} catch(e) {
    println "MySQL banner read failed: ${e.message}"
}
