import java.net.Socket
import java.net.InetSocketAddress
import java.util.concurrent.*

// 1) Test desde el Jenkins MASTER (red interna 172.27.x)
def targets = [
  'dbasears.mrc-services.io:3308',
  '172.27.141.24:3308',
  '172.27.141.24:3306',
  '172.27.141.4:3310',
  '172.27.141.4:3306',
  '172.27.140.148:4243',
  '172.27.140.151:22',
]

def pool = Executors.newFixedThreadPool(8)
def results = Collections.synchronizedList([])
targets.each { t ->
  pool.submit({
    def parts = t.split(':')
    def hn = parts[0]; def pn = parts[1] as int
    try {
      def s = new Socket()
      s.connect(new InetSocketAddress(hn, pn), 5000)
      def banner = ''
      try {
        s.setSoTimeout(3000)
        def inS = s.getInputStream()
        def buf = new byte[128]
        def n = inS.read(buf)
        if (n > 0) banner = new String(buf, 0, n).replaceAll('[^\\x20-\\x7E]', '.')
      } catch (ignored) {}
      s.close()
      results.add("MASTER|${t}|OPEN|${banner}")
    } catch (Exception e) {
      results.add("MASTER|${t}|CLOSED|${e.class.simpleName}: ${e.message}")
    }
  } as Runnable)
}
pool.shutdown()
pool.awaitTermination(30, TimeUnit.SECONDS)
results.sort().each { println(it) }

// 2) DNS check desde master
try {
  def addr = InetSocketAddress.createUnresolved('dbasears.mrc-services.io', 3308)
  def resolved = java.net.InetAddress.getByName('dbasears.mrc-services.io')
  println("DNS|dbasears.mrc-services.io|" + resolved.getHostAddress())
} catch (Exception e) {
  println("DNS|dbasears.mrc-services.io|FAIL: " + e.message)
}
println("MASTER_PROBE_DONE")
