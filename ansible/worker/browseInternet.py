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
    Objective: Aprire un URL forzando Edge (Windows) o Firefox (Linux)
    '''
    def browseInternet(self, targetUrl):
        self.logger.info(f"Tentativo di apertura URL: {targetUrl}")
        try:
            # Caso Windows: Forza Microsoft Edge
            if os.name == "nt":
                RNULL = open('NUL', 'r')
                WNULL = open('NUL', 'w')
                # "start msedge" lancia specificamente Edge
                command = f"start msedge {targetUrl}"
                
                # Esegue il comando senza bloccare lo script
                subp = Popen(command, shell=True, stdin=RNULL, stdout=WNULL)
                time.sleep(2) 
            
            # Caso Linux: Forza Mozilla Firefox
            else:
                RNULL = open('/dev/null', 'r')
                WNULL = open('/dev/null', 'w')
                
                # DISPLAY=:0 assicura che si apra a video.
                # --new-tab apre in una scheda se il browser è già aperto (più pulito)
                command = f"DISPLAY=:0 firefox --new-tab {targetUrl}"
                
                subp = Popen(command, shell=True, stdin=RNULL, stdout=WNULL)
                time.sleep(2)

            self.logger.info("Browser lanciato con successo.")

        except Exception as e:
            self.logger.error(f"Errore nell'apertura della pagina: {str(e)}")

# Blocco principale
if __name__ == "__main__":
    bot = simulateBrowser()
    
    # Controlliamo se Ansible ha inviato un URL
    if len(sys.argv) > 1:
        url_input = sys.argv[1]
        bot.browseInternet(url_input)
    else:
        # Fallback per test manuale
        print("Nessun URL fornito, apro Google per test.")
        bot.browseInternet("https://www.google.com")
