import json
import time
import random
import subprocess
import os

# --- CONFIGURAZIONE FILE ---
ANSIBLE_INVENTORY = "configs/hosts"
REGISTRATION_FILE = "configs/registration.json"
WEBSITES_FILE = "configs/websites.json"

# --- CONFIGURAZIONE LINUX ---
LINUX_USER = "osboxes"
LINUX_WORKER_PATH = f"/home/{LINUX_USER}/dapt2021/worker"

# --- CONFIGURAZIONE WINDOWS ---
WINDOWS_USER = "User"  # Metti qui il nome utente vero
# Percorso su Windows (Nota le doppie barre rovesciate \\ per sicurezza in Python)
WINDOWS_BAT_PATH = f"C:\\Users\\{WINDOWS_USER}\\dapt2021\\worker\\run_task.bat"

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Impossibile leggere {filepath}: {e}")
        return {}

def create_ansible_inventory(hosts_data):
    """
    Crea l'inventario.
    Per Windows usiamo una configurazione PULITA perché usiamo il modulo 'raw'.
    """
    linux_hosts = []
    windows_hosts = []

    for host in hosts_data:
        ip = host.get('ip')
        os_type = host.get('os', 'linux').lower()
        
        if os_type == 'windows':
            windows_hosts.append(ip)
        else:
            linux_hosts.append(ip)

    with open(ANSIBLE_INVENTORY, 'w') as f:
        # Gruppo LINUX
        f.write("[workers_linux]\n")
        for ip in linux_hosts:
            f.write(f"{ip} ansible_user={LINUX_USER} ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")
        
        # Gruppo WINDOWS (Semplificato)
        f.write("\n[workers_windows]\n")
        for ip in windows_hosts:
            # Togliamo ansible_shell_type, usiamo SSH standard
            f.write(f"{ip} ansible_user={WINDOWS_USER} ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")
            
    print(f"[INFO] Inventario creato: {len(linux_hosts)} Linux, {len(windows_hosts)} Windows.")
    return len(windows_hosts) > 0

def run_ansible_command(url, has_windows):
    """Lancia i comandi."""
    
    print(f"[ACTION] Apertura URL: {url}")

    # --- COMANDO PER LINUX (Modulo SHELL) ---
    cmd_linux_text = (
        f"export DISPLAY=:0 && "
        f"export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus && "
        f"python3 {LINUX_WORKER_PATH}/browseInternet.py '{url}'"
    )
    
    cmd_linux = [
        "ansible", "workers_linux",
        "-i", ANSIBLE_INVENTORY,
        "-m", "shell",
        "-a", f"nohup sh -c '{cmd_linux_text}' > /dev/null 2>&1 &"
    ]

    # --- COMANDO PER WINDOWS (Modulo RAW -> run_task.bat) ---
    if has_windows:
        # Chiamiamo direttamente il file BAT passando l'URL
        cmd_win = [
            "ansible", "workers_windows",
            "-i", ANSIBLE_INVENTORY,
            "-m", "raw",  # IMPORTANTE: Usa raw, non shell
            "-a", f"{WINDOWS_BAT_PATH} {url}"
        ]

    # ESECUZIONE LINUX
    try:
        subprocess.run(cmd_linux, capture_output=True, text=True)
    except Exception as e:
        print(f"[ERROR] Linux cmd: {e}")

    # ESECUZIONE WINDOWS
    if has_windows:
        try:
            res = subprocess.run(cmd_win, capture_output=True, text=True)
            # Con il modulo RAW, controlliamo se il codice di ritorno è 0
            if res.returncode != 0:
                print(f"[WARN] Windows Command FAILED!")
                print(f"--- OUTPUT: ---\n{res.stdout}\n{res.stderr}")
            else:
                # Se vuoi vedere "Command completed successfully" scommenta la riga sotto
                # print(f"[DEBUG Win] {res.stdout}")
                pass
        except Exception as e:
            print(f"[ERROR] Windows cmd: {e}")
        
    print("[OK] Comandi inviati.")

def main():
    print("--- AVVIO SCHEDULER IBRIDO (BAT VERSION) ---")
    
    reg_config = load_json(REGISTRATION_FILE)
    web_config = load_json(WEBSITES_FILE)
    
    if 'HOSTS_LIST' in reg_config:
        hosts_data = reg_config['HOSTS_LIST']
    elif 'HOSTS_IP_ADDRESS' in reg_config:
        print("[WARN] JSON vecchio formato. Assumo tutti Linux.")
        hosts_data = [{'ip': ip, 'os': 'linux'} for ip in reg_config['HOSTS_IP_ADDRESS']]
    else:
        print("[FATAL] Nessuna lista host trovata.")
        return

    urls = [site['url'] for site in web_config.get('IT', [])]

    # Crea inventario
    has_windows_hosts = create_ansible_inventory(hosts_data)
    
    try:
        while True:
            target_url = random.choice(urls)
            run_ansible_command(target_url, has_windows_hosts)
            
            wait_time = random.randint(10, 30)
            print(f"[WAIT] Attesa di {wait_time} secondi...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\n[STOP] Simulazione interrotta.")

if __name__ == "__main__":
    main()
