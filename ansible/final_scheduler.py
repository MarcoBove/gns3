import json
import time
import random
import subprocess
import os
from multiprocessing import Process
import copy

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

def web_simulation(args, duration):
    vlan, registration, websites, inventory, linux_user, linux_path, windows_user, windows_bat_path = args
    print(f"--- AVVIO SIMULAZIONE WEB: {vlan} ---")
    print(f"--- Tempo assegnato dallo scheduler: {duration:.1f} secondi ---")
    
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
            
            wait_time = duration #random.randint(60, 100)
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


def pdf_simulation(args, duration):
    vlan, registration, pdf_json_path, inventory, linux_user, linux_path, windows_user, windows_bat_path = args
    print(f"--- AVVIO SIMULAZIONE PDF: {vlan} ---")
    print(f"--- Tempo assegnato dallo scheduler: {duration:.1f} secondi ---")
    
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

            wait_time = duration #random.randint(60, 100)
            print(f"[WAIT {vlan}] Lettura in corso per {wait_time} secondi...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Simulazione PDF interrotta.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore nel loop PDF: {e}")


def run_print_command(pdf_path, has_windows, inventory, windows_bat_path):
    """
    Invia comando di stampa solo a Windows.
    """
    if not has_windows:
        return

    # Comando: path_del_pdf print
    cmd_win = [
        "ansible", "workers_windows",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{windows_bat_path} {pdf_path} print"
    ]

    try:
        subprocess.run(cmd_win, capture_output=True, text=True)
        print(f"[OK {inventory}] Stampa inviata: {pdf_path}")
    except Exception as e:
        print(f"[ERROR {inventory}] Print cmd: {e}")

def print_simulation(args, duration):
    vlan, pdf_json_path, inventory, windows_bat_path = args
    print(f"--- AVVIO SIMULAZIONE STAMPA: {vlan} ---")
    print(f"--- Tempo assegnato dallo scheduler: {duration:.1f} secondi ---")
    
    # Usiamo lo stesso file JSON dei PDF che usiamo per la lettura
    pdf_config = load_json(pdf_json_path)
    
    # Ci servono solo i PDF di Windows
    pdfs_windows = pdf_config.get('windows', [])
    
    if not pdfs_windows:
        print(f"[WARN {vlan}] Nessun PDF Windows trovato per la stampa.")
        return

    # Check hosts (semplificato)
    has_windows = True

    try:
        while True:
            # Scegli un PDF a caso
            target_pdf = random.choice(pdfs_windows)
            
            # Lancia la stampa
            run_print_command(target_pdf, has_windows, inventory, windows_bat_path)
            
            # Attesa realistica tra una stampa e l'altra (es. ogni 2-5 minuti)
            wait_time = duration #random.randint(120, 300)
            print(f"[WAIT {vlan}] Prossima stampa tra {wait_time} secondi...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Simulazione Stampa interrotta.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore loop Stampa: {e}")

def run_mail_command(has_windows, inventory, windows_bat_path):
    """
    Lancia il comando Mail solo su Windows.
    """
    if not has_windows:
        return

    # Argomento 1: "gmail" (testo a caso, tanto il bat lo ignora nel caso mail)
    # Argomento 2: "mail" (l'azione che attiva l'if nel bat)
    cmd_win = [
        "ansible", "workers_windows",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{windows_bat_path} gmail mail"
    ]

    try:
        subprocess.run(cmd_win, capture_output=True, text=True)
        print(f"[OK {inventory}] Mail avviata su Windows")
    except Exception as e:
        print(f"[ERROR {inventory}] Mail cmd: {e}")


def read_mail_simulation(args, duration):
    vlan, inventory, windows_bat_path = args
    print(f"--- AVVIO SIMULAZIONE MAIL: {vlan} ---")
    print(f"--- Tempo assegnato dallo scheduler: {duration:.1f} secondi ---")
    
    # Creiamo un inventario al volo solo per windows (se serve) o usiamo quello esistente
    # Nota: qui semplifico assumendo che l'inventario sia già popolato o fisso.
    # Se devi ricrearlo dinamicamente usa create_ansible_inventory come nelle altre funzioni.
    
    # Controllo veloce se ci sono host windows nell'inventario
    # (Per semplicità assumiamo True se lanciamo questa funzione)
    has_windows = True 
    
    try:
        while True:
            # Lancia Gmail
            run_mail_command(has_windows, inventory, windows_bat_path)
            
            # Lascia la mail aperta per molto tempo (es. 5-10 minuti)
            # O il tempo che preferisci
            wait_time = duration #random.randint(300, 600) 
            print(f"[WAIT {vlan}] Consultazione mail per {wait_time} secondi...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Simulazione Mail interrotta.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore nel loop Mail: {e}")


def main():
    print("--- AVVIO SCHEDULER ---")

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

    args_lab = (
        "Laboratory", 
        "configs/registration_50.json", 
        "configs/websites_50.json", 
        "configs/hosts_50", 
        "", 
        "", 
        "LabUser", 
        "C:\\Users\\LabUser\\user_behavior_generation\\worker\\browser_task.bat"
    )

    args_sec = (
        "Secretary", 
        "configs/registration_40.json", 
        "configs/websites_40.json", 
        "configs/hosts_40", 
        "", 
        "", 
        "Secretary", 
        "C:\\Users\\Secretary\\user_behavior_generation\\worker\\browser_task.bat"
    )
     
    args_pdf_c1 = (
         "Classroom1",
         "configs/registration_10.json",
         "configs/pdf_10.json", # NUOVO FILE
         "configs/hosts_10", # Inventario separato se vuoi
         "student",
         "/home/student/user_behavior_generation/worker",
         "Student",
         "C:\\Users\\Student\\user_behavior_generation\\worker\\browser_task.bat"
     )
    
    args_pdf_c2 = (
         "Classroom2",
         "configs/registration_20.json",
         "configs/pdf_20.json", # NUOVO FILE
         "configs/hosts_20", # Inventario separato se vuoi
         "student",
         "/home/student/user_behavior_generation/worker",
         "",
         ""
     )
    
    args_pdf_lab = (
         "Laboratory",
         "configs/registration_50.json",
         "configs/pdf_50.json", # NUOVO FILE
         "configs/hosts_50", # Inventario separato se vuoi
         "",
         "",
         "LabUser",
         "C:\\Users\\LabUser\\user_behavior_generation\\worker\\browser_task.bat"
     )
    
    args_pdf_sec = (
         "Secretary",
         "configs/registration_40.json",
         "configs/pdf_40.json", # NUOVO FILE
         "configs/hosts_40", # Inventario separato se vuoi
         "",
         "",
         "Secretary",
         "C:\\Users\\Secretary\\user_behavior_generation\\worker\\browser_task.bat"
     )

    
    args_mail_sec = (
        "Secretary",
        "configs/hosts_40",      # Usa l'inventario esistente
        "C:\\Users\\Secretary\\user_behavior_generation\\worker\\browser_task.bat"
    )

    args_print_sec = (
         "Secretary",
         "configs/print_pdf_40.json", # NUOVO FILE
         "configs/hosts_40", # Inventario separato se vuoi
         "C:\\Users\\Secretary\\user_behavior_generation\\worker\\browser_task.bat"
     )
    

    # 1. CREAZIONE STRUTTURA MASTER
    # Ogni lista interna rappresenta un "Gruppo" (Classroom, Lab, ecc.)
    # Ogni elemento è una tupla: (FUNZIONE_DA_LANCIARE, ARGOMENTI)
    master_structure = [
        # Classroom 1 Group
        [
            (web_simulation, args_c1),
            (pdf_simulation, args_pdf_c1)
        ],
        # Classroom 2 Group
        [
            (web_simulation, args_c2),
            (pdf_simulation, args_pdf_c2)
        ],
        # Laboratory Group
        [
            (web_simulation, args_lab), # Ipotizzo web_simulation per args_lab
            (pdf_simulation, args_pdf_lab)
        ],
        # Secretary Group
        [
            (web_simulation, args_sec),
            (pdf_simulation, args_pdf_sec),
            (read_mail_simulation, args_mail_sec),
            (print_simulation, args_print_sec)
        ]
    ]

    cycle_count = 1
    active_processes = []

    try:
        while True: # Ciclo infinito di riavvio (Reset)
            print(f"\n--- [MASTER] INIZIO CICLO {cycle_count} ---")
            
            # 2. RESET: Creiamo una copia di lavoro per non svuotare il master
            # Usiamo deepcopy per essere sicuri di avere liste nuove modificabili
            working_pool = copy.deepcopy(master_structure)

            # Finché ci sono gruppi disponibili nella lista
            while len(working_pool) > 0:
                
                # A. SCELTA CASUALE DEL GRUPPO
                group_index = random.randint(0, len(working_pool) - 1)
                selected_group = working_pool[group_index]

                # B. SCELTA CASUALE DELL'ARGOMENTO NEL GRUPPO
                task_index = random.randint(0, len(selected_group) - 1)
                target_func, task_args = selected_group[task_index]

                # C. CALCOLO TEMPI (5-7 minuti)
                # Per testare velocemente, puoi cambiare 300, 420 in 3, 5 secondi
                duration_minutes = random.uniform(5, 7) 
                duration_seconds = duration_minutes * 60 
                
                # Calcolo il momento di avvio del prossimo (80% della durata)
                overlap_time = duration_seconds * 0.8
                
                print(f"[MASTER] Scelto Gruppo {group_index}, Task {task_args}.")
                print(f"[MASTER] Durata totale: {duration_seconds:.1f}s. Prossimo avvio tra: {overlap_time:.1f}s")

                # D. AVVIO PROCESSO
                # Nota: Passo 'duration_seconds' alla funzione così sa quanto durare.
                # Se le tue funzioni non accettano duration, fammelo sapere.
                p = Process(target=target_func, args=(task_args, duration_seconds))
                p.start()
                active_processes.append(p)

                # E. RIMOZIONE (CONSUMPTION)
                # Rimuovo il task usato dal gruppo
                selected_group.pop(task_index)
                
                # Se il gruppo è vuoto, rimuovo il gruppo dalla pool
                if len(selected_group) == 0:
                    working_pool.pop(group_index)
                    print(f"[MASTER] Gruppo {group_index} svuotato e rimosso.")

                # F. PULIZIA PROCESSI MORTI (Opzionale ma consigliato)
                # Controlliamo se qualche processo vecchio ha finito
                active_processes = [proc for proc in active_processes if proc.is_alive()]

                # G. ATTESA SOVRAPPOSIZIONE (Sleep del Master)
                # Il master dorme per l'80%, poi si sveglia e lancia il prossimo
                time.sleep(overlap_time)

            print(f"[MASTER] Ciclo {cycle_count} completato. Tutte le variabili usate. Riavvio...")
            cycle_count += 1
            # Qui potresti mettere un time.sleep extra se vuoi una pausa tra i cicli completi

    except KeyboardInterrupt:
        print("\n[MASTER] Stop ricevuto. Termino tutti i processi attivi...")
        for p in active_processes:
            if p.is_alive():
                p.terminate()
        print("[MASTER] Chiusura completata.")
    


if __name__ == "__main__":

    main()

