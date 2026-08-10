import javax.net.ssl.*
import java.security.cert.X509Certificate
def tm = [new X509TrustManager() {
    public X509Certificate[] getAcceptedIssuers() { return null }
    public void checkClientTrusted(X509Certificate[] c, String t) {}
    public void checkServerTrusted(X509Certificate[] c, String t) {}
}] as TrustManager[]
def sc = SSLContext.getInstance('TLS')
sc.init(null, tm, new java.security.SecureRandom())
def sf = sc.getSocketFactory()
['172.30.2.90','172.25.13.13','172.25.13.15','172.25.13.50'].each { h ->
    println '=== ' + h + ' ==='
    try {
        def sock = sf.createSocket()
        sock.connect(new InetSocketAddress(h, 443), 4000)
        sock.setSoTimeout(4000)
        sock.startHandshake()
        def cert = sock.getSession().getPeerCertificates()[0]
        println 'CN: ' + cert.getSubjectX500Principal().toString()
        println 'Issuer: ' + cert.getIssuerX500Principal().toString()
        try {
            def sans = cert.getSubjectAlternativeNames()
            if (sans) { sans.each { println 'SAN: ' + it } }
        } catch (e3) {}
        sock.close()
    } catch (e) {
        println 'ERR ' + e.getClass().getSimpleName() + ': ' + e.getMessage()
    }
    try {
        def sock2 = new Socket()
        sock2.connect(new InetSocketAddress(h, 443), 4000)
        sock2.setSoTimeout(4000)
        def out = sock2.getOutputStream()
        def req = 'GET / HTTP/1.0\r\nHost: ' + h + '\r\nUser-Agent: Mozilla/5.0\r\n\r\n'
        out.write(req.getBytes('UTF-8'))
        out.flush()
        def inp = sock2.getInputStream()
        def buf = new byte[2048]
        def rd = inp.read(buf)
        if (rd > 0) {
            def resp = new String(buf, 0, rd, 'UTF-8')
            resp.readLines().take(8).each { println 'R: ' + it }
        }
        sock2.close()
    } catch (e) {
        println 'HTTP-ERR ' + e.getClass().getSimpleName()
    }
}
println 'DONE'
