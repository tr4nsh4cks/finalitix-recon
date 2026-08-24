import sys

# Generates LF-only shell scripts for docker_run --shfile
scripts = {
    "hunt_envgen.sh": """ls -la /opt/env-generator/ 2>/dev/null
echo "=== ENVGEN ==="
for f in /opt/env-generator/*; do echo "--- $f ---"; cat "$f" 2>/dev/null; done
echo "=== KS ==="
grep -E "rootpw|^user|password" /root/anaconda-ks.cfg /root/original-ks.cfg 2>/dev/null | head -20
echo "=== DONE ==="
""",
}

if __name__ == "__main__":
    name = sys.argv[1]
    with open(name, "w", newline="\n") as f:
        f.write(scripts[name])
    print("written LF:", name)
