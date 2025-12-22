student@osboxes:~/user_behavior_generation/worker$ export TMPDIR=/home/student/tmp_firefox && ./venv/bin/python pdf_worker.py /home/student/user_behavior_generation/worker/bdd.pdf
[PDF] Apertura file: file:///home/student/user_behavior_generation/worker/bdd.pdf
[ERROR] Errore driver: Message: binary is not a Firefox executable

Traceback (most recent call last):
  File "/home/student/user_behavior_generation/worker/pdf_worker.py", line 88, in main
    driver = webdriver.Firefox(options=options, service=service)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/student/user_behavior_generation/worker/venv/lib/python3.12/site-packages/selenium/webdriver/firefox/webdriver.py", line 68, in __init__
    super().__init__(command_executor=executor, options=options)
  File "/home/student/user_behavior_generation/worker/venv/lib/python3.12/site-packages/selenium/webdriver/remote/webdriver.py", line 257, in __init__
    self.start_session(capabilities)
  File "/home/student/user_behavior_generation/worker/venv/lib/python3.12/site-packages/selenium/webdriver/remote/webdriver.py", line 352, in start_session
    response = self.execute(Command.NEW_SESSION, caps)["value"]
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/student/user_behavior_generation/worker/venv/lib/python3.12/site-packages/selenium/webdriver/remote/webdriver.py", line 432, in execute
    self.error_handler.check_response(response)
  File "/home/student/user_behavior_generation/worker/venv/lib/python3.12/site-packages/selenium/webdriver/remote/errorhandler.py", line 232, in check_response
    raise exception_class(message, screen, stacktrace)
selenium.common.exceptions.InvalidArgumentException: Message: binary is not a Firefox executable

student@osboxes:~/user_behavior_generation/worker$ which firefox
/usr/bin/firefox


# --- CONFIGURAZIONE LINUX (Firefox) ---
        if "linux" in sys.platform:
            options = FirefoxOptions()
            
            # TENTATIVO 1: Cerca il binario vero di Snap (Standard su Ubuntu/osboxes)
            snap_binary = "/snap/firefox/current/usr/lib/firefox/firefox"
            
            # TENTATIVO 2: Cerca il binario classico
            classic_binary = "/usr/bin/firefox"
            
            if os.path.exists(snap_binary):
                print(f"[DEBUG] Trovato Firefox Snap: {snap_binary}")
                options.binary_location = snap_binary
            else:
                # Se non è Snap, proviamo quello standard, ma potrebbe fallire se è un wrapper
                print(f"[DEBUG] Uso Firefox Standard: {classic_binary}")
                options.binary_location = classic_binary

            # FIX TMPDIR: Fondamentale per Firefox Snap altrimenti crasha
            # Se la cartella tmp non esiste o non ha permessi, Selenium muore.
            os.environ["TMPDIR"] = f"/home/{os.environ.get('USER', 'student')}/tmp_firefox"
            
            service = FirefoxService()
            # Se geckodriver non è nel PATH globale, specifica qui il percorso:
            # service = FirefoxService(executable_path="/home/student/user_behavior_generation/worker/geckodriver")
            
            driver = webdriver.Firefox(options=options, service=service)
