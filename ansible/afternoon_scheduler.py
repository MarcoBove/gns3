import multiprocessing
import time
import random
import subprocess
import sys
import os

# --- CONFIGURAZIONE URL E PATH ---

# 1. LABORATORIO (Tech & Code)
LAB_WEB_URLS = [
    "https://docs.python.org/3/tutorial/index.html",   # Doc Python
    "https://www.w3schools.com/html/default.asp",      # Esercizi Web
    "https://stackoverflow.com/questions"              # Forum Tecnico
]
# Assicurati di aver scaricato i PDF come detto prima
LAB_PDF_PATHS = [
    "/home/student/documents/lab/git_cheat.pdf",
    "/home/student/documents/lab/linux_cheat.pdf"
]

# 2. CLASSROOM 2 (Studenti Generici)
CLASS2_WEB_URLS = [
    "https://it.wikipedia.org/wiki/Portale:Informatica",
    "https://www.studenti.it/appunti/universita/",
    "https://www.ted.com/talks"
]
CLASS2_PDF_PATHS = [
    "/home/student/documents/classroom/turing_paper.pdf",
    "/home/student/documents/classroom/style_guide.pdf"
]

# 3. SEGRETERIA (Admin)
SEC_WEB_URLS = [
    "https://www.gazzettaufficiale.it/",
    "https://www.miur.gov.it/web/guest/notizie",
    "https://www.aranzulla.it/computer/"
]
SEC_PDF_PATHS = [
    "/home/student/documents/secretariat/gdpr_law.pdf",
    "/home/student/documents/secretariat/meeting_rules.pdf"
]

# --- FUNZIONI WORKER (WRAPPERS) ---

def web_simulation(args, duration):
    """Lancia smart_worker.py per navigazione web."""
    url = args[0]
    print(f"   [WORKER] Web: {url} ({duration:.0f}s)", flush=True)
    subprocess.run([sys.executable, "smart_worker.py", url, "generic"], timeout=duration+10)

def pdf_simulation(args, duration):
    """Lancia pdf_worker.py per lettura PDF."""
    path = args[0]
    print(f"   [WORKER] PDF: {path} ({duration:.0f}s)", flush=True)
    subprocess.run([sys.executable, "pdf_worker.py", path, str(int(duration))], timeout=duration+10)

def read_mail_simulation(args, duration):
    """Simula lettura mail (Placeholder o script dedicato)."""
    print(f"   [WORKER] Controllo Posta ({duration:.0f}s)", flush=True)
    # Qui potresti chiamare un 'mail_worker.py' se esiste, o fare un sleep
    time.sleep(duration)

def print_simulation(args, duration):
    """Simula invio stampa (Placeholder o script dedicato)."""
    print(f"   [WORKER] Invio Stampa ({duration:.0f}s)", flush=True)
    # Esempio comando reale: subprocess.run(["lp", "-d", "PDF_Printer", "test_file.txt"])
    time.sleep(duration)

# --- LOGICA DI SCELTA SEGRETERIA ---
def pick_secretary_task():
    """
    La segreteria fa un po' di tutto.
    40% Web, 30% PDF, 20% Mail, 10% Stampa.
    """
    roll = random.random() # numero tra 0.0 e 1.0
    
    if roll < 0.40:
        # Web
        url = random.choice(SEC_WEB_URLS)
        return web_simulation, [url]
    elif roll < 0.70:
        # PDF
        pdf = random.choice(SEC_PDF_PATHS)
        return pdf_simulation, [pdf]
    elif roll < 0.90:
        # Mail
        return read_mail_simulation, []
    else:
        # Stampa
        return print_simulation, []

# --- MAIN LOOP ---
def main():
    print("--- [MAIN 2] AVVIO SCHEDULER: LAB -> SEC -> C2 -> SEC ---", flush=True)
    
    # SEQUENZA DEFINITA
    sequence_steps = ["LABORATORY", "SECRETARY", "CLASSROOM2", "SECRETARY"]
    step_index = 0 
    active_processes = []

    try:
        while True:
            # 1. Chi tocca adesso?
            current_actor = sequence_steps[step_index]
            
            target_func = None
            target_args = None
            
            # 2. Logica di selezione
            if current_actor == "LABORATORY":
                # Il Lab è come una Classroom: o Web Tecnico o PDF Tecnico
                if random.choice(["WEB", "PDF"]) == "WEB":
                    target_func = web_simulation
                    target_args = [random.choice(LAB_WEB_URLS)]
                else:
                    target_func = pdf_simulation
                    target_args = [random.choice(LAB_PDF_PATHS)]

            elif current_actor == "CLASSROOM2":
                if random.choice(["WEB", "PDF"]) == "WEB":
                    target_func = web_simulation
                    target_args = [random.choice(CLASS2_WEB_URLS)]
                else:
                    target_func = pdf_simulation
                    target_args = [random.choice(CLASS2_PDF_PATHS)]

            elif current_actor == "SECRETARY":
                target_func, target_args = pick_secretary_task()

            # 3. Calcolo Tempi (Base 5-7 min)
            duration_minutes = random.uniform(5, 7)
            duration_seconds = duration_minutes * 60
            
            # --- DIMEZZAMENTO TEMPO PER MAIL/STAMPA ---
            if target_func == read_mail_simulation or target_func == print_simulation:
                duration_seconds = duration_seconds / 2
                print(f"[MASTER] Attività rapida Segreteria. Tempo dimezzato.", flush=True)
            # ------------------------------------------

            overlap_time = duration_seconds * 0.8
            
            # --- STAMPE DEBUG ---
            print(f"\n[MASTER] ------------------------------------------------", flush=True)
            print(f"[MASTER] Step {step_index + 1}/{len(sequence_steps)}: {current_actor}", flush=True)
            if target_args:
                print(f"[MASTER] Target: {target_args[0] if target_args else 'Action'}", flush=True)
            print(f"[MASTER] Durata: {duration_seconds:.0f}s. Attesa Main: {overlap_time:.0f}s", flush=True)

            # 4. Avvio Processo
            if target_func:
                p = multiprocessing.Process(target=target_func, args=(target_args, duration_seconds))
                p.start()
                active_processes.append(p)
            
            # 5. Pulizia processi vecchi
            active_processes = [proc for proc in active_processes if proc.is_alive()]

            # 6. Aggiornamento indice
            step_index = (step_index + 1) % len(sequence_steps)

            # 7. Attesa Sovrapposizione
            time.sleep(overlap_time)

    except KeyboardInterrupt:
        print("\n[MASTER] Stop ricevuto. Chiudo tutto...", flush=True)
        for p in active_processes:
            if p.is_alive():
                p.terminate()
        print("[MASTER] Terminato.", flush=True)

if __name__ == "__main__":
    main()
