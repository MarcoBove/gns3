import multiprocessing
import time
import random
import subprocess
import sys
import os

def run_lab_ansible_command(url, action_type, inventory, win_bat1, win_bat2):
    """
    Helper specifico per il Laboratorio:
    Lancia il comando su DUE configurazioni Windows diverse (es. due utenti/task diversi).
    """
    
    # --- COMANDO PER WINDOWS USER 1 ---
    cmd_win1 = [
        "ansible", "workers_windows",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{win_bat1} {url} {action_type}"
    ]

    # --- COMANDO PER WINDOWS USER 2 ---
    cmd_win2 = [
        "ansible", "workers_windows",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{win_bat2} {url} {action_type}"
    ]

    # ESECUZIONE 1
    try:
        # print(f"   [DEBUG] Executing Win1: {win_bat1}")
        subprocess.run(cmd_win1, capture_output=True, text=True)
    except Exception as e:
        print(f"[ERROR {inventory}] Win1 cmd: {e}")

    # ESECUZIONE 2
    try:
        # print(f"   [DEBUG] Executing Win2: {win_bat2}")
        subprocess.run(cmd_win2, capture_output=True, text=True)
    except Exception as e:
        print(f"[ERROR {inventory}] Win2 cmd: {e}")

    print(f"[OK {inventory}] Comandi Lab inviati (2 Utenti) -> {url}")


def web_lab_simulation(args, duration):
    """
    Simulazione WEB specifica per Laboratorio (Solo Windows, 2 Utenti).
    Args attesi: vlan, registration, websites, inventory, win_user1, win_bat1, win_user2, win_bat2
    """
    vlan, registration, websites, inventory, win_user1, win_bat1, win_user2, win_bat2 = args
    
    print(f"--- AVVIO SIMULAZIONE LAB WEB: {vlan} (Dual Windows) ---")
    print(f"--- Tempo: {duration:.1f}s ---")
    
    web_config = load_json(websites)
    reg_config = load_json(registration)

    # Nota: Assumiamo che create_ansible_inventory gestisca la creazione dell'inventario.
    # Se quella funzione accetta solo 2 utenti (linux/win), passagliene uno dei due win come primario, 
    # tanto l'esecuzione usa i .bat path che sono passati nel comando raw.
    if 'HOSTS_LIST' in reg_config:
        hosts_data = reg_config['HOSTS_LIST']
        # Creiamo inventario (passiamo win_user1 come riferimento principale)
        create_ansible_inventory(hosts_data, inventory, "no_linux_user", win_user1)
    else:
        print(f"[FATAL {vlan}] Nessuna lista host trovata.")
        return

    # Estrazione URLs
    raw_entries = [site['url'] for site in web_config.get('IT', [])]
    if not raw_entries:
        print(f"[WARN {vlan}] Nessun URL trovato.")
        return

    try:
        # Loop Singolo (Esegue e poi dorme per tutta la durata)
        # O Loop continuo finché duration non scade (dipende da come vuoi gestirlo, qui faccio single shot + sleep come tuo esempio)
        
        full_entry = random.choice(raw_entries)
        parts = full_entry.split()
        target_url = parts[0]
        action_type = parts[1] if len(parts) > 1 else "generic"

        # Chiamata doppia Windows
        run_lab_ansible_command(target_url, action_type, inventory, win_bat1, win_bat2)
        
        print(f"[WAIT {vlan}] Attesa termine task ({duration:.0f}s)...")
        time.sleep(duration)

    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Lab Web interrotto.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore Lab Web: {e}")


def pdf_lab_simulation(args, duration):
    """
    Simulazione PDF specifica per Laboratorio (Solo Windows, 2 Utenti).
    Args attesi: vlan, registration, pdf_json, inventory, win_user1, win_bat1, win_user2, win_bat2
    """
    vlan, registration, pdf_json_path, inventory, win_user1, win_bat1, win_user2, win_bat2 = args
    
    print(f"--- AVVIO SIMULAZIONE LAB PDF: {vlan} (Dual Windows) ---")
    print(f"--- Tempo: {duration:.1f}s ---")
    
    reg_config = load_json(registration)
    pdf_config = load_json(pdf_json_path)
    
    # 1. Recupero PDF solo per Windows
    pdfs_windows = pdf_config.get('windows', [])
    if not pdfs_windows:
        print(f"[WARN {vlan}] Nessun PDF Windows trovato nel config.")
        time.sleep(duration)
        return

    # 2. Inventario
    if 'HOSTS_LIST' in reg_config:
        hosts_data = reg_config['HOSTS_LIST']
        create_ansible_inventory(hosts_data, inventory, "no_linux_user", win_user1)

    try:
        # Scelta PDF
        target_pdf = random.choice(pdfs_windows)
        
        # Invochiamo l'helper usando come action "pdf"
        # Nota: Assicurati che il tuo .bat gestisca il secondo argomento come 'pdf' action
        run_lab_ansible_command(target_pdf, "pdf", inventory, win_bat1, win_bat2)

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
