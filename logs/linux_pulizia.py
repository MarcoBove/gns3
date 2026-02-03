import os
import subprocess

def clear_linux_logs():
    if os.geteuid() != 0:
        print("[-] Errore: Devi eseguire questo script con sudo.")
        return

    print("[*] Inizio pulizia log Linux...")

    # 1. Pulizia Auditd
    if os.path.exists("/var/log/audit/audit.log"):
        # Svuota il file senza eliminarlo per evitare problemi di permessi
        with open("/var/log/audit/audit.log", "w") as f:
            f.truncate(0)
        print("[+] Log Auditd svuotato.")

    # 2. Pulizia Syslog e log generici
    logs_to_clear = ["/var/log/syslog", "/var/log/auth.log", "/var/log/messages"]
    for log_path in logs_to_clear:
        if os.path.exists(log_path):
            with open(log_path, "w") as f:
                f.truncate(0)
            print(f"[+] Log svuotato: {log_path}")

    # 3. Pulizia Journald (Log di sistema moderni)
    try:
        subprocess.run(["journalctl", "--vacuum-time=1s"], check=True)
        print("[+] Journald vacuum completato.")
    except Exception as e:
        print(f"[-] Errore durante vacuum journalctl: {e}")

    print("[!] Pulizia completata.")

if __name__ == "__main__":
    clear_linux_logs()
