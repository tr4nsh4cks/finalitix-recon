// Enumerate ALL containers via Docker API (including stopped)
def dockerApi = "http://172.27.140.148:4243"

def httpGet(String urlStr) {
    def url = new URL(urlStr)
    def conn = (HttpURLConnection) url.openConnection()
    conn.setRequestMethod("GET")
    conn.setConnectTimeout(10000)
    conn.setReadTimeout(15000)
    def code = conn.getResponseCode()
    def body
    if (code >= 400) {
        body = conn.getErrorStream()?.getText("UTF-8")
    } else {
        body = conn.getInputStream().getText("UTF-8")
    }
    conn.disconnect()
    return [code: code, body: body]
}

// Docker version info
def ver = httpGet(dockerApi + "/version")
println "=== DOCKER VERSION ==="
println "HTTP " + ver.code
println ver.body

// List ALL containers
def r = httpGet(dockerApi + "/containers/json?all=true&size=false")
println ""
println "=== CONTAINERS (all) HTTP " + r.code + " ==="
println r.body
