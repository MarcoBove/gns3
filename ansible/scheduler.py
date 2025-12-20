import json
import time
import random
import subprocess
import os
from multiprocessing import Process # <--- IMPORTANTE: Importiamo Process

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Impossibile leggere {filepath}: {e}")
        return {}

def create_ansible_inventory(hosts_data, inventory, linux_user, windows_user):
    linux_hosts = []
    windows_hosts = []

    for host in hosts_data:
        ip = host.get('ip')
        os_type = host.get('os', 'linux').lower()
        
        if os_type == 'windows':
            windows_hosts.append(ip)
        else:
            linux_hosts.append(ip)

    # Assicuriamoci che la directory per l'inventario esista o gestiamo il path
    try:
        with open(inventory, 'w') as f:
            # Gruppo LINUX
            f.write("[workers_linux]\n")
            for ip in linux_hosts:
                f.write(f"{ip} ansible_user={linux_user} ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")
            
            # Gruppo WINDOWS
            if windows_hosts: # Scriviamo il gruppo windows solo se ce ne sono
                f.write("\n[workers_windows]\n")
                for ip in windows_hosts:
                    f.write(f"{ip} ansible_user={windows_user} ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")
    except Exception as e:
        print(f"[ERROR] Errore scrittura inventario {inventory}: {e}")
            
    print(f"[INFO] Inventario {inventory} creato: {len(linux_hosts)} Linux, {len(windows_hosts)} Windows.")
    return len(windows_hosts) > 0

def run_ansible_command(url, has_windows, inventory, linux_path, windows_bat_path):
    # --- COMANDO PER LINUX ---
    cmd_linux_text = (
        f"export DISPLAY=:0 && "
        f"export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus && "
        f"python3 {linux_path}/browseInternet.py '{url}'"
    )
    
    cmd_linux = [
        "ansible", "workers_linux",
        "-i", inventory,
        "-m", "shell",
        "-a", f"nohup sh -c '{cmd_linux_text}' > /dev/null 2>&1 &"
    ]

    # --- COMANDO PER WINDOWS ---
    cmd_win = []
    if has_windows:
        cmd_win = [
            "ansible", "workers_windows",
            "-i", inventory,
            "-m", "raw",
            "-a", f"{windows_bat_path} {url}"
        ]

    # ESECUZIONE (In sequenza rapida per questo processo)
    # Nota: Questo blocca il singolo processo per un attimo, ma dato che usiamo 
    # Multiprocessing nel main, l'altra Classroom non sta aspettando questa.
    try:
        # Lancia Linux
        subprocess.run(cmd_linux, capture_output=True, text=True)
    except Exception as e:
        print(f"[ERROR {inventory}] Linux cmd: {e}")

    if has_windows:
        try:
            # Lancia Windows
            subprocess.run(cmd_win, capture_output=True, text=True)
        except Exception as e:
            print(f"[ERROR {inventory}] Windows cmd: {e}")
        
    print(f"[OK {inventory}] Comandi inviati per URL: {url}")

def simulation(vlan, registration, websites, inventory, linux_user, linux_path, windows_user, windows_bat_path):
    print(f"--- AVVIO PROCESSO SIMULAZIONE: {vlan} ---")
    
    reg_config = load_json(registration)
    web_config = load_json(websites)
    
    if 'HOSTS_LIST' in reg_config:
        hosts_data = reg_config['HOSTS_LIST']
    elif 'HOSTS_IP_ADDRESS' in reg_config:
        hosts_data = [{'ip': ip, 'os': 'linux'} for ip in reg_config['HOSTS_IP_ADDRESS']]
    else:
        print(f"[FATAL {vlan}] Nessuna lista host trovata.")
        return

    # Seleziona URL (supporto fallback se manca chiave IT)
    urls = [site['url'] for site in web_config.get('IT', [])]
    if not urls:
        print(f"[WARN {vlan}] Nessun URL trovato nel file websites.")
        return

    # Crea inventario specifico per questo processo
    has_windows_hosts = create_ansible_inventory(hosts_data, inventory, linux_user, windows_user)
    
    try:
        while True:
            target_url = random.choice(urls)
            run_ansible_command(target_url, has_windows_hosts, inventory, linux_path, windows_bat_path)
            
            # Delay casuale indipendente per ogni classroom
            wait_time = random.randint(20, 40)
            print(f"[WAIT {vlan}] Attesa di {wait_time} secondi...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Simulazione interrotta.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore nel loop: {e}")

def main():
    print("--- AVVIO SCHEDULER MULTI-PROCESSO ---")

    # --- CONFIGURAZIONE CLASSROOM 1 ---
    # Definiamo gli argomenti in una tupla
    args_c1 = (
        "Classroom1", 
        "configs/registration_10.json", 
        "configs/websites_10.json", 
        "configs/hosts_10", 
        "student", 
        "/home/student/user_behavior_generation/worker", 
        "Student", 
        "C:\\Users\\Student\\user_behavior_generation\\worker\\browser_task.bat"
    )

    # --- CONFIGURAZIONE CLASSROOM 2 ---
    # Nota: windows_user e bat_path vuoti vanno bene perché l'inventario non avrà host windows
    args_c2 = (
        "Classroom2", 
        "configs/registration_20.json", 
        "configs/websites_20.json", 
        "configs/hosts_20", 
        "student", 
        "/home/student/user_behavior_generation/worker", 
        "", 
        ""
    )

    # Creazione dei processi paralleli
    p1 = Process(target=simulation, args=args_c1)
    p2 = Process(target=simulation, args=args_c2)

    # Avvio dei processi
    p1.start()
    print("[MASTER] Classroom1 avviata.")
    p2.start()
    print("[MASTER] Classroom2 avviata.")

    # Il main attende che i processi finiscano (in teoria mai, finché non premi CTRL+C)
    try:
        p1.join()
        p2.join()
    except KeyboardInterrupt:
        print("\n[MASTER] Ricevuto Stop. Termino i processi...")
        p1.terminate()
        p2.terminate()
        p1.join()
        p2.join()
        print("[MASTER] Tutti i processi terminati.")

if __name__ == "__main__":
    main()
