def cmd = ["bash", "-c", "which php php7 php8 2>/dev/null; php --version 2>&1 | head -1"]
def proc = cmd.execute()
def out = new StringBuilder()
def err = new StringBuilder()
proc.consumeProcessOutput(out, err)
proc.waitForOrKill(10000)
println out.toString()
