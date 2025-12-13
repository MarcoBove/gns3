import os
import sys
import time
from subprocess import Popen

# Classe di log semplice
class SimpleLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")
    def error(self, msg):
        print(f"[ERROR] {msg}")

class simulateBrowser:
    def __init__(self):
        self.logger = SimpleLogger()

    def browseInternet(self, targetUrl):
        self.logger.info(f"Richiesta apertura URL: {targetUrl}")
        
        try:
            # --- CASO WINDOWS ---
            if os.name == "nt":
                RNULL = open('NUL', 'r')
                WNULL = open('NUL', 'w')
                # Apre Edge su Windows
                Popen(f"start msedge {targetUrl}", shell=True, stdin=RNULL, stdout=WNULL)
                time.sleep(2)
            
            # --- CASO LINUX (Xorg Standard) ---
            else:
                RNULL = open('/dev/null', 'r')
                WNULL = open('/dev/null', 'w')
                
                # Configurazione Utente
                # Assicurati che questo sia l'utente corretto sui worker
                remote_user = "osboxes" 
                
                # Su Xorg il file authority è sempre nella home dell'utente.
                # Molto più semplice e stabile.
                auth_file = f"/home/{remote_user}/.Xauthority"
                
                # Comando pulito per Xorg
                command = (
                    f"export DISPLAY=:0 && "
                    f"export XAUTHORITY={auth_file} && "
                    f"/usr/bin/firefox --new-tab {targetUrl}"
                )
                
                # Eseguiamo il comando in background (fire and forget)
                Popen(command, shell=True, stdin=RNULL, stdout=WNULL)
                
                self.logger.info(f"Comando Firefox inviato su DISPLAY=:0")
                time.sleep(2)

        except Exception as e:
            self.logger.error(f"Errore critico: {str(e)}")

if __name__ == "__main__":
    bot = simulateBrowser()
    
    # Prende l'URL dagli argomenti passati da Ansible
    if len(sys.argv) > 1:
        input_url = sys.argv[1]
        bot.browseInternet(input_url)
    else:
        print("Nessun URL fornito, test su Google.")
        bot.browseInternet("https://www.google.com")
