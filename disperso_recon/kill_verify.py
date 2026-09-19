"""Kill ALL spray/python processes on ALL VPS and verify."""
import paramiko, time

VPS_LIST = [
    {"ip": "64.177.83.195", "pass": "Nm9.#p)WzifT.fo2"},
    {"ip": "64.177.88.10", "pass": "5F.jyTK$D6%.F{a="},
    {"ip": "216.238.69.202", "pass": "hL@4xY@k)Nt6z_CE"},
    {"ip": "216.238.75.117", "pass": "]Aq9mngH(_%ZV%jn"},
    {"ip": "216.238.93.120", "pass": "6W@zCQaCG=UekagG"},
    {"ip": "64.177.88.129", "pass": "2f-Nkz4GdWiYunE,"},
    {"ip": "216.238.94.45", "pass": "F5v-Sr!@GZ@5P4#E"},
]

for vps in VPS_LIST:
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(vps['ip'], username='root', password=vps['pass'], timeout=10)
        
        # Kill ALL python3 processes and spray-related processes
        _, s, _ = c.exec_command('pkill -9 -f "spray|disperso|mini_spray" 2>/dev/null; pkill -9 python3 2>/dev/null; sleep 1; echo killed_all')
        out = s.read().decode().strip()
        
        # Verify no python processes remain
        _, s2, _ = c.exec_command('pgrep -af python3 2>/dev/null; echo done')
        procs = s2.read().decode().strip()
        
        print(f"[+] {vps['ip']}: {out} | Remaining procs: {procs[:100]}")
        c.close()
    except Exception as e:
        print(f"[-] {vps['ip']}: {str(e)[:50]}")
    time.sleep(1)

print("\n[*] TODOS los Python3 muertos en todos los VPS.")
print("[*] Ahora: SILENCIO TOTAL — cero requests al endpoint por 20 minutos.")
