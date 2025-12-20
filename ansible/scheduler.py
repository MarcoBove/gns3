import json
import time
import random
import subprocess
import os
from multiprocessing import Process

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

    try:
        with open(inventory, 'w') as f:
            # Gruppo LINUX
            f.write("[workers_linux]\n")
            for ip in linux_hosts:
                f.write(f"{ip} ansible_user={linux_user} ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")
            
            # Gruppo WINDOWS
            if windows_hosts:
                f.write("\n[workers_windows]\n")
                for ip in windows_hosts:
                    f.write(f"{ip} ansible_user={windows_user} ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")
    except Exception as e:
        print(f"[ERROR] Errore scrittura inventario {inventory}: {e}")
            
    print(f"[INFO] Inventario {inventory} creato: {len(linux_hosts)} Linux, {len(windows_hosts)} Windows.")
    return len(windows_hosts) > 0

def run_ansible_command(url, action_type, has_windows, inventory, linux_user, linux_path, windows_bat_path):
    """
    Lancia i comandi Ansible.
    Passa url e action_type sia a Linux che a Windows.
    """
    
    # --- COMANDO PER LINUX (smart_worker.py) ---
    cmd_linux_text = (
        f"export DISPLAY=:0 && "
        f"export TMPDIR=/home/{linux_user}/tmp_firefox && "
        f"{linux_path}/venv/bin/python {linux_path}/smart_worker.py {url} {action_type}"
    )
    
    cmd_linux = [
        "ansible", "workers_linux",
        "-i", inventory,
        "-m", "shell",
        "-a", f"nohup sh -c '{cmd_linux_text}' > /dev/null 2>&1 &"
    ]

    # --- COMANDO PER WINDOWS (Chiama il .bat che attiva il Task Scheduler) ---
    cmd_win = []
    if has_windows:
        # Passiamo URL e ACTION al .bat. Lui li scriverà nel file txt e chiamerà schtasks
        cmd_win = [
            "ansible", "workers_windows",
            "-i", inventory,
            "-m", "raw",
            "-a", f"{windows_bat_path} {url} {action_type}"
        ]

    # ESECUZIONE 
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
        
    print(f"[OK {inventory}] Comandi inviati -> {url} ({action_type})")

def simulation(vlan, registration, websites, inventory, linux_user, linux_path, windows_user, windows_bat_path):
    print(f"--- AVVIO PROCESSO SIMULAZIONE: {vlan} ---")
    
    reg_config = load_json(registration)
    web_config = load_json(websites)
    
    # Gestione Hosts
    if 'HOSTS_LIST' in reg_config:
        hosts_data = reg_config['HOSTS_LIST']
    elif 'HOSTS_IP_ADDRESS' in reg_config:
        hosts_data = [{'ip': ip, 'os': 'linux'} for ip in reg_config['HOSTS_IP_ADDRESS']]
    else:
        print(f"[FATAL {vlan}] Nessuna lista host trovata.")
        return

    # Gestione URLs (estrae la stringa intera "url azione")
    raw_entries = [site['url'] for site in web_config.get('IT', [])]
    if not raw_entries:
        print(f"[WARN {vlan}] Nessun URL trovato nel file websites.")
        return

    # Crea inventario specifico per questo processo
    has_windows_hosts = create_ansible_inventory(hosts_data, inventory, linux_user, windows_user)
    
    try:
        while True:
            # Prende una stringa a caso dal JSON es: "https://www.google.com generic"
            full_entry = random.choice(raw_entries)
            
            # SPLIT della stringa in URL e TYPE
            parts = full_entry.split()
            target_url = parts[0]
            action_type = parts[1] if len(parts) > 1 else "generic"

            run_ansible_command(target_url, action_type, has_windows_hosts, inventory, linux_user, linux_path, windows_bat_path)
            
            wait_time = random.randint(20, 40)
            print(f"[WAIT {vlan}] Attesa di {wait_time} secondi...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Simulazione interrotta.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore nel loop: {e}")

def main():
    print("--- AVVIO SCHEDULER MULTI-PROCESSO (SMART WORKER - VISIBLE MODE) ---")

    # --- CONFIGURAZIONE CLASSROOM 1 ---
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

    p1 = Process(target=simulation, args=args_c1)
    p2 = Process(target=simulation, args=args_c2)

    p1.start()
    print("[MASTER] Classroom1 avviata.")
    p2.start()
    print("[MASTER] Classroom2 avviata.")

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
