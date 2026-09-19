import json
from pathlib import Path

DIR = Path(r"c:\xampp\htdocs\pentagi\independencia_attack")
p = DIR / "intelx_findep_results_final.json"
d = json.loads(p.read_text(encoding="utf-8"))

extra = [
    {"identity": "bmendezar", "password": "b3nj4m1n-2089!", "url": "notepad leftover", "source": "usuarios y contraseñas.txt", "note": "end of dump"},
]
d["orphan_passwords"] = [
    {"password": "Nosemeolvida032024*", "context": "near swagger chat Alejandro Aguilar Leon"},
    {"password": "N@slub8", "context": "near credprod / sybase / factura portal"},
]
seen = {(x["identity"].lower(), x["password"]) for x in d.get("unique_email_password") or []}
for e in extra:
    k = (e["identity"].lower(), e["password"])
    if k not in seen:
        d.setdefault("unique_email_password", []).append(e)
        seen.add(k)

d["azure_ad_secrets"] = [
    {
        "label": "VALOR SECRET BIGAZURE",
        "secret": "REDACTED",  # stored in api-keys.mdc
        "azure_id": "a7db7bbb-f6cf-46ac-ac96-24def7a67482",
        "application_client_id": "dcd316cd-3d3b-498a-b9cf-fc3aa69b4669",
        "source": "usuarios y contraseñas.txt",
        "note": "Looks like Azure AD app client secret (~ pattern). Highest-value cloud IAM leak. Not GKE kubeconfig.",
    }
]
d["internal_swagger"] = [
    "https://transformacion-polizas-service.backoffice.calidad-architect.com/v1/swagger-ui",
    "https://transformacion-polizas-tyson-service.tysonbeta.com/v1/swagger-ui",
    "https://dispersion-facade-service.tysonbeta.com/v1/swagger-ui/index.html",
    "http://localhost:8080/v1/swagger-ui.html",
]
d["employee_profile_bmendezar"] = {
    "name": "BENJAMIN MENDEZ ARMENTA",
    "email": "bmendezar@findep.com.mx",
    "rfc": "MEAB950906GU7",
    "num_empleado": "727282577",
    "puesto": "PROGRAMADOR",
    "departamento": "OPERACIONES",
    "empresa": "AEF, S.A. DE C.V.",
    "sucursal": "CORPORATIVO",
    "jefe": "Clara Maria Guerra",
}

# highlight emails
emails = (d.get("phonebook") or {}).get("pb_emails", {}).get("selectors") or []
interesting = []
for e in emails:
    el = e.lower()
    if any(k in el for k in ["fisa", "admin", "soto", "escamilla", "kube", "root", "devops", "cloud", "gcp", "azure", "vpn", "spei", "stp"]):
        interesting.append(e)
d["interesting_phonebook_emails"] = interesting

raw = json.dumps(d, indent=2, ensure_ascii=False, default=str)
(DIR / "intelx_findep_results_final.json").write_text(raw, encoding="utf-8")
try:
    (DIR / "intelx_findep_results.json").write_text(raw, encoding="utf-8")
except Exception as ex:
    print("primary save fail", ex)
print("pairs", len(d.get("unique_email_password") or []))
print("interesting emails", interesting[:40])
print("azure secret saved")
