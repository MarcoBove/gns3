import multiprocessing
import time
import random
import subprocess
import sys
import os

def create_lab_ansible_inventory(hosts_data, inventory, win_user1, win_user2):
    """
    Crea un inventario specifico per il Laboratorio (Solo Windows).
    Genera due gruppi: uno per il primo utente e uno per il secondo.
    """
    windows_hosts = []

    # 1. Filtra gli host (Nel Lab assumiamo siano tutti Windows o forziamo l'uso)
    for host in hosts_data:
        ip = host.get('ip')
        # Se nel json c'è scritto 'linux' per sbaglio, lo ignoriamo o lo trattiamo come win?
        # Qui prendiamo tutto ciò che è windows o che non ha os specificato (assumendo Lab=Win)
        os_type = host.get('os', 'windows').lower()
        
        if os_type == 'windows':
            windows_hosts.append(ip)

    try:
        with open(inventory, 'w') as f:
            # --- GRUPPO 1: Utente Primario (workers_windows) ---
            # Manteniamo questo nome standard così il comando cmd_win1 funziona subito
            f.write("[workers_windows]\n")
            for ip in windows_hosts:
                f.write(f"{ip} ansible_user={win_user1} ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")
            
            # --- GRUPPO 2: Utente Secondario (workers_windows_secondary) ---
            f.write("\n[workers_windows_secondary]\n")
            for ip in windows_hosts:
                f.write(f"{ip} ansible_user={win_user2} ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")

    except Exception as e:
        print(f"[ERROR] Errore scrittura inventario Lab {inventory}: {e}")
        return False
            
    # print(f"[INFO] Inventario Lab {inventory} creato per 2 Utenti su {len(windows_hosts)} Host.")
    return len(windows_hosts) > 0



def run_lab_ansible_command(url1, action1, url2, action2, inventory, win_bat1, win_bat2):
    """
    Lancia comandi WEB diversi per due utenti diversi.
    """
    # --- UTENTE WINDOWS 1 (Gruppo: workers_windows) ---
    cmd_win1 = [
        "ansible", "workers_windows",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{win_bat1} {url1} {action1}"
    ]

    # --- UTENTE WINDOWS 2 (Gruppo: workers_windows_secondary) ---
    cmd_win2 = [
        "ansible", "workers_windows_secondary",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{win_bat2} {url2} {action2}"
    ]

    # Esecuzione Utente 1
    try:
        subprocess.run(cmd_win1, capture_output=True, text=True)
    except Exception as e:
        print(f"[ERROR {inventory}] Win1 Web: {e}")

    # Esecuzione Utente 2
    try:
        subprocess.run(cmd_win2, capture_output=True, text=True)
    except Exception as e:
        print(f"[ERROR {inventory}] Win2 Web: {e}")
    
    print(f"[OK {inventory}] Lab Web Dual: U1->{url1} | U2->{url2}")


def run_lab_pdf_command(pdf1, action1, pdf2, action2, inventory, win_bat1, win_bat2):
    """
    Lancia comandi PDF diversi per due utenti diversi.
    """
    # --- UTENTE WINDOWS 1 (Gruppo: workers_windows) ---
    cmd_win1 = [
        "ansible", "workers_windows",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{win_bat1} {pdf1} {action1}"
    ]

    # --- UTENTE WINDOWS 2 (Gruppo: workers_windows_secondary) ---
    cmd_win2 = [
        "ansible", "workers_windows_secondary",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{win_bat2} {pdf2} {action2}"
    ]

    # Esecuzione Utente 1
    try:
        subprocess.run(cmd_win1, capture_output=True, text=True)
    except Exception as e:
        print(f"[ERROR {inventory}] Win1 PDF: {e}")

    # Esecuzione Utente 2
    try:
        subprocess.run(cmd_win2, capture_output=True, text=True)
    except Exception as e:
        print(f"[ERROR {inventory}] Win2 PDF: {e}")

    print(f"[OK {inventory}] Lab PDF Dual: U1->{pdf1} | U2->{pdf2}")




def web_lab_simulation(args, duration):
    """
    Wrapper WEB Lab: Carica 2 config diversi per 2 utenti.
    Args attesi: vlan, registration, inventory, 
                 websites_1, win_user1, win_bat1, 
                 websites_2, win_user2, win_bat2
    """
    # Unpack esteso
    vlan, registration, inventory, web_json1, win_user1, win_bat1, web_json2, win_user2, win_bat2 = args
    
    print(f"--- AVVIO SIMULAZIONE LAB WEB: {vlan} (Dual Config) ---")
    
    reg_config = load_json(registration)
    
    # 1. Creazione Inventario
    if 'HOSTS_LIST' in reg_config:
        hosts_data = reg_config['HOSTS_LIST']
        create_lab_ansible_inventory(hosts_data, inventory, win_user1, win_user2)
    else:
        print(f"[FATAL {vlan}] Nessuna lista host.")
        return

    # 2. Caricamento e Estrazione URL per UTENTE 1
    config1 = load_json(web_json1)
    raw_entries1 = [site['url'] for site in config1.get('IT', [])]
    
    # 3. Caricamento e Estrazione URL per UTENTE 2
    config2 = load_json(web_json2)
    # Se il config 2 ha una struttura diversa adattalo, qui assumo sia uguale ('IT')
    raw_entries2 = [site['url'] for site in config2.get('IT', [])]

    if not raw_entries1 or not raw_entries2:
        print(f"[WARN {vlan}] Uno dei due file websites è vuoto o non valido.")
        return

    try:
        # Scelta Random U1
        entry1 = random.choice(raw_entries1)
        p1 = entry1.split()
        url1 = p1[0]
        act1 = p1[1] if len(p1) > 1 else "generic"

        # Scelta Random U2
        entry2 = random.choice(raw_entries2)
        p2 = entry2.split()
        url2 = p2[0]
        act2 = p2[1] if len(p2) > 1 else "generic"

        # ESECUZIONE DOPPIA
        run_lab_ansible_command(url1, act1, url2, act2, inventory, win_bat1, win_bat2)
        
        print(f"[WAIT {vlan}] Navigazione in corso ({duration:.0f}s)...")
        time.sleep(duration)

    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Lab Web interrotto.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore Lab Web: {e}")


def pdf_lab_simulation(args, duration):
    """
    Wrapper PDF Lab: Carica 2 config diversi per 2 utenti.
    Args attesi: vlan, registration, inventory, 
                 pdf_json1, win_user1, win_bat1, 
                 pdf_json2, win_user2, win_bat2
    """
    # Unpack esteso
    vlan, registration, inventory, pdf_json1, win_user1, win_bat1, pdf_json2, win_user2, win_bat2 = args
    
    print(f"--- AVVIO SIMULAZIONE LAB PDF: {vlan} (Dual Config) ---")
    
    reg_config = load_json(registration)
    
    # 1. Creazione Inventario
    if 'HOSTS_LIST' in reg_config:
        hosts_data = reg_config['HOSTS_LIST']
        create_lab_ansible_inventory(hosts_data, inventory, win_user1, win_user2)

    # 2. Config Utente 1
    conf1 = load_json(pdf_json1)
    pdfs1 = conf1.get('windows', [])

    # 3. Config Utente 2
    conf2 = load_json(pdf_json2)
    pdfs2 = conf2.get('windows', [])

    if not pdfs1 or not pdfs2:
        print(f"[WARN {vlan}] Liste PDF incomplete per uno dei due utenti.")
        time.sleep(duration)
        return

    try:
        # Scelta Random
        target1 = random.choice(pdfs1)
        target2 = random.choice(pdfs2)
        
        # ESECUZIONE DOPPIA
        run_lab_pdf_command(target1, "pdf", target2, "pdf", inventory, win_bat1, win_bat2)

        print(f"[WAIT {vlan}] Lettura PDF in corso ({duration:.0f}s)...")
        time.sleep(duration)

    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Lab PDF interrotto.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore Lab PDF: {e}")


def main():
    print("--- [MAIN 2] AVVIO SCHEDULER: LAB -> SEC -> C2 -> SEC ---", flush=True)
    
    # SEQUENZA
    sequence_steps = ["LABORATORY", "SECRETARY", "CLASSROOM2", "SECRETARY"]
    step_index = 0 
    active_processes = []

    try:
        while True:
            # 1. Identifichiamo chi tocca adesso
            current_actor = sequence_steps[step_index]
            
            # --- PREPARAZIONE VARIABILI (Così la logica sotto resta pulita) ---
            # Prepariamo gli argomenti randomici PRIMA, così nel blocco if usiamo solo le variabili
            args_lab_web = [random.choice(LAB_WEB_URLS)]
            args_lab_pdf = [random.choice(LAB_PDF_PATHS)]
            args_c2_web  = [random.choice(CLASS2_WEB_URLS)]
            args_c2_pdf  = [random.choice(CLASS2_PDF_PATHS)]
            
            target_func = None
            target_args = None
            task_type = "UNKNOWN"

            # 2. Logica di selezione (PULITA, COME RICHIESTO)
            if current_actor == "LABORATORY":
                task_type = random.choice(["WEB", "PDF"])
                if task_type == "WEB":
                    target_func = web_simulation
                    target_args = args_lab_web
                else:
                    target_func = pdf_simulation
                    target_args = args_lab_pdf

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
            
            # --- LOGICA DIMEZZAMENTO TEMPO ---
            # Se la funzione scelta è Mail o Stampa, dimezziamo i secondi.
            if target_func == read_mail_simulation or target_func == print_simulation:
                duration_seconds = duration_seconds / 2
                print(f"[MASTER] Attività breve ({target_func.__name__}): Tempo dimezzato.", flush=True)
            # ---------------------------------

            # Calcolo sovrapposizione (sempre 80% del tempo finale calcolato)
            overlap_time = duration_seconds * 0.8
            
            # --- STAMPE DI DEBUG ---
            print(f"\n[MASTER] ------------------------------------------------", flush=True)
            print(f"[MASTER] Step {step_index + 1}/{len(sequence_steps)}: {current_actor}", flush=True)
            
            if isinstance(target_args, (list, tuple)) and len(target_args) > 0:
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
