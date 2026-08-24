#!/usr/bin/env python
# Builder generico: empaqueta un archivo (py/php/sh) en un groovy que lo ejecuta en el container via Docker API
# Uso: python build_groovy_exec.py <archivo> <salida.groovy> [interprete]
import sys, base64

src_file = sys.argv[1]
out_file = sys.argv[2]
interp = sys.argv[3] if len(sys.argv) > 3 else 'python'

ext = src_file.rsplit('.', 1)[-1]
remote = '/tmp/job_%s.%s' % (base64.b16encode(src_file.encode()).decode()[:8], ext)

code = open(src_file, 'rb').read()
b64 = base64.b64encode(code).decode('ascii')

template = '''import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def dHost = "172.27.140.148"
def dPort = 4243
def cid = "5b32e909c295"

def codeB64 = "B64PLACEHOLDER"
def shCmd = 'echo ' + codeB64 + ' | base64 -d > REMOTEPLACEHOLDER && INTERPPLACEHOLDER REMOTEPLACEHOLDER'
def url = new URL("http://${dHost}:${dPort}/containers/${cid}/exec")
def conn = url.openConnection()
conn.setRequestMethod("POST"); conn.setDoOutput(true)
conn.setRequestProperty("Content-Type", "application/json")
def body = JsonOutput.toJson([AttachStdout:true, AttachStderr:true, Cmd:["bash","-c",shCmd]])
conn.outputStream.write(body.bytes); conn.outputStream.flush()
def r = new JsonSlurper().parseText(conn.inputStream.text)
def eid = r.Id
def su = new URL("http://${dHost}:${dPort}/exec/${eid}/start").openConnection()
su.setRequestMethod("POST"); su.setDoOutput(true)
su.setRequestProperty("Content-Type", "application/json")
su.outputStream.write('{"Detach":false,"Tty":true}'.bytes); su.outputStream.flush()
su.setConnectTimeout(10000)
su.setReadTimeout(240000)
println su.inputStream.text
'''

out = template.replace('B64PLACEHOLDER', b64).replace('REMOTEPLACEHOLDER', remote).replace('INTERPPLACEHOLDER', interp)
open(out_file, 'w', encoding='utf-8').write(out)
print('written', out_file, len(out))
