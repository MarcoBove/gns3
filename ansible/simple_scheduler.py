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
# Percorso worker Linux
LINUX_WORKER_PATH = f"/home/{LINUX_USER}/dapt2021/worker"

# --- CONFIGURAZIONE WINDOWS ---
WINDOWS_USER = "User"  # Metti qui il nome utente vero di Windows
# Percorso worker Windows (Usa le barre normali / anche qui)
WINDOWS_WORKER_PATH = f"C:/Users/{WINDOWS_USER}/dapt2021/worker"

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Impossibile leggere {filepath}: {e}")
        return {}

def create_ansible_inventory(hosts_data):
    """
    Legge la lista dal JSON e crea l'inventario diviso.
    Si aspetta una lista di dizionari: [{'ip': '...', 'os': '...'}, ...]
    """
    linux_hosts = []
    windows_hosts = []

    # 1. Separiamo gli host in base al campo "os" nel JSON
    for host in hosts_data:
        ip = host.get('ip')
        os_type = host.get('os', 'linux').lower() # Default a linux se non specificato
        
        if os_type == 'windows':
            windows_hosts.append(ip)
        else:
            linux_hosts.append(ip)

    # 2. Scriviamo il file inventory
    with open(ANSIBLE_INVENTORY, 'w') as f:
        # Gruppo LINUX
        f.write("[workers_linux]\n")
        for ip in linux_hosts:
            f.write(f"{ip} ansible_user={LINUX_USER} ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")
        
        # Gruppo WINDOWS
        f.write("\n[workers_windows]\n")
        for ip in windows_hosts:
            f.write(f"{ip} ansible_user={WINDOWS_USER} ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")
            
    print(f"[INFO] Inventario creato: {len(linux_hosts)} Linux, {len(windows_hosts)} Windows.")
    
    # Ritorniamo True se ci sono host Windows, per sapere se lanciare i comandi Win dopo
    return len(windows_hosts) > 0

def run_ansible_command(url, has_windows):
    """Lancia i comandi appropriati."""
    
    print(f"[ACTION] Apertura URL: {url}")

    # --- COMANDO PER LINUX ---
    cmd_linux_text = (
        f"export DISPLAY=:0 && "
        f"export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus && "
        f"python3 {LINUX_WORKER_PATH}/browseInternet.py '{url}'"
    )
    
    # Nota: Usiamo 'workers_linux' come target
    cmd_linux = [
        "ansible", "workers_linux",
        "-i", ANSIBLE_INVENTORY,
        "-m", "shell",
        "-a", f"nohup sh -c '{cmd_linux_text}' > /dev/null 2>&1 &"
    ]

    # --- COMANDO PER WINDOWS ---
    cmd_windows_text = (
        f"echo {url} > {WINDOWS_WORKER_PATH}/current_url.txt && "
        f"schtasks /run /tn DaptBrowser"
    )
    
    # Nota: Usiamo 'workers_windows' come target
    cmd_windows = [
        "ansible", "workers_windows",
        "-i", ANSIBLE_INVENTORY,
        "-m", "shell",
        "-a", f"{cmd_windows_text}"
    ]

    # ESECUZIONE LINUX (Sempre, se il gruppo esiste Ansible gestisce se è vuoto o no, ma meglio gestire errori)
    try:
        # Lanciamo e ignoriamo l'output standard per pulizia
        subprocess.run(cmd_linux, capture_output=True, text=True)
    except Exception as e:
        print(f"[ERROR] Linux cmd: {e}")

    # ESECUZIONE WINDOWS (Solo se ci sono host windows)
    if has_windows:
        try:
            res = subprocess.run(cmd_windows, capture_output=True, text=True)
            if res.returncode != 0:
                print(f"[WARN] Windows cmd error: {res.stderr}")
        except Exception as e:
            print(f"[ERROR] Windows cmd: {e}")
        
    print("[OK] Comandi inviati.")

def main():
    print("--- AVVIO SCHEDULER IBRIDO (JSON DINAMICO) ---")
    
    # 1. Carica Configurazioni
    reg_config = load_json(REGISTRATION_FILE)
    web_config = load_json(WEBSITES_FILE)
    
    # Verifica che il JSON abbia la chiave giusta (HOSTS_LIST o quella che hai scelto)
    if 'HOSTS_LIST' in reg_config:
        hosts_data = reg_config['HOSTS_LIST']
    elif 'HOSTS_IP_ADDRESS' in reg_config:
        # Supporto retroattivo se non hai ancora cambiato il JSON (assume tutti Linux)
        print("[WARN] JSON vecchio formato rilevato. Assumo tutti Linux.")
        hosts_data = [{'ip': ip, 'os': 'linux'} for ip in reg_config['HOSTS_IP_ADDRESS']]
    else:
        print("[FATAL] Nessuna lista host trovata nel JSON.")
        return

    urls = [site['url'] for site in web_config.get('IT', [])]

    # 2. Crea Inventario Ansible e controlla se abbiamo Windows
    has_windows_hosts = create_ansible_inventory(hosts_data)
    
    # 3. Loop
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
