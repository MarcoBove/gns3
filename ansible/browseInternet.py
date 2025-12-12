import os
import sys
import time
from subprocess import Popen

# Simuliamo il logger per evitare dipendenze esterne complicate per ora
class SimpleLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")
    def error(self, msg):
        print(f"[ERROR] {msg}")

class simulateBrowser:
    def __init__(self):
        self.logger = SimpleLogger()

    '''
    Function: browseInternet
    Objective: Aprire un URL nel browser di default del sistema
    '''
    def browseInternet(self, targetUrl):
        self.logger.info(f"Tentativo di apertura URL: {targetUrl}")
        try:
            # Caso Windows (se mai dovessi usarlo)
            if os.name == "nt":
                RNULL = open('NUL', 'r')
                WNULL = open('NUL', 'w')
                command = f"start {targetUrl}"
                # Esegue il comando senza bloccare lo script
                subp = Popen(command, shell=True, stdin=RNULL, stdout=WNULL)
                time.sleep(2) 
            
            # Caso Linux (Le tue macchine)
            else:
                RNULL = open('/dev/null', 'r')
                WNULL = open('/dev/null', 'w')
                # DISPLAY=:0 è necessario per dire a Linux di aprire la finestra sul monitor principale
                command = f"DISPLAY=:0 xdg-open {targetUrl}" 
                subp = Popen(command, shell=True, stdin=RNULL, stdout=WNULL)
                time.sleep(2)

            self.logger.info("Browser lanciato con successo.")

        except Exception as e:
            self.logger.error(f"Errore nell'apertura della pagina: {str(e)}")

# Blocco per testare lo script da solo senza Ansible
if __name__ == "__main__":
    # Test rapido: prova ad aprire Google
    bot = simulateBrowser()
    bot.browseInternet("https://www.google.com")
