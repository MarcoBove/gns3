import os
import sys
import time
import glob
from subprocess import Popen

class SimpleLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")
    def error(self, msg):
        print(f"[ERROR] {msg}")

class simulateBrowser:
    def __init__(self):
        self.logger = SimpleLogger()

    def browseInternet(self, targetUrl):
        self.logger.info(f"Target URL: {targetUrl}")
        
        if os.name == "nt":
            # Windows
            RNULL = open('NUL', 'r')
            WNULL = open('NUL', 'w')
            Popen(f"start msedge {targetUrl}", shell=True, stdin=RNULL, stdout=WNULL)
            time.sleep(2)
        else:
            # LINUX
            # Percorso base dove hai trovato il file
            base_dir = "/run/user/1000/"
            
            # Cerchiamo qualsiasi file che inizi con .mutter-Xwaylandauth
            # Il * significa "qualsiasi cosa ci sia dopo"
            pattern = os.path.join(base_dir, ".mutter-Xwaylandauth.*")
            found_files = glob.glob(pattern)
            
            auth_file = ""
            
            if found_files:
                # Prendiamo il primo che troviamo (es. .mutter-Xwaylandauth.ILLAH3)
                auth_file = found_files[0]
                self.logger.info(f"Trovato file auth dinamico: {auth_file}")
            else:
                # Fallback se non lo trova (magari in futuro cambia)
                self.logger.error("Non ho trovato il file mutter! Provo .Xauthority standard.")
                auth_file = "/home/osboxes/.Xauthority"

            # Costruiamo il comando con il file trovato
            command = (
                f"export DISPLAY=:0 && "
                f"export XAUTHORITY={auth_file} && "
                f"export GDK_BACKEND=x11 && " # Importante per Wayland
                f"/usr/bin/firefox --new-tab {targetUrl}"
            )
            
            try:
                # Usiamo devnull per pulizia
                RNULL = open('/dev/null', 'r')
                WNULL = open('/dev/null', 'w')
                Popen(command, shell=True, stdin=RNULL, stdout=WNULL)
                self.logger.info("Firefox lanciato.")
                time.sleep(2)
            except Exception as e:
                self.logger.error(f"Errore: {e}")

if __name__ == "__main__":
    bot = simulateBrowser()
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.google.com"
    bot.browseInternet(url)
