def cmd1 = ["bash", "-c", "ps aux | grep ssh | grep -v grep"]
def proc1 = cmd1.execute()
def out1 = new StringBuilder()
proc1.consumeProcessOutput(out1, new StringBuilder())
proc1.waitForOrKill(10000)
println "=== SSH PROCESSES ==="
println out1.toString()

def cmd2 = ["bash", "-c", "ss -tlnp 2>/dev/null | grep -E '1330|1331' || netstat -tlnp 2>/dev/null | grep -E '1330|1331'"]
def proc2 = cmd2.execute()
def out2 = new StringBuilder()
proc2.consumeProcessOutput(out2, new StringBuilder())
proc2.waitForOrKill(10000)
println "=== PORTS 13306-13310 ==="
println out2.toString()

def cmd3 = ["bash", "-c", "ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null"]
def proc3 = cmd3.execute()
def out3 = new StringBuilder()
proc3.consumeProcessOutput(out3, new StringBuilder())
proc3.waitForOrKill(10000)
println "=== ALL LISTENING PORTS ==="
println out3.toString()
