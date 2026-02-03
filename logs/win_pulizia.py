import subprocess
import os
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def clear_windows_logs():
    if not is_admin():
        print("[-] Errore: Devi eseguire questo script come Amministratore.")
        return

    # Lista dei log principali da pulire
    logs = ["System", "Application", "Security", "Microsoft-Windows-Sysmon/Operational"]
    
    print("[*] Inizio pulizia log Windows...")
    
    for log in logs:
        try:
            subprocess.run(["wevtutil", "cl", log], check=True)
            print(f"[+] Log pulito: {log}")
        except subprocess.CalledProcessError:
            print(f"[-] Impossibile pulire il log: {log} (Potrebbe non essere installato)")

    print("[!] Pulizia completata.")

if __name__ == "__main__":
    clear_windows_logs()
