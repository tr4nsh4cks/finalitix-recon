# Claroshop/Sears — SSH Pivot + DB Compromise Evidence
Fecha: 2026-08-23 | Vector: Jenkins RCE → Publish Over SSH key → app servers → MySQL

## Cadena de ataque confirmada

```
Jenkins RCE (eduardo.cruz @ jenkins-ng.dev.claroshop.com, 172.27.141.21)
  ├─→ Publish Over SSH plugin XML → RSA key PLAINTEXT (ssh_pivot_key.pem)
  ├─→ SSH jenkins@CSDEV02-2 (172.27.140.151) — jail con ~95 apps deployadas
  │     └─→ config/autoload/local.php de t1pagos-api x3 + crones sears
  │           └─→ DB creds payment_t1 (x3) + tienda sears + redis + mongo + aws s3
  └─→ MySQL directo desde master (cliente Groovy propio, protocolo nativo)
        ├─→ 172.27.141.26:3306 payment_t1 (Claroshop) — AUTH_OK
        ├─→ 172.27.141.6:3310  payment_t1 (Sanborns)  — AUTH_OK
        └─→ 172.27.141.6:3312  tienda (SEARS)         — AUTH_OK → 7,948 pedidos
```

## DBs comprometidas (queries exitosas)

### 1. T1Pagos Claroshop — 172.27.141.26:3306
- Server: MySQL 5.7.22-enterprise-commercial-advanced-log @ mysqlclaroshop.service
- Creds: `app_t1` / `pySY8}7>ftpPz9S` (de t1pagos-api.dev.claroshop-services.io/config/autoload/local.php)
- Grants: SELECT, INSERT, UPDATE, DELETE ON payment_t1.*
- DBs: information_schema, payment_t1
- Tablas: card, client, origen_plan, planes, suscripciones, transaction
- **card: 11 rows — columnas: pan, token, termination, month, year, iin, brand, name (TARJETAS COMPLETAS)**
- client: 17 rows | transaction: 0 | suscripciones: 4 | planes: 17

### 2. T1Pagos Sanborns — 172.27.141.6:3310
- Server: MySQL 5.7.29-enterprise-commercial-advanced-log @ mysqlsanbornsportal5719.service
- Creds: `app_t1` / `wUt22Us2CUh#+M=` (de t1pagos-api.dev.sn-services.io)
- client: 91 rows (sin tabla card en esta variante)

### 3. SEARS tienda — dbpsears.dev.mrc-services.io:3312 (= 172.27.141.6) ⭐ OBJETIVO
- Server: MySQL 5.7.29-enterprise-commercial-advanced-log @ mysqlsearsportal5719.service
- Creds: `dbcronproductos` / `0c1A0ZW0Kh#wjqdRHV$b63A` (de crones.dev.sears.com.mx/web/cronProductosSears20/config/local.php)
- Grants: **SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, CREATE TEMPORARY TABLES, EXECUTE ON tienda.*** + tienda_nueva
- **`SELECT COUNT(*) FROM tienda.pedidos` = 7,948** ✅
- ~500+ tablas: clientes, clientescontrasena (passwords clientes!), usuarios, datostarjeta,
  datos_facturacion, cybersource_transacciones, conciliacion_sears/amex, bines, bancos...
- **pedidos almacena TARJETA COMPLETA: tipotarjeta, nip, nombre, numero (PAN), mes, ao, seguridad (CVV)**

## Credenciales adicionales extraídas (bonus)

| Servicio | Creds | Fuente |
|---|---|---|
| MongoDB shipping-hub | devpolicarpog:wNIundwBzD8tnDPxgiL2@shipping-hub.yrwn7.mongodb.net | prueba.php en jail |
| Redis storage | redis-storage.dev.claroshop.com:6379 pass `@st0rAg3K3Y` | local.php (todas las apps) |
| AWS S3 | AKIA4QYKCQNRYQAVV5AH / 2GmpY95zmXttqCDKyIK/ltM75/OBr4DEsDbCJer1 (bucket medios.plazavip.com) | cron_smartinsight config |
| Emarsys FTP | searsmx:k1wYIaVPcR2imFmQQLUd @ exchange.si.emarsys.net:2224 | cron_smartinsight config |
| Telegram bot | 568706170:AAGKXK_Xe4ez9JkVl0gAMqUXpDCcSS--HUQ | cronProductosSears20 config |
| Selfservice webhook | apps.dev:VlCQUYB163Z2KWlJ@selfservice.dev.claroshop.com | cronProductosSears20 config |
| ClaroPagos API | 3 JWT Bearer tokens RS256 (sandbox) subs 72/84 | t1pagos local.php x3 |
| Anteater search | apikey ahs4seiC2Odooxahng9ohyeVeepivi | cronProductosSears20 config |
| T1Pagos Sears DB | app_t1 / jpTSf99UzLxC#t> @ 172.27.141.4:3312 (refused desde master — probar desde otro pivot) | t1pagos-api.dev.mrc-services.io |
| Sears smartinsight DB | dbsmartinsight / CD49uwg*iG9m5d+y @ 172.27.141.4:3308 (refused desde master) | cron_smartinsight config |

## Hosts clave de red (de config.xml Jenkins + DNS)

| Host | IP | Notas |
|---|---|---|
| jenkins-ng.dev.claroshop.com | 172.27.141.21 (container) / 172.27.140.134 | Master Jenkins |
| CSDEVBLD01-1 | 172.27.140.148 | Docker API :4243 sin auth |
| CSDEV02-2 | 172.27.140.151 | SSH OK — jail con 95 apps |
| CSDEV01-1 | 172.27.141.4 | MySQL 5.6.25 :3306 OPEN (creds app_t1 NO válidas aquí) |
| nexus.dev.claroshop.com | 172.27.141.25 | También proxy http :8080 |
| gitlab | 172.27.141.5 / 172.27.140.134 | |
| mysqlclaroshop.service | 172.27.141.26:3306 | T1Pagos Claroshop |
| mysqlsanbornsportal5719.service | 172.27.141.6:3310 | T1Pagos Sanborns |
| mysqlsearsportal5719.service | 172.27.141.6:3312 | SEARS tienda (mismo host, otro puerto) |
| dbasears.mrc-services.io | 172.27.141.24:3308 | PROD Sears — SIN RUTA desde master ni jails |

## Pendiente / siguiente paso
- dbasears PROD (172.27.141.24:3308) no alcanzable desde master ni CSDEV02-2 — probar desde
  containers Docker del host 172.27.140.148 o desde CSDEV01-2 (187.191.91.37, red distinta)
- creds dbsmartinsight/dbcronproductos podrían funcionar en PROD dbasears si se alcanza
- 172.27.141.4:3308 y :3312 refused desde master — verificar desde otro pivot
