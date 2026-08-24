def pyScript = '''
import socket, sys
reload(sys)
sys.setdefaultencoding("utf-8")

for port in [13306, 13307, 13308, 23456]:
    print "=== Port %d ===" % port
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(("127.0.0.1", port))
        data = s.recv(1024)
        print "  Connected! Got %d bytes" % len(data)
        print "  Hex: " + data.encode("hex")
        print "  ASCII: " + repr(data[:200])
        # Check if it looks like MySQL handshake
        if len(data) >= 5 and data[4] == chr(0):
            print "  Looks like MySQL handshake!"
            # Parse version
            i = 5
            ver = ""
            while i < len(data) and data[i] != chr(0):
                ver += data[i]
                i += 1
            print "  MySQL version: " + ver
        s.close()
    except Exception as e:
        print "  ERROR: " + str(e)
    print
'''

def encoded = pyScript.bytes.encodeBase64().toString()
def cmd = ["bash", "-c", "echo '${encoded}' | base64 -d > /tmp/porttest.py && python /tmp/porttest.py 2>&1"]
def proc = cmd.execute()
def out = new StringBuilder()
proc.consumeProcessOutput(out, new StringBuilder())
proc.waitForOrKill(15000)
println out.toString()
