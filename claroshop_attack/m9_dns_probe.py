import socket, struct, sys

def dns_query(host, server='8.8.8.8'):
    tid = 0x1234
    flags = 0x0100
    header = struct.pack('>HHHHHH', tid, flags, 1, 0, 0, 0)
    qname = b''.join(chr(len(p)) + p.encode() for p in host.split('.')) + b'\x00'
    question = qname + struct.pack('>HH', 1, 1)
    pkt = header + question
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(6)
    try:
        s.sendto(pkt, (server, 53))
        data, _ = s.recvfrom(4096)
    except Exception as e:
        print host, '-> DNS FAIL', e
        return []
    finally:
        s.close()
    ancount = struct.unpack('>H', data[6:8])[0]
    i = 12
    while ord(data[i]) != 0:
        i += ord(data[i]) + 1
    i += 5
    ips = []
    for _ in range(ancount):
        if ord(data[i]) & 0xC0 == 0xC0:
            i += 2
        else:
            while data[i] != 0:
                i += ord(data[i]) + 1
            i += 1
        rtype, rclass, ttl, rdlen = struct.unpack('>HHIH', data[i:i+10])
        i += 10
        rdata = data[i:i+rdlen]
        i += rdlen
        if rtype == 1 and rdlen == 4:
            ips.append(socket.inet_ntoa(rdata))
    return ips

hosts = ['t1envios-shard-00-00.kqoop.mongodb.net','t1envios-shard-00-01.kqoop.mongodb.net','t1envios-shard-00-02.kqoop.mongodb.net','t1envios-shard-00-03.kqoop.mongodb.net']
allips = set()
for h in hosts:
    ips = dns_query(h)
    print h, '->', ips
    allips.update(ips)

print '--- TCP test a IPs reales Atlas ---'
for ip in sorted(allips):
    s = socket.socket()
    s.settimeout(6)
    try:
        s.connect((ip, 27017))
        print ip, ':27017 OK'
    except Exception as e:
        print ip, ':27017 FAIL', e
    finally:
        s.close()

print '--- DNS interno (system resolver) para comparar ---'
for h in hosts[:1] + ['t1envios.kqoop.mongodb.net']:
    try:
        print h, '->', socket.gethostbyname(h)
    except Exception as e:
        print h, 'FAIL', e
print 'DONE'
