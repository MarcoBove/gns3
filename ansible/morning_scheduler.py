import json
import time
import random
import subprocess
import os
import multiprocessing 
import copy
import sys

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



# --- ARGOMENTI (Configurazioni) ---
# Classroom 1
args_c1_web = (
        "Classroom1", 
        "configs/registration_10.json", 
        "configs/websites_10.json", 
        "configs/hosts_10", 
        "student", 
        "/home/student/user_behavior_generation/worker", 
        "Student", 
        "C:\\Users\\Student\\user_behavior_generation\\worker\\browser_task.bat"
    )
args_c1_pdf = (
         "Classroom1",
         "configs/registration_10.json",
         "configs/pdf_10.json", # NUOVO FILE
         "configs/hosts_10", # Inventario separato se vuoi
         "student",
         "/home/student/user_behavior_generation/worker",
         "Student",
         "C:\\Users\\Student\\user_behavior_generation\\worker\\browser_task.bat"
     )

# Classroom 2
args_c2_web = (
        "Classroom2", 
        "configs/registration_20.json", 
        "configs/websites_20.json", 
        "configs/hosts_20", 
        "student", 
        "/home/student/user_behavior_generation/worker", 
        "", 
        ""
    )
args_c2_pdf = (
         "Classroom2",
         "configs/registration_20.json",
         "configs/pdf_20.json", # NUOVO FILE
         "configs/hosts_20", # Inventario separato se vuoi
         "student",
         "/home/student/user_behavior_generation/worker",
         "",
         ""
     )

# Segreteria (Notare che servono args specifici per ogni task)
args_sec_web = (
        "Secretary", 
        "configs/registration_40.json", 
        "configs/websites_40.json", 
        "configs/hosts_40", 
        "", 
        "", 
        "Secretary", 
        "C:\\Users\\Secretary\\user_behavior_generation\\worker\\browser_task.bat"
    )
     
args_sec_pdf = (
         "Secretary",
         "configs/registration_40.json",
         "configs/pdf_40.json", # NUOVO FILE
         "configs/hosts_40", # Inventario separato se vuoi
         "",
         "",
         "Secretary",
         "C:\\Users\\Secretary\\user_behavior_generation\\worker\\browser_task.bat"
     )
args_sec_mail = (
        "Secretary",
        "configs/hosts_40",      # Usa l'inventario esistente
        "C:\\Users\\Secretary\\user_behavior_generation\\worker\\browser_task.bat"
    )
args_sec_print = (
         "Secretary",
         "configs/print_pdf_40.json", # NUOVO FILE
         "configs/hosts_40", # Inventario separato se vuoi
         "C:\\Users\\Secretary\\user_behavior_generation\\worker\\browser_task.bat"
     )


def pick_secretary_task():
    """
    Sceglie il task della segreteria in base alle probabilità:
    - 80%: Web o PDF (scelta a caso tra i due)
    - 10%: Mail
    - 10%: Stampa
    Restituisce: (funzione_da_lanciare, argomenti_da_usare)
    """
    roll = random.randint(1, 100)
    
    if roll <= 80:
        # 80% dei casi: Web o PDF
        # Qui facciamo 50/50 tra Web e PDF
        if random.choice([True, False]):
            return web_simulation, args_sec_web
        else:
            return pdf_simulation, args_sec_pdf
            
    elif roll <= 90:
        # Dal 81 al 90 (10% dei casi): Mail
        return read_mail_simulation, args_sec_mail
        
    else:
        # Dal 91 al 100 (10% dei casi): Stampa
        return print_simulation, args_sec_print


def main():
    print("--- [MAIN 1] AVVIO SCHEDULER: C1 -> SEC -> C2 -> SEC ---", flush=True)
    
    # SEQUENZA
    sequence_steps = ["CLASSROOM1", "SECRETARY", "CLASSROOM2", "SECRETARY"]
    step_index = 0 
    active_processes = []

    try:
        while True:
            # 1. Identifichiamo chi tocca adesso
            current_actor = sequence_steps[step_index]
            
            target_func = None
            target_args = None
            task_type = "UNKNOWN"

            # 2. Logica di selezione
            if current_actor == "CLASSROOM1":
                task_type = random.choice(["WEB", "PDF"])
                if task_type == "WEB":
                    target_func = web_simulation
                    target_args = args_c1_web
                else:
                    target_func = pdf_simulation
                    target_args = args_c1_pdf

            elif current_actor == "CLASSROOM2":
                task_type = random.choice(["WEB", "PDF"])
                if task_type == "WEB":
                    target_func = web_simulation
                    target_args = args_c2_web 
                else:
                    target_func = pdf_simulation
                    target_args = args_c2_pdf

            elif current_actor == "SECRETARY":
                # Qui pick_secretary_task() decide se fare Web, PDF, Mail o Stampa
                target_func, target_args = pick_secretary_task()
                task_type = "AUTO_SECRETARY"

            # 3. Calcolo Tempi Base (5-7 minuti)
            duration_minutes = random.uniform(5, 7)
            duration_seconds = duration_minutes * 60
            
            # --- [MODIFICA RICHIESTA] LOGICA DIMEZZAMENTO TEMPO ---
            # Se la funzione scelta è Mail o Stampa, dimezziamo i secondi.
            # Nota: web_simulation e pdf_simulation NON vengono toccati.
            if target_func == read_mail_simulation or target_func == print_simulation:
                duration_seconds = duration_seconds / 2
                print(f"[MASTER] Attività breve ({target_func.__name__}): Tempo dimezzato.", flush=True)
            # ------------------------------------------------------

            # Calcolo sovrapposizione (sempre 80% del tempo finale calcolato)
            overlap_time = duration_seconds * 0.8
            
            # --- STAMPE DI DEBUG ---
            print(f"\n[MASTER] ------------------------------------------------", flush=True)
            print(f"[MASTER] Step {step_index + 1}/{len(sequence_steps)}: {current_actor}", flush=True)
            
            if isinstance(target_args, (list, tuple)):
                print(f"[MASTER] Target Info: {target_args[0]}", flush=True)
                
            print(f"[MASTER] Task: {target_func.__name__}", flush=True)
            print(f"[MASTER] Durata: {duration_seconds:.0f}s. Attesa Main: {overlap_time:.0f}s", flush=True)

            # 4. Avvio Processo
            if target_func:
                p = multiprocessing.Process(target=target_func, args=(target_args, duration_seconds))
                p.start()
                active_processes.append(p)
            else:
                print(f"[ERROR] Nessuna funzione assegnata per {current_actor}!", flush=True)

            # 5. Pulizia processi
            active_processes = [proc for proc in active_processes if proc.is_alive()]

            # 6. Aggiornamento indice
            step_index = (step_index + 1) % len(sequence_steps)

            # 7. Attesa
            time.sleep(overlap_time)

    except KeyboardInterrupt:
        print("\n[MASTER] Stop ricevuto. Termino i processi...", flush=True)
        for p in active_processes:
            if p.is_alive():
                p.terminate()
        print("[MASTER] Terminato.", flush=True)

    

if __name__ == "__main__":
    main()
