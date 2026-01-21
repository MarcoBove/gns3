import multiprocessing
import time
import random

# --- FUNZIONI SIMULATE (Assicurati che accettino 'args' e 'duration') ---
# Incolla qui le tue funzioni reali (web_simulation, pdf_simulation, ecc.)
# Per brevità metto delle versioni placeholder che stampano e basta.

def web_simulation(args, duration):
    name = args[0] # Assumiamo che il primo elemento sia il nome
    print(f"   -> [AVVIO] WEB Simulation su {name}. Durata: {duration:.0f}s")
    time.sleep(duration)
    print(f"   -> [FINE] WEB Simulation {name} terminata.")

def pdf_simulation(args, duration):
    name = args[0]
    print(f"   -> [AVVIO] PDF Simulation su {name}. Durata: {duration:.0f}s")
    time.sleep(duration)
    print(f"   -> [FINE] PDF Simulation {name} terminata.")

def read_mail_simulation(args, duration):
    name = args[0]
    print(f"   -> [AVVIO] MAIL Simulation su {name}. Durata: {duration:.0f}s")
    time.sleep(duration)
    print(f"   -> [FINE] MAIL Simulation {name} terminata.")

def print_simulation(args, duration):
    name = args[0]
    print(f"   -> [AVVIO] PRINT Simulation su {name}. Durata: {duration:.0f}s")
    time.sleep(duration)
    print(f"   -> [FINE] PRINT Simulation {name} terminata.")

# --- ARGOMENTI (Configurazioni) ---
# Classroom 1
args_c1_web = ("Classroom1", "WebConfig...")
args_c1_pdf = ("Classroom1", "PdfConfig...")

# Classroom 2
args_c2_web = ("Classroom2", "WebConfig...")
args_c2_pdf = ("Classroom2", "PdfConfig...")

# Segreteria (Notare che servono args specifici per ogni task)
args_sec_web = ("Secretary", "WebConfig...")
args_sec_pdf = ("Secretary", "PdfConfig...")
args_sec_mail = ("Secretary", "MailConfig...")
args_sec_print = ("Secretary", "PrintConfig...")


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
    print("--- [MAIN 1] AVVIO SCHEDULER: C1 -> SEC -> C2 -> SEC ---")
    
    # DEFINIZIONE SEQUENZA
    # Questa lista verrà ripetuta all'infinito
    sequence_steps = ["CLASSROOM1", "SECRETARY", "CLASSROOM2", "SECRETARY"]
    
    step_index = 0 # Indice per scorrere la lista
    active_processes = []

    try:
        while True:
            # 1. Identifichiamo chi tocca adesso
            current_actor = sequence_steps[step_index]
            
            target_func = None
            target_args = None

            # 2. Logica di selezione in base all'attore
            if current_actor == "CLASSROOM1":
                # Scelta casuale tra Web e PDF
                if random.choice(["WEB", "PDF"]) == "WEB":
                    target_func = web_simulation
                    target_args = args_c1_web
                else:
                    target_func = pdf_simulation
                    target_args = args_c1_pdf

            elif current_actor == "CLASSROOM2":
                # Scelta casuale tra Web e PDF
                if random.choice(["WEB", "PDF"]) == "WEB":
                    target_func = web_simulation
                    target_args = args_c2_web
                else:
                    target_func = pdf_simulation
                    target_args = args_c2_pdf

            elif current_actor == "SECRETARY":
                # Logica complessa con percentuali
                target_func, target_args = pick_secretary_task()

            # 3. Calcolo Tempi (5-7 minuti)
            duration_minutes = random.uniform(5, 7)
            duration_seconds = duration_minutes * 60
            overlap_time = duration_seconds * 0.8
            
            print(f"\n[MASTER] Step: {current_actor}")
            print(f"[MASTER] Task: {target_func.__name__}. Durata: {duration_seconds:.0f}s. Prossimo avvio tra: {overlap_time:.0f}s")

            # 4. Avvio Processo
            p = multiprocessing.Process(target=target_func, args=(target_args, duration_seconds))
            p.start()
            active_processes.append(p)

            # 5. Pulizia processi terminati (Housekeeping)
            active_processes = [proc for proc in active_processes if proc.is_alive()]

            # 6. Aggiornamento indice per il prossimo giro (Loop circolare)
            step_index = (step_index + 1) % len(sequence_steps)

            # 7. Attesa Sovrapposizione (80%)
            time.sleep(overlap_time)

    except KeyboardInterrupt:
        print("\n[MASTER] Stop ricevuto. Termino i processi...")
        for p in active_processes:
            if p.is_alive():
                p.terminate()
        print("[MASTER] Terminato.")

if __name__ == "__main__":
    main()
