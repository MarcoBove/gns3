import os
import sys
import time
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
        self.logger.info(f"Tentativo di apertura URL: {targetUrl}")
        try:
            if os.name == "nt":
                command = f"start msedge {targetUrl}"
            else:
                uid = os.getuid()
                command = (
                    f"DISPLAY=:0 "
                    f"XDG_RUNTIME_DIR=/run/user/{uid} "
                    f"DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus "
                    f"firefox --no-remote --profile /tmp/dapt_profile "
                    f"'{targetUrl}'"
                )

            Popen(command, shell=True,
                  stdin=open('/dev/null', 'r'),
                  stdout=open('/dev/null', 'w'),
                  stderr=open('/dev/null', 'w'))

            self.logger.info("Browser lanciato con successo.")

        except Exception as e:
            self.logger.error(str(e))

if __name__ == "__main__":
    bot = simulateBrowser()
    if len(sys.argv) > 1:
        bot.browseInternet(sys.argv[1])
    else:
        bot.browseInternet("https://www.google.com")
