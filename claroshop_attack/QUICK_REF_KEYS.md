# ClaroShop / Sears / Sanborns — Quick Reference Credentials & Keys

> **Documento de Referencia Rápida — Grupo Sanborns / ClaroShop / Sears / T1Envios**  
> *Fecha de extracción:* 21-23 de Agosto de 2026  
> *Ubicación del engagement:* Jenkins Script Console RCE (`jenkins-ng.dev.claroshop.com`), AWS S3 (`860625208163`), DBs internas (`172.27.x.x`), Dumps de producción.

---

## 1. Top Credentials (Copy-Paste Ready)

### AWS Cloud & Storage
```text
# AWS S3 (Account 860625208163 - aws_sears_claro) - 29 Buckets accesibles
AWS_ACCESS_KEY_ID=AKIA4QYKCQNRTB3RPOG5
AWS_SECRET_ACCESS_KEY=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
AWS_DEFAULT_REGION=us-east-1

# S3 Backup Bucket Principal (162 GB Dumps SQL):
s3://sears-backups/
s3://prodigy-bk/
s3://respaldo-servers/
s3://axii-pedidos/
s3://medios.plazavip.com/

# AWS S3 Secondary Secret (smart_insight / cs_new_front)
AWS_SECRET_KEY_2=2GmpY95zmXttqCDKyIK/ltM75/OBr4DEsDbCJer1
```

### Databases (MySQL / MariaDB)
```text
# MySQL Producción ClaroShop (889K pedidos, 393K clientes, 388K tarjetas)
Host: 172.27.140.151 (masterdb57.claroshop.com / mysqlclaroshop.service:3306)
Database: tienda / admonplaza / payment_claropay
User: appmsclient / Pass: d9FNoft#NSaEZgvt
User: dbapipedidoscsb / Pass: YF8v{%dvupN3V1%T
User: dbclaroapilandinga / Pass: ApLik$r92_GF73.y
User: croncsasigdig / Pass: 5er6_dY65aSgf/s2
User: croncsasigpeds / Pass: BLu3%Man46eRks/s
User: dbcronconciliapayucs / Pass: ke$YLM98_reT4d28
User: croncamionestas / Pass: c6B=EB^Eh]afepZuP8
User: app_claropay / Pass: M@id83{sAx9=s>Vbw5

# MySQL Sanborns Producción
Host: dbas.claroshop-services.net:3306
User: adaxisdb
Pass PROD: DVcF8Q:tL3Yg8*jQ
Pass QA: qtn_RF42#pXzvV%
Pass Adicionales: Sci3nT}Z4bEL<3aU5 | Lo#$xcVB78d%3zxB | BeF=r3.6AxJSL+3q | Byd87$ml-TX5s9Da

# MySQL T1Envios (Dev / Prod)
Host DEV: dbst1envios.dev.t1envios-services.io:3322
User DEV: appgeotrack / Pass: A9P63oTr4Ck#T13nvi0s
Host PROD: dbst1envios.t1envios-services.io:3322
Pass PROD: F&tkC7aVg\H@iAj22SN

# MySQL T1 Pagos (172.27.141.4:3310)
Database: payment_t1
User: app_t1 / Pass: wUt22Us2CUh#+M=

# MySQL Cron Migración Tarjetas (masterdb57.qa.claroshop.com)
Database: tienda
User: cronmigraciontarjetas / Pass: S7^aq83=s{?sRM6tVv
```

### Redis / Cache
```text
# Redis Producción ClaroShop
Host: redis-storage-ng.claroshop-services.io:6379
Password: nBZxDxL2XxYwAEYyttme

# Redis Dev ClaroShop
Host: redis-storage-ng.dev.claroshop-services.io:6379
Password: @st0rAg3K3Y
```

### MongoDB
```text
# MongoDB Atlas (T1Envios K8s cluster)
URI: mongodb+srv://appmasivas_inb:nReyDxpQJXM0yvAYQTsa@t1envios.kqoop.mongodb.net/
User: appmasivas_inb
Pass: nReyDxpQJXM0yvAYQTsa

# MongoDB Interno (Carga Masiva)
Host: 172.26.84.132:27017
Pass: S157EM4TraC3s2
```

---

## 2. Encryption & Secret Keys (Crypto)

```text
# 1. Llave de Encriptación de Tarjetas de Crédito (TDC) - Producción
# Usada en: local.php (ClaroShop Producción), OneClickController, Cyber/Service.php
# Algoritmo: AES-256-CTR (Chris Veness implementation) / nBits=256
LLAVE_TDC_PROD=8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA

# 2. Llave de Encriptación de Tarjetas (TDC) - QA / Desarrollo
# Usada en: Elasticsearch betaqa, cron-migracion-tarjetas QA
LLAVE_TDC_DEV=K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4

# 3. Llave Conciliación de Tarjetas (Base64 -> 32 bytes RAW)
# Usada en: cron_conciliacion, Elasticsearch/betaqa/produccion.php
KEY_CONCILIA=VLDzybwRFujEMu4JaKBbz11FYPX9ixfzUX88bPCYXf0=
KEY_CONCILIA_HEX=54b0f3c9bc1116e8c432ee0968a05bcf5d4560f5fd8b17f3517f3c6cf0985dfd

# 4. Sears / Amex AES Key (Base64 -> 32 bytes RAW)
# Usada en: filesystems.php, Microservicios Sears
SEARS_AES_KEY=8fb2LIE2LYtjhZ8uDkY1EuO4mWfmOD6oZrWxPZfB76s=
SEARS_AES_KEY_HEX=f1f6f62c81362d8b63859f2e0e463512e3b89967e6383ea866b5b13d97c1efa4

# 5. 3D Secure KEY_SECRET (Firma y Verificación de Callbacks Bancarios)
# Usada en: TransaccionCyberController.php, Cybersource responses
KEY_3D_SECURE=cl40ro78sh3op9414042

# 6. Semilla Login Sears (CryptoAES)
SEMILLA_LOGIN=D3C0MP@52015

# 7. Internal Tokenization Keys (16 bytes RAW)
KEY_MKY=MKY21ASTR45YUPC1
KEY_UHUK=uhUKZEKBws4bxQ0G
KEY_PARTNER=xmx2L3570SwDefRZ4vFrnW55R0

# 8. Webhook / Callback Auth Key
AUTHKEY_WEBHOOK=/=T=gv6k84sc=xbn/hH=Gf2G==fK25j5//9

# 9. Laravel APP_KEY
APP_KEY_LARAVEL=base64:bwW89dBBBKoytnQhEyW/M9INdCwWXUXvYUql+YGf3as=

# 10. Cybersource Transaction Keys
CYBERSOURCE_POS_KEY=da4b9237bacccdf19c0760cab7aec4a8359010b0
CYBERSOURCE_RSA_KEY=yn/7kv47g0vaylkMXbWsB86S4E9r9Ve0j3pI8h4DEkS1hWQ3TG6N4WuqsLbovLCQ3adqAHkNrG5UNvynQS2MYCaskdQ1PhtfBuDJmiP5wSP3FC+4kaYQi85S2RC3dePRlzNoRiYCsDE49cdHPFcmwd4dQSeK6v5vY8yjvXKGPo3ygWSnva0Z7XoeAmM7CHo+RSytxtXpASlfswugyelt15nxmB8qvAeJVL5+zcBlYR/y1ZoOCsOob09HJQ8IoaJMQjOL3wFA8u3OCCG8i3uf+vVo4ckaqqNxUUNk++U5C3EpWa9p8irEn6FZm6fiGLsNthBNpi3w9h4514yf/dfd6g==

# 11. MercadoPago Public Key
MERCADOPAGO_PUBLIC_KEY=APP_USR-38cad5a8-7c4e-45e1-8be2-a890c5ebc429

# 12. Gigya / SAP Customer Data Cloud Secrets
GIGYA_KEY=3_i1QeZqrz6xSX5fF_TanfzOBYK_tqHpRtD6ylvBZI5kpyIh7wQBpeYSAMVIPJ7T27
GIGYA_SECRET_1=sXWa6ly4DNY79T0df7Pl
GIGYA_SECRET_2=Wl/jeXkpGG/AelI/q1a1gNRN1JHRq6cs8+oYfqekmHU=

# 13. Google reCAPTCHA v2 (Site Key & Secret Key)
RECAPTCHA_SITE_KEY=6LdkagsTAAAAAPmLFF4JdL9oPpIek3xNOhVdCnr4
RECAPTCHA_SECRET_KEY=6LdkagsTAAAAAH4e4EZ6-wBmK5POsaw2-sNFtOx0
```

---

## 3. Web & Admin Access (Confirmed Portals)

```text
# Graylog T1Envios (Logs de Producción) - HIT 200 OK
URL: https://graylog-admin.t1envios.com
User: eduardo.cruz
Pass: ZGpxZJnpit

# Jenkins-NG DEV (CI/CD Pipeline con Script Console RCE) - HIT 200 OK
URL: https://jenkins-ng.dev.claroshop.com (o 200.57.183.182)
User: eduardo.cruz
Pass: xwMyIxfkZZaDNkFg
Alt User: maria.policarpo / Pass: try60JzExAifXzs5
Alt User: jenkins_legacy / Pass: JenkisLegasy25

# T1Envios Admin PROD - HIT 302 OK
URL: https://admin.t1envios.com
User: eduardo.cruz@claroshop.com
Pass: y1P22*_2022

# POT Admin ClaroShop PROD (Catálogo & Productos) - HIT 302 OK
URL: https://pot.admin.claroshop.com
User: validacionproductiva@claroshop.com
Pass: Enero2023**

# Axii Admin SEARS Backoffice - HIT 302 OK
URL: https://axii.sears.com.mx (o dev)
User: eduardo.cruz@decompras.com
Pass: Q1234567890qwertyu

# Axii Admin SANBORNS Backoffice - HIT 302 OK
URL: https://axii.sanborns.com.mx (o dev)
User: eduardo.cruz@decompras.com
Pass: Q1234567890qwertu

# Selfservice ClaroShop Admin PROD
URL: https://selfservice.claroshop.com
User: admin@claroshop.com / Pass: Clar0Sh0p1
User: eduardo.cruz@claroshop.com / Pass: bRVJ2tCHw4
Release User: claroshop.prod / Pass: 7b0PrigflRil5iws

# Instana APM / Monitoring PROD
URL: https://plataforma-claro.instana.io
User: eduardo.cruz@claroshop.com
Pass: B4v*W*Pvm2rW5mp

# Graylog Plataforma Claro PROD
URL: https://graylog-admin.plataforma-claro.com
User: eduardo.cruz
Pass: Junio2022

# Graylog Dev
URL: https://graylog.dev.claroshop.com
User: eduardo.cruz
Pass: HJPt1UdEjib90VFa

# Facturación Electrónica (Solución Factible)
URL: https://solucionfactible.com
User: CRUZEDUE@GLOBALHITSS.COM
Pass: L67ujhpa

# Keycloak SSO Plataforma Claro / Asgard / Aegis
URL: https://loginclaro.com/auth/ (realms: plataforma-claro, asgard)
User: eduardo.cruz@claroshop.com / Pass: S4suk38509
User Asgard: eduardo.cruz / Pass: kcwaVb$xDAn

# GitLab Interno (Dev)
URL: http://172.27.140.129 / http://CSDEV01-2.dev.claroshop.com
User: maria.policarpo / Pass: FtMRl4fDXzIDY4Yj
User: jenkins / Pass: e6LBqIkOI$PR1XX2oia
User: jenkins_legacy / Pass: JenkisLegasy25
```

---

## 4. Payment Gateways & Logistics APIs

```text
# PayPal PROD Secret
Client ID / Key: ELkohHOoMS2ttcBZC4BLvHMXCQWaLEqFMEXqc1V3bhr32WMd74234TBMV5e0En69bKArLQBqY8N89m1D
API Secret: EJskuxQaCbhvzGCfZCbF91FfIYlOkwSUkRkxezUiWxKZnFVPleBV6IEVRo4liqay

# PayPal Sandbox
Client ID: ARKcq6f_UqJJjDd2...
Client Secret: EIWCCmDTP2e7Fe8jaKWsRZ_h3...

# PayU API (Comprobantes / Pagos)
API Key: xmx2L3570SwDefRZ4vFrnW55R0
API Key Colombia: 4Vj8eK4rloUd272L48hsrarnUA
PROD Key: 6J6ogJP07Xy30Noz2jw5Ax4jZJ

# FedEx API (wsbeta / prod)
Key: LgiWacWCmeeZlgQq
Password: v1KJYPOKhqVcsSOXVJsSbNrDe
Account: 510087763
Secret ID: f04ae9335a49454e88996f1b57bccc54

# DHL Express (Sanborns / ClaroShop)
Host: xmlpitest-ea.dhl.com
SiteID: xmlSANBORNH
Password: ke3tUXq8RJ
Account: 988007116
PROD Key: 4eJ7G0paawA8R53AQJu15yxd / OXmt73yIhr

# Estafeta API
Host: labelqa.estafeta.com
User: prueba1 / Pass: lAbeL_K_11

# Redpack API
Key: Rsi)M|Y5WdPs{>+/a2cC

# iMile Express
Host: openapi.52imile.cn
Account: C21018328 / Pass: BE8YaUErgogL

# 99Minutos Sandbox
User: desarrollo@t1envios.com / Pass: Dp1yGrDl1r6zay

# BigSmart API
User: daniel.garcia@claroshop.com / Pass: garcia@2020

# Cargamos API
User: roberto.martinez@claroshop.com / Pass: Claroshop_1234
```

---

## 5. Email & SMTP Accounts

```text
guiassearscom@claroshop.com / 87AC_Vqm
guiasc@claroshop.com / 3q.X}G8G&%
guiass@claroshop.com / oL$q7+kR2l
respaldo_api_sears@claroshop.com / rUTouV6ca
respaldo_notificacion_api@claroshop.com / DiSSjK628t9
ticket.claroshop@claroshop.com / G=h9$$R7p7
incidenciasmensajerias@claroshop.com / :M1zsPlC^J
cancelacionesclaroshop@claroshop.com / V99icY_U7
cancelacionessanborns@claroshop.com / B1p!KUgojR
pedidosmkclaro@claroshop.com / <1FmF]OwC[
maria.policarpo@claroshop.com / eHlkP6r5
eduardo.cruz@claroshop.com / S@suk3240285
guiasclaroshop@gmail.com / 6u1@5C14r05Hh0P
reportesconpaqueteria@gmail.com / reportesconpaqueteria9876
cancelacionessanborns (Gmail) / C4nc314c1ON35
policarpomg (Correoweb Hitss) / 6969#Kl12
```

---

## 6. SSH Keys & Docker Hosts

```text
# Jenkins Node SSH Key (CSDEV01-2 / Internal Deploy Key)
Host: 200.57.183.182 (CSDEV01-2.dev.claroshop.com)
User: jenkins (uid=556)
Private Key File: jenkins_source/jenkins_ssh_key.pem

# Internal Docker Daemon (Unauthenticated REST API)
Host: http://CSDEVBLD01-1:4243 / http://172.27.140.129:2375
Registry: docker-registry.nexus.dev.claroshop.com
Image Utilizada para RCE/Queries: docker-registry.nexus.dev.claroshop.com/docker-jnlp-slave-php71-src-sonar
```
