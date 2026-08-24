// Fast TCP probe: Jenkins → T1Pagos (172.27.141.4:3310) y PROD Sears
// Timeout corto, respuesta rápida

def pyScript = '''
import socket, struct

targets = [
    ("172.27.141.4", 3310, "T1Pagos DB"),
    ("172.27.141.4", 3306, "T1Pagos MySQL default"),
    ("172.27.141.4", 22,   "T1Pagos SSH"),
    ("172.27.141.24", 3308, "PROD Sears DB"),
    ("172.27.141.24", 3306, "PROD Sears MySQL default"),
    ("172.27.141.24", 22,  "PROD Sears SSH"),
    ("dbasears.mrc-services.io", 3308, "PROD Sears DNS"),
    ("172.27.141.25", 8080, "Proxy"),
    ("172.27.140.134", 80,  "Jenkins host"),
    ("console.dev.amxnova.net", 8443, "OpenShift console"),
]

for host, port, name in targets:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        r = s.connect_ex((host, port))
        if r == 0:
            # Try to read banner
            try:
                s.settimeout(2)
                banner = s.recv(128)
                print("OPEN  %-40s %s:%d  BANNER: %s" % (name, host, port, repr(banner[:60])))
            except:
                print("OPEN  %-40s %s:%d" % (name, host, port))
        else:
            print("CLOSED %-40s %s:%d  errno=%d" % (name, host, port, r))
        s.close()
    except Exception as e:
        print("ERROR %-40s %s:%d  %s" % (name, host, port, str(e)))

print("PROBE DONE")
'''

def encoded = pyScript.bytes.encodeBase64().toString()
def cmd = ["bash", "-c", "echo '${encoded}' | base64 -d > /tmp/probe.py && python /tmp/probe.py 2>&1"]
def proc = cmd.execute()
def out = new StringBuilder()
proc.consumeProcessOutput(out, new StringBuilder())
proc.waitForOrKill(60000)
println out.toString()
