def r = ["bash","-c","""python -c "
import sys,base64,hashlib,subprocess,os,struct,socket
reload(sys);sys.setdefaultencoding('utf-8')

key_raw='K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4'
samples=['L7nSVdHR0dF/VLlW9yCgBC9SZOQ=','eLPSVaOjo6NkY4jy+Nafepcz2JgypSA=','T6rSVVZWVlaw9G6mohmb5q9E3Hk=','163SVdra2tq4DF0DBUPMIw+8Wns=']

keys={
 'raw32': key_raw[:32].encode('hex'),
 'raw16': key_raw[:16].encode('hex'),
 'md5': hashlib.md5(key_raw).hexdigest(),
 'sha1_16': hashlib.sha1(key_raw).digest()[:16].encode('hex'),
 'sha256_32': hashlib.sha256(key_raw).hexdigest()[:64],
 'sha256_16': hashlib.sha256(key_raw).hexdigest()[:32],
}
print 'Keys generated:'
for n,k in keys.items(): print ' ',n,'=',k

for s in samples:
 raw=base64.b64decode(s)
 header=raw[:4]
 payload=raw[4:20]
 extra=raw[20:] if len(raw)>20 else ''
 print '\\nSample:',s
 print ' full_hex:',raw.encode('hex')
 print ' header:',header.encode('hex'),'payload16:',payload.encode('hex'),'extra:',extra.encode('hex') if extra else 'none'
 
 # Try each key with AES-256-ECB on 16-byte payload (skip header)
 for name,khex in keys.items():
  if len(khex)>=64:
   f='/tmp/p.bin'
   open(f,'wb').write(payload)
   cmd='openssl enc -aes-256-ecb -d -K %s -nopad -in %s 2>/dev/null' % (khex[:64],f)
   p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   o,e=p.communicate()
   if o:
    printable=''.join(c if c.isdigit() or c.isalpha() else '.' for c in o)
    print '  AES256-ECB skip4 key=%s -> hex:%s ascii:%s' % (name,o.encode('hex'),printable)

  # AES-128-ECB on payload
  if len(khex)>=32:
   f='/tmp/p.bin'
   open(f,'wb').write(payload)
   cmd='openssl enc -aes-128-ecb -d -K %s -nopad -in %s 2>/dev/null' % (khex[:32],f)
   p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   o,e=p.communicate()
   if o:
    printable=''.join(c if c.isdigit() or c.isalpha() else '.' for c in o)
    print '  AES128-ECB skip4 key=%s -> hex:%s ascii:%s' % (name,o.encode('hex'),printable)

 # XOR with key on full blob
 out=''
 for i,b in enumerate(raw):
  out+=chr(ord(b)^ord(key_raw[i%len(key_raw)]))
 digits_count=sum(1 for c in out if c.isdigit())
 print '  XOR-full -> digits:%d repr:%s' % (digits_count, repr(out[:24]))

 # XOR with key on payload only (skip 4)
 out2=''
 for i,b in enumerate(payload):
  out2+=chr(ord(b)^ord(key_raw[i%len(key_raw)]))
 digits2=sum(1 for c in out2 if c.isdigit())
 print '  XOR-payload -> digits:%d repr:%s' % (digits2, repr(out2[:20]))

 # Try BF-ECB on 16 bytes (blowfish accepts variable key)
 for name,khex in [('raw32',key_raw[:32].encode('hex')),('md5',hashlib.md5(key_raw).hexdigest())]:
  f='/tmp/p.bin'
  # Blowfish needs 8-byte blocks, try first 16 bytes
  open(f,'wb').write(payload[:16])
  cmd='openssl enc -bf-ecb -d -K %s -nopad -in %s 2>/dev/null' % (khex,f)
  p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  o,e=p.communicate()
  if o:
   printable=''.join(c if c.isdigit() or c.isalpha() else '.' for c in o)
   print '  BF-ECB key=%s -> hex:%s ascii:%s' % (name,o.encode('hex'),printable)

 # Try DES-EDE3 (Triple DES) 
 for name,khex in [('raw24',key_raw[:24].encode('hex')),('md5x1.5',(hashlib.md5(key_raw).hexdigest()+hashlib.md5(key_raw).hexdigest())[:48])]:
  f='/tmp/p.bin'
  open(f,'wb').write(payload[:16])
  cmd='openssl enc -des-ede3 -d -K %s -nopad -in %s 2>/dev/null' % (khex,f)
  p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  o,e=p.communicate()
  if o:
   printable=''.join(c if c.isdigit() or c.isalpha() else '.' for c in o)
   print '  3DES key=%s -> hex:%s ascii:%s' % (name,o.encode('hex'),printable)
" 2>&1"""].execute().text
println r
