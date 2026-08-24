// Probe de URLs candidatas del panel admin desde el nodo Jenkins (red interna)
def urls = [
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

def script = new StringBuilder()
script.append("for U in")
urls.each { script.append(" ").append(it) }
script.append("""; do
  CODE=$(curl -sk -o /tmp/resp.txt -w "%{http_code}|%{size_download}|%{redirect_url}" --connect-timeout 6 --max-time 12 -A "Mozilla/5.0" "$U")
  TITLE=$(grep -oiP '(?<=<title>)[^<]+' /tmp/resp.txt | head -1)
  echo "PROBE|$U|$CODE|$TITLE"
done
""")

def r = ["bash","-c", script.toString()].execute().text
println r
println "PROBE_DONE"
