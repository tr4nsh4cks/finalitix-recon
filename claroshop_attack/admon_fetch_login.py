#!/usr/bin/env python3
# Fetch login pages de los paneles AXII activos desde nodo Jenkins
import base64, sys
from admonplaza_query import jenkins_exec

sys.stdout.reconfigure(errors='replace')

bash = r"""
for U in "https://axii.admin.sears.com.mx/login.php" "https://axii.admin.claroshop.com/login.php" "https://axii.admin.sanborns.com.mx/login.php"; do
  echo "===== $U ====="
  curl -sk --connect-timeout 6 --max-time 12 -A "Mozilla/5.0" "$U" | head -c 3000
  echo
done
echo FETCH_DONE
"""

bash_b64 = base64.b64encode(bash.encode()).decode()
groovy = 'def r = ["bash","-c","echo %s | base64 -d | bash"].execute().text\nprintln r\n' % bash_b64
out = jenkins_exec(groovy, timeout=180)
print(out)
