// Quick connectivity test to PROD Sears via internal IP
def pyScript = '''
import socket, struct, hashlib, sys

targets = [
    ("172.27.141.24", 3308, "apifincadob", "nNzy]Ku2Ah=u%y1I"),
    ("172.27.141.24", 3306, "apifincadob", "nNzy]Ku2Ah=u%y1I"),
]

for host, port, user, pw in targets:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))
        # Read greeting
        h = b""
        while len(h) < 4: h += s.recv(4 - len(h))
        l = struct.unpack("<I", h[:3] + b"\\x00")[0]
        d = b""
        while len(d) < l: d += s.recv(l - len(d))
        version = d[1:d.find(b"\\x00", 1)].decode("latin1")
        print("%s:%d OPEN - MySQL %s" % (host, port, version))
        s.close()
    except Exception as e:
        print("%s:%d CLOSED - %s" % (host, port, str(e)))
'''

def encoded = pyScript.bytes.encodeBase64().toString()
def cmd = ["bash", "-c", "echo '${encoded}' | base64 -d > /tmp/tp.py && python /tmp/tp.py 2>&1"]
def proc = cmd.execute()
def out = new StringBuilder()
proc.consumeProcessOutput(out, new StringBuilder())
proc.waitForOrKill(15000)
println out.toString()
