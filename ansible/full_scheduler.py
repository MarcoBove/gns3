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
            
            wait_time = random.randint(60, 100)
            print(f"[WAIT {vlan}] Attesa di {wait_time} secondi...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Simulazione interrotta.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore nel loop: {e}")
        

def run_pdf_command(pdf_path, action_type, has_windows, inventory, linux_user, linux_path, windows_bat_path):
    """
    Lancia il comando per leggere PDF.
    action_type sarà sempre 'pdf' in questo caso.
    """
    
    # --- COMANDO PER LINUX (pdf_worker.py) ---
    log_file = f"/home/{linux_user}/worker_pdf.log"

    # Nota: chiamiamo pdf_worker.py invece di smart_worker.py
    cmd_linux_text = (
        f"export DISPLAY=:0 && "
        f"{linux_path}/venv/bin/python {linux_path}/pdf_worker.py {pdf_path}"
    )
    
    # Se il path è vuoto (es. non ci sono PDF per Linux nel json), non eseguiamo su Linux
    cmd_linux = []
    if pdf_path and not pdf_path.startswith("C:"): # Controllo semplice per vedere se è un path linux
        cmd_linux = [
            "ansible", "workers_linux",
            "-i", inventory,
            "-m", "shell",
            "-a", f"nohup sh -c '{cmd_linux_text}' > {log_file} 2>&1 &"
        ]

    # --- COMANDO PER WINDOWS (.bat) ---
    cmd_win = []
    if has_windows and pdf_path and pdf_path.startswith("C:"):
        cmd_win = [
            "ansible", "workers_windows",
            "-i", inventory,
            "-m", "raw",
            # Passiamo il path del pdf e la parola chiave 'pdf'
            "-a", f"{windows_bat_path} {pdf_path} pdf"
        ]

    # ESECUZIONE
    # Nota: Qui la logica è leggermente diversa perché PDF Linux e PDF Windows sono diversi.
    # Dobbiamo gestire il fatto che run_pdf_command viene chiamato con UN path.
    # Vedi la logica modificata in pdf_simulation sotto.
    
    if cmd_linux:
        try:
            subprocess.run(cmd_linux, capture_output=True, text=True)
            print(f"[OK {inventory}] Linux PDF: {pdf_path}")
        except Exception as e:
            print(f"[ERROR {inventory}] Linux PDF cmd: {e}")

    if cmd_win:
        try:
            subprocess.run(cmd_win, capture_output=True, text=True)
            print(f"[OK {inventory}] Windows PDF: {pdf_path}")
        except Exception as e:
            print(f"[ERROR {inventory}] Windows PDF cmd: {e}")


def pdf_simulation(vlan, registration, pdf_json_path, inventory, linux_user, linux_path, windows_user, windows_bat_path):
    print(f"--- AVVIO SIMULAZIONE PDF: {vlan} ---")
    
    reg_config = load_json(registration)
    pdf_config = load_json(pdf_json_path) # Carichiamo il file dei PDF
    
    # Gestione Hosts
    if 'HOSTS_LIST' in reg_config:
        hosts_data = reg_config['HOSTS_LIST']
    elif 'HOSTS_IP_ADDRESS' in reg_config:
        hosts_data = [{'ip': ip, 'os': 'linux'} for ip in reg_config['HOSTS_IP_ADDRESS']]
    else:
        print(f"[FATAL {vlan}] Nessuna lista host trovata.")
        return

    # Liste PDF separate
    pdfs_linux = pdf_config.get('linux', [])
    pdfs_windows = pdf_config.get('windows', [])

    has_windows_hosts = create_ansible_inventory(hosts_data, inventory, linux_user, windows_user)
    
    try:
        while True:
            # 1. LANCIO SU LINUX
            # Se ci sono PDF per Linux, ne peschiamo uno e lanciamo SOLO sui worker Linux
            if pdfs_linux:
                target_pdf = random.choice(pdfs_linux)
                # Chiamiamo funzione specifica passando solo parametri Linux validi
                run_pdf_command(target_pdf, "pdf", False, inventory, linux_user, linux_path, "")
            
            # 2. LANCIO SU WINDOWS
            # Se ci sono host Windows E pdf Windows
            if has_windows_hosts and pdfs_windows:
                target_pdf = random.choice(pdfs_windows)
                # Passiamo has_windows=True e il bat path
                run_pdf_command(target_pdf, "pdf", True, inventory, "", "", windows_bat_path)

            wait_time = random.randint(60, 100)
            print(f"[WAIT {vlan}] Lettura in corso per {wait_time} secondi...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Simulazione PDF interrotta.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore nel loop PDF: {e}")


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
     # Esempio di come potresti lanciare un processo PDF per la Classroom 1
    args_pdf_c1 = (
         "Classroom1_PDF",
         "configs/registration_10.json",
         "configs/pdf_10.json", # NUOVO FILE
         "configs/hosts_10_pdf", # Inventario separato se vuoi
         "student",
         "/home/student/user_behavior_generation/worker",
         "Student",
         "C:\\Users\\Student\\user_behavior_generation\\worker\\browser_task.bat"
     )
    
    #p_pdf = Process(target=pdf_simulation, args=args_pdf_c1)

    p1 = Process(target=simulation, args=args_c1)
    p2 = Process(target=simulation, args=args_c2)
    
    #p_pdf.start()

    p1.start()
    print("[MASTER] Classroom1 avviata.")
    p2.start()
    print("[MASTER] Classroom2 avviata.")

    try:
        p1.join()
        p2.join()
        #p_pdf.join()
    except KeyboardInterrupt:
        print("\n[MASTER] Ricevuto Stop. Termino i processi...")
        p1.terminate()
        p2.terminate()
        #p_pdf.terminate()
        p1.join()
        p2.join()
        #p_pdf.join()
        
        print("[MASTER] Tutti i processi terminati.")

if __name__ == "__main__":
    main()
