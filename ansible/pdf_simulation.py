# ... (gli import restano uguali)

# Funzione load_json rimane uguale ...
# Funzione create_ansible_inventory rimane uguale ...
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

def print_simulation(vlan, registration, pdf_json_path, inventory, windows_user, windows_bat_path):
    print(f"--- AVVIO SIMULAZIONE STAMPA: {vlan} ---")
    
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
            wait_time = random.randint(120, 300)
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


def read_mail_simulation(vlan, inventory, windows_user, windows_bat_path):
    print(f"--- AVVIO SIMULAZIONE MAIL: {vlan} ---")
    
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
            wait_time = random.randint(300, 600) 
            print(f"[WAIT {vlan}] Consultazione mail per {wait_time} secondi...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Simulazione Mail interrotta.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore nel loop Mail: {e}")

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

            wait_time = random.randint(30, 60)
            print(f"[WAIT {vlan}] Lettura in corso per {wait_time} secondi...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print(f"\n[STOP {vlan}] Simulazione PDF interrotta.")
    except Exception as e:
        print(f"[CRITICAL {vlan}] Errore nel loop PDF: {e}")

# --- MAIN ESEMPIO ---
def main():
    # Esempio di come potresti lanciare un processo PDF per la Classroom 1
    # args_pdf_c1 = (
    #     "Classroom1_PDF",
    #     "configs/registration_10.json",
    #     "configs/pdf_10.json", # NUOVO FILE
    #     "configs/hosts_10_pdf", # Inventario separato se vuoi
    #     "student",
    #     "/home/student/user_behavior_generation/worker",
    #     "Student",
    #     "C:\\Users\\Student\\user_behavior_generation\\worker\\browser_task.bat"
    # )
    
    # p_pdf = Process(target=pdf_simulation, args=args_pdf_c1)
    # p_pdf.start()
    # ... definizioni precedenti ...

    # Esempio Classroom 1 - MAIL (Solo Windows)
    args_mail_c1 = (
        "Classroom1_Mail",
        "configs/hosts_10",      # Usa l'inventario esistente
        "Student",
        "C:\\Users\\Student\\user_behavior_generation\\worker\\browser_task.bat"
    )

    # p_mail = Process(target=read_mail_simulation, args=args_mail_c1)
    # p_mail.start()
    
    # ... start altri processi ...

if __name__ == "__main__":
    main()
