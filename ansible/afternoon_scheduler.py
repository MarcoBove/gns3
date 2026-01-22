import multiprocessing
import time
import random
import subprocess
import sys
import os



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
