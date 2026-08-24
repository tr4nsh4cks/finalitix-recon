import subprocess,os,base64,struct,sys
PASSWORD="K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4"
pw=PASSWORD[:32]

def aes_ecb(key_raw,data_raw):
    open('/tmp/_ai','wb').write(data_raw)
    kh=key_raw.encode('hex')
    os.system('openssl enc -aes-256-ecb -K %s -nopad -nosalt -in /tmp/_ai -out /tmp/_ao 2>/dev/null'%kh)
    return open('/tmp/_ao','rb').read()

k16=aes_ecb(pw,pw[:16])
fk=k16+k16

def decrypt(b64):
    try:
        raw=base64.b64decode(b64.strip())
    except:
        return '?b64err'
    if len(raw)<9:
        return '?short'
    nonce=raw[:8]
    ct=raw[8:]
    nb=(len(ct)+15)//16
    pt=''
    for b in range(nb):
        cb=bytearray(16)
        for i in range(8):
            cb[i]=ord(nonce[i])
        cb[15]=b&0xff
        cb[14]=(b>>8)&0xff
        cb[13]=(b>>16)&0xff
        cb[12]=(b>>24)&0xff
        ks=aes_ecb(fk,str(cb))
        blk=ct[b*16:(b+1)*16]
        for i in range(len(blk)):
            pt+=chr(ord(blk[i])^ord(ks[i]))
    return pt.rstrip('\x00')
