# MX Global Exchange — Reporte de Reconocimiento
**Fecha:** 2026-09-24
**Target:** MX Global (mx.exchange / mxglobal.com.my)
**Equipo:** Tr4nsHack

---

## RESUMEN EJECUTIVO

- Exchange crypto malasio (Securities Commission Malaysia) — pares BTC/ETH/XRP/SOL/WLD contra MYR
- **32 subdominios** descubiertos en mx.exchange + 3 en mxglobal.com.my
- **UAT host leakeado** en la documentación de la API (openapiuat.azurewebsites.net) — Azure directo sin WAF
- **RabbitMQ DEV expuesto** (13.76.221.253) — Management UI :15672, AMQP :5672, SSH :22 — 7 CVEs
- **RabbitMQ PROD expuesto** (52.187.114.84) — AMQP :5672 — 2 CVEs
- **OpenAPI spec pública** con esquema HMAC-SHA256 y código de ejemplo completo
- **BitGo Express** expuesto (infraestructura de wallets crypto)
- **Grafana** accesible (403 Cloudflare pero subdomain vivo)

---

## INFRAESTRUCTURA

| Host | IP | CDN/WAF | Notas |
|---|---|---|---|
| openapi.mx.exchange | 104.20.31.91 / 172.66.160.211 | Cloudflare | API producción |
| mx.exchange | 104.20.31.91 / 172.66.160.211 | Cloudflare | Apex |
| mxglobal.com.my | 104.26.12.96 / 172.67.71.154 | Cloudflare | Marketing |
| openapiuat.azurewebsites.net | **13.67.9.5** | **SIN WAF** | UAT API (Azure SE Asia) |
| openapi-uat.mx.exchange | **13.67.9.5** | **SIN WAF** | UAT alias |
| web-uat.mx.exchange | **13.67.9.5** | **SIN WAF** | UAT web |
| webdev2.mx.exchange | **13.67.9.5** | **SIN WAF** | Dev2 web |
| rabbitmqdev.mx.exchange | **13.76.221.253** | **SIN WAF** | RabbitMQ DEV |
| rmq.mx.exchange | **52.187.114.84** | **SIN WAF** | RabbitMQ PROD |
| git.mx.exchange | 58.26.224.86 | Ninguno (timeout) | Git server (internal?) |
| bitgoexpress.mx.exchange | **52.163.113.76** | **SIN WAF** | BitGo wallet infra |
| web-stg.mx.exchange | 20.43.132.133 | Azure shared | Staging web |
| dev.mx.exchange | CloudFront | AWS | Dev (500 error) |
| coldplay.mx.exchange | 76.76.21.164 | Vercel | Marketing campaign |
| admin.mx.exchange | CF | Cloudflare (403) | Admin panel |
| grafana.mx.exchange | CF | Cloudflare (403) | Monitoring |
| app.mx.exchange | CF | Cloudflare | Exchange frontend |
| support.mx.exchange | CF | Cloudflare | Helpdesk (login) |

---

## HALLAZGOS / VULNERABILIDADES

### VULN-1: UAT API Expuesta sin WAF (ALTA)
- openapiuat.azurewebsites.net (13.67.9.5) — VIVO, Azure App Service directo
- Misma API spec que producción, datos de test
- Orderbook separado (precios ~222K MYR vs ~363K prod)
- Leakeado en los code examples del Swagger (host hardcodeado)
- Endpoint público accesible sin restricción de IP

### VULN-2: RabbitMQ DEV Expuesto con CVEs (CRÍTICA)
- rabbitmqdev.mx.exchange → 13.76.221.253
- Puertos: 22 (SSH 7.4p1), 5672 (AMQP), **15672 (Management UI)**
- RabbitMQ 3.8.2 (EOL)
- CVEs: CVE-2022-31008, CVE-2023-46118, CVE-2021-22116, CVE-2021-32719, CVE-2021-32718, CVE-2020-11022, CVE-2020-11023
- Probar guest:guest en management UI (PENDIENTE — requiere VPS con SSH)

### VULN-3: RabbitMQ PROD AMQP Expuesto (ALTA)
- rmq.mx.exchange → 52.187.114.84
- Puerto: 5672 (AMQP)
- RabbitMQ 3.8.18 (EOL)
- CVEs: CVE-2022-31008, CVE-2023-46118

### VULN-4: OpenAPI Spec Pública con Auth Scheme (MEDIA)
- /swagger/v1/swagger.json accesible sin auth (prod + UAT)
- Swagger UI interactivo habilitado
- Documenta esquema HMAC-SHA256 completo con código de ejemplo
- Revela hostnames internos (openapiuat.azurewebsites.net)

### VULN-5: BitGo Express Expuesto (ALTA)
- bitgoexpress.mx.exchange → 52.163.113.76 (Azure)
- BitGo Express = servicio de firma de transacciones crypto
- Timeout pero subdomain resuelve — posiblemente filtrado por IP

### VULN-6: Múltiples Entornos Dev/Test/Staging Accesibles (MEDIA)
- web-stg.mx.exchange (20.43.132.133) — Staging
- web-uat.mx.exchange (13.67.9.5) — UAT
- webdev2.mx.exchange (13.67.9.5) — Dev2
- dev.mx.exchange (CloudFront) — Dev (500)
- 6 hosts *hkdev.mx.exchange — Hong Kong Dev

### VULN-7: Git Server Expuesto (MEDIA)
- git.mx.exchange → 58.26.224.86
- IP no-cloud (ISP Malaysia?)
- Timeout desde WebFetch — posiblemente requiere VPN/whitelist

### VULN-8: Helpdesk Login Sin Captcha (BAJA)
- support.mx.exchange — ticketing system
- Login username/password sin captcha visible

---

## API ENDPOINTS CONFIRMADOS

### Públicos (sin auth)
| Método | Path | Datos |
|---|---|---|
| GET | /api/1/marketpair | 5 pares: BTCMYR, ETHMYR, XRPMYR, SOLMYR, WLDMYR |
| GET | /api/1/orderbooks?pair= | Full orderbook (asks/bids con precios y volúmenes) |
| GET | /api/1/recenttrades?pair= | Historial de trades recientes |

### Requieren Auth (HMAC-SHA256)
| Método | Path | Función |
|---|---|---|
| GET | /api/Preflight | WLD offramp limits (401 sin auth) |
| GET | /api/Quote?cryptoAmount= | WLD offramp quote (401 sin auth) |
| POST | /api/1/user/order/fak_order | Fill-and-Kill market order |
| POST | /api/1/user/order/limit_order | Limit order |
| POST | /api/1/user/order/cancel | Cancel order |
| POST | /api/1/user/order/cancel_multiple | Cancel multiple orders |
| GET | /api/1/user/balance | Wallet balance |
| GET | /api/1/user/order/openorders?pair= | Open orders |
| GET | /api/1/user/order/{id} | Order details |
| GET | /api/1/user/trades?pair= | User trades |
| GET | /api/1/user/orderexecutions?orderbookId= | Order executions |

---

## AUTH SCHEME

- HMAC-SHA256 HTTP Signatures
- Headers: Date (RFC1123 UTC, max 5min skew) + Authorization
- GET signature: (request-target) + host + date
- POST signature: (request-target) + host + date + content-type + content-length + body
- keyId = API key, secret = API secret
- Rate limit: 120 requests/min

---

## PENDIENTES (P0)

- [ ] Probar RabbitMQ Management UI guest:guest desde VPS (13.76.221.253:15672)
- [ ] Probar creds default RabbitMQ AMQP (52.187.114.84:5672)
- [ ] Buscar API keys en stealer logs (IntelX: mx.exchange, mxglobal.com.my)
- [ ] Probar BitGo Express endpoints (52.163.113.76)
- [ ] Probar SSH default creds en 13.76.221.253:22
- [ ] Registrar cuenta en app.mx.exchange → obtener API key → probar UAT
- [ ] Grafana default creds (admin:admin) — necesita bypass Cloudflare
- [ ] Helpdesk spray/brute (support.mx.exchange)
- [ ] OSINT empleados MX Global en LinkedIn
- [ ] Nuclei scan UAT (13.67.9.5) sin WAF
