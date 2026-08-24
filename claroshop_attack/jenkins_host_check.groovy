// Check Jenkins container for host escape vectors
println "=== docker.sock ==="
println new File("/var/run/docker.sock").exists() ? "DOCKER_SOCK EXISTS" : "no docker.sock"
println "=== mounts ==="
println new File("/proc/mounts").text.readLines().grep(~/.*(docker|host|\/proc|\/sys).*/).join("\n").take(2000)
println "=== env ==="
System.getenv().each { k, v -> if (k =~ /(?i)(host|docker|kube|jenkins)/) println "$k=$v" }
println "=== hostname ==="
println "hostname".execute().text
println "=== capabilities ==="
try { println new File("/proc/1/status").text.readLines().grep(~/Cap.*/).join("\n") } catch (e) { println e.message }
