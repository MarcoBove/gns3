import multiprocessing
import time
import random
import subprocess
import sys
import os

def run_lab_ansible_command(url, action_type, inventory, win_bat1, win_bat2):
    """
    Lancia i comandi WEB per il Laboratorio su DUE utenti Windows.
    Sostituisce run_ansible_command.
    """
    # --- UTENTE WINDOWS 1 ---
    cmd_win1 = [
        "ansible", "workers_windows",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{win_bat1} {url} {action_type}"
    ]

    # --- UTENTE WINDOWS 2 ---
    cmd_win2 = [
        "ansible", "workers_windows",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{win_bat2} {url} {action_type}"
    ]

    # Esecuzione
    try:
        subprocess.run(cmd_win1, capture_output=True, text=True)
        # print(f"[DEBUG] Win1 Web avviato.")
    except Exception as e:
        print(f"[ERROR {inventory}] Win1 Web: {e}")

    try:
        subprocess.run(cmd_win2, capture_output=True, text=True)
        # print(f"[DEBUG] Win2 Web avviato.")
    except Exception as e:
        print(f"[ERROR {inventory}] Win2 Web: {e}")
    
    print(f"[OK {inventory}] Lab Web inviato (2 Users) -> {url}")


def run_lab_pdf_command(pdf_path, action_type, inventory, win_bat1, win_bat2):
    """
    Lancia i comandi PDF per il Laboratorio su DUE utenti Windows.
    Sostituisce run_pdf_command.
    """
    # --- UTENTE WINDOWS 1 ---
    cmd_win1 = [
        "ansible", "workers_windows",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{win_bat1} {pdf_path} {action_type}"
    ]

    # --- UTENTE WINDOWS 2 ---
    cmd_win2 = [
        "ansible", "workers_windows",
        "-i", inventory,
        "-m", "raw",
        "-a", f"{win_bat2} {pdf_path} {action_type}"
    ]

    # Esecuzione
    try:
        subprocess.run(cmd_win1, capture_output=True, text=True)
        # print(f"[DEBUG] Win1 PDF avviato.")
    except Exception as e:
        print(f"[ERROR {inventory}] Win1 PDF: {e}")

    try:
        subprocess.run(cmd_win2, capture_output=True, text=True)
        # print(f"[DEBUG] Win2 PDF avviato.")
    except Exception as e:
        print(f"[ERROR {inventory}] Win2 PDF: {e}")

    print(f"[OK {inventory}] Lab PDF inviato (2 Users) -> {pdf_path}")


def web_lab_simulation(args, duration):
    """
    Wrapper per simulazione WEB in Laboratorio.
    Chiama: run_lab_ansible_command
    """
    # Unpack degli argomenti (Tutti per Windows)
    vlan, registration, websites, inventory, win_user1, win_bat1, win_user2, win_bat2 = args
    
    print(f"--- AVVIO SIMULAZIONE LAB WEB: {vlan} ---")
    
    reg_config = load_json(registration)
    web_config = load_json(websites)
    
    # 1. Creazione Inventario (Usiamo win_user1 come riferimento, niente Linux)
    if 'HOSTS_LIST' in reg_config:
        hosts_data = reg_config['HOSTS_LIST']
        create_ansible_inventory(hosts_data, inventory, "no_linux", win_user1)
    else:
        print(f"[FATAL {vlan}] Nessuna lista host.")
        return

    # 2. Estrazione URL
    raw_entries = [site['url'] for site in web_config.get('IT', [])]
    if not raw_entries:
        print(f"[WARN {vlan}] Nessun URL trovato.")
        return

    try:
        # Loop o Single Shot (qui single shot per durata)
        full_entry = random.choice(raw_entries)
        parts = full_entry.split()
        target_url = parts[0]
        action_type = parts[1] if len(parts) > 1 else "generic"

        # CHIAMATA ALLA FUNZIONE DEDICATA WEB
        run_lab_ansible_command(target_url, action_type, inventory, win_bat1, win_bat2)
        
        print(f"[WAIT {vlan}] Navigazione in corso ({duration:.0f}s)...")
        time.sleep(duration)

    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Lab Web interrotto.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore Lab Web: {e}")


def pdf_lab_simulation(args, duration):
    """
    Wrapper per simulazione PDF in Laboratorio.
    Chiama: run_lab_pdf_command
    """
    # Unpack degli argomenti
    vlan, registration, pdf_json_path, inventory, win_user1, win_bat1, win_user2, win_bat2 = args
    
    print(f"--- AVVIO SIMULAZIONE LAB PDF: {vlan} ---")
    
    reg_config = load_json(registration)
    pdf_config = load_json(pdf_json_path)
    
    # 1. Creazione Inventario
    if 'HOSTS_LIST' in reg_config:
        hosts_data = reg_config['HOSTS_LIST']
        create_ansible_inventory(hosts_data, inventory, "no_linux", win_user1)

    # 2. Recupero PDF (Solo lista Windows)
    pdfs_windows = pdf_config.get('windows', [])
    if not pdfs_windows:
        print(f"[WARN {vlan}] Nessun PDF Windows trovato.")
        time.sleep(duration)
        return

    try:
        target_pdf = random.choice(pdfs_windows)
        
        # CHIAMATA ALLA FUNZIONE DEDICATA PDF
        # Passiamo "pdf" come action_type
        run_lab_pdf_command(target_pdf, "pdf", inventory, win_bat1, win_bat2)

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
