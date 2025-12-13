import json
import time
import random
import subprocess
import os

# --- CONFIGURAZIONE ---
ANSIBLE_INVENTORY = "configs/hosts"
REGISTRATION_FILE = "configs/registration.json"
WEBSITES_FILE = "configs/websites.json"

# Nome utente remoto (deve essere uguale su tutte le macchine worker)
REMOTE_USER = "tuo_nome_utente"  # <--- CAMBIA QUESTO!
REMOTE_WORKER_PATH = "/home/" + REMOTE_USER + "/dapt2021/worker" 

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def create_ansible_inventory(ip_list):
    """Crea un file inventory semplice per Ansible"""
    with open(ANSIBLE_INVENTORY, 'w') as f:
        f.write("[workers]\n")
        for ip in ip_list:
            f.write(f"{ip} ansible_user={REMOTE_USER} ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")
    print(f"[INFO] Inventario Ansible creato con {len(ip_list)} host.")

def run_ansible_command(url):
    """Lancia il comando di browsing su TUTTI i worker"""
    
    # Aggiungiamo export DISPLAY=:0 per agganciare la sessione grafica
    remote_cmd = f"export DISPLAY=:0 && python3 {REMOTE_WORKER_PATH}/browseInternet.py '{url}'"
    
    print(f"[ACTION] Apertura URL: {url} su tutti i worker...")
    
    # Comando Ansible ottimizzato per GUI remote
    cmd = [
        "ansible", "workers",
        "-i", ANSIBLE_INVENTORY,
        "-m", "shell",
        "-a", f"nohup sh -c '{remote_cmd}' > /dev/null 2>&1 &"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Comando inviato correttamente.")
        else:
            print(f"[ERROR] Errore Ansible:\n{result.stderr}")
    except Exception as e:
        print(f"[ERROR] Eccezione: {e}")

def main():
    print("--- AVVIO SCHEDULER SEMPLIFICATO ---")
    
    # 1. Leggi configurazioni
    reg_config = load_json(REGISTRATION_FILE)
    web_config = load_json(WEBSITES_FILE)
    
    ips = reg_config['HOSTS_IP_ADDRESS']
    urls = [site['url'] for site in web_config['IT']] # Prendiamo solo gli URL del dipartimento IT
    
    # 2. Prepara Ansible
    create_ansible_inventory(ips)
    
    # 3. Loop infinito di simulazione
    try:
        while True:
            # Scegli un URL a caso
            target_url = random.choice(urls)
            
            # Lancia il comando
            run_ansible_command(target_url)
            
            # Attendi un tempo casuale tra 10 e 30 secondi
            wait_time = random.randint(10, 30)
            print(f"[WAIT] Attesa di {wait_time} secondi...\n")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\n[STOP] Simulazione interrotta dall'utente.")

if __name__ == "__main__":
    main()
