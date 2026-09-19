"""Kill all spray processes on all VPS."""
import paramiko, time

VPS_LIST = [
    {"ip": "64.177.83.195", "pass": "Nm9.#p)WzifT.fo2"},
    {"ip": "64.177.88.10", "pass": "5F.jyTK$D6%.F{a="},
    {"ip": "216.238.69.202", "pass": "hL@4xY@k)Nt6z_CE"},
    {"ip": "216.238.75.117", "pass": "]Aq9mngH(_%ZV%jn"},
    {"ip": "216.238.93.120", "pass": "6W@zCQaCG=UekagG"},
]

for vps in VPS_LIST:
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(vps['ip'], username='root', password=vps['pass'], timeout=10)
        _, s, _ = c.exec_command('pkill -f spray_v2 2>/dev/null; pkill -f spray_soporte 2>/dev/null; pkill -f mini_spray 2>/dev/null; pkill -f spray_v2 2>/dev/null; echo killed')
        print(f"[+] {vps['ip']}: {s.read().decode().strip()}")
        c.close()
    except Exception as e:
        print(f"[-] {vps['ip']}: {str(e)[:50]}")
    time.sleep(1)

print("\n[*] Todos los sprays detenidos. NO tocar soporte.disperso.com por 20+ minutos.")
print("[*] El rate limit se resetea con cada request — silencio total necesario.")
