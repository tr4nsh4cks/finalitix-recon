"""
Run a one-shot container on the remote docker host (via Jenkins RCE proxy)
and return its logs.
Usage:
  python docker_run.py <image> <cmd...> [--env K=V ...]
"""
import sys, os, json, time, subprocess, tempfile

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

def conf = [
    Image: "__IMAGE__",
    Cmd: new JsonSlurper().parseText('__CMD_JSON__'),
    Env: new JsonSlurper().parseText('__ENV_JSON__'),
    HostConfig: [NetworkMode: "bridge"],
    AttachStdout: true,
    AttachStderr: true
]

def created = http("POST", "/containers/create", conf, 30000)
println "CREATE_CODE=" + created.code
if (created.code != 201) { println created.body; return }
def cid = new JsonSlurper().parseText(created.body).Id
println "CID=" + cid

def started = http("POST", "/containers/" + cid + "/start", null, 30000)
println "START_CODE=" + started.code

// wait for exit
int status = -1
for (int i = 0; i < 24; i++) {
    def insp = http("GET", "/containers/" + cid + "/json", null, 15000)
    def j = new JsonSlurper().parseText(insp.body)
    if (!j.State.Running) { status = j.State.ExitCode; break }
    Thread.sleep(5000)
}
println "EXIT_CODE=" + status

def logs = http("GET", "/containers/" + cid + "/logs?stdout=1&stderr=1", null, 60000)
println "LOGS_BEGIN"
println logs.body
println "LOGS_END"

http("DELETE", "/containers/" + cid + "?force=1", null, 15000)
println "CLEANED"
'''


def run_container(image, cmd, env=None, timeout=180, entrypoint=None):
    env = env or []
    if entrypoint:
        cmd = cmd if isinstance(cmd, list) else [cmd]
    def groovy_sq(s):
        return s.replace("\\", "\\\\").replace("'", "\\'")
    ep_json = groovy_sq(json.dumps(entrypoint)) if entrypoint else None
    script = (GROOVY
              .replace("__DOCKER__", DOCKER_HOST)
              .replace("__IMAGE__", image.replace("\\", "\\\\").replace('"', '\\"'))
              .replace("__CMD_JSON__", groovy_sq(json.dumps(cmd)))
              .replace("__ENV_JSON__", groovy_sq(json.dumps(env))))
    if ep_json:
        script = script.replace(
            "Env: new JsonSlurper().parseText('" + groovy_sq(json.dumps(env)) + "'),",
            "Env: new JsonSlurper().parseText('" + groovy_sq(json.dumps(env)) + "'),\n    Entrypoint: new JsonSlurper().parseText('" + ep_json + "'),")
    with tempfile.NamedTemporaryFile("w", suffix=".groovy", delete=False, dir=HERE, encoding="utf-8") as f:
        f.write(script)
        tmp = f.name
    try:
        out = subprocess.run([sys.executable, JENKINS_EXEC, tmp], capture_output=True, timeout=timeout)
        raw = out.stdout.decode("utf-8", errors="replace") + out.stderr.decode("utf-8", errors="replace")
        return raw
    finally:
        os.unlink(tmp)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    import shlex, base64
    image = args[0]
    env = []
    cmd = []
    entrypoint = None
    i = 1
    while i < len(args):
        if args[i] == "--env":
            env.append(args[i + 1])
            i += 2
        elif args[i] == "--entrypoint":
            entrypoint = [args[i + 1]]
            i += 2
        elif args[i] == "--shfile":
            with open(args[i + 1], "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode()
            cmd = ["-c", f"echo {b64} | base64 -d | sh"]
            entrypoint = ["/bin/sh"]
            i += 2
        else:
            cmd.append(args[i])
            i += 1
    if len(cmd) == 1:
        cmd = shlex.split(cmd[0])
    result = run_container(image, cmd, env, entrypoint=entrypoint)
    sys.stdout.buffer.write(result.encode("utf-8", errors="replace"))
