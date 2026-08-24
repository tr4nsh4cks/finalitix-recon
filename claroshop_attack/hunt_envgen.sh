ls -la /opt/env-generator/ 2>/dev/null
echo "=== ENVGEN ==="
for f in /opt/env-generator/*; do echo "--- $f ---"; cat "$f" 2>/dev/null; done
echo "=== KS ==="
grep -E "rootpw|^user|password" /root/anaconda-ks.cfg /root/original-ks.cfg 2>/dev/null | head -20
echo "=== DONE ==="
