def setup_driver(browser_type="edge"):
    """Inizializza il browser. Se offline, usa il driver locale."""
    driver = None
    try:
        if browser_type == "edge":
            options = webdriver.EdgeOptions()
            options.add_argument("--start-maximized")
            # options.add_argument("--headless") 

            try:
                # Tenta la via automatica (richiede internet)
                service = EdgeService(EdgeChromiumDriverManager().install())
            except Exception as e:
                print(f"[WARN] Impossibile scaricare driver online. Uso driver locale. Err: {e}")
                # Percorso manuale al file che hai copiato
                # ATTENZIONE: Assicurati che il percorso sia corretto!
                local_driver_path = r"C:\Users\User\dapt2021\worker\msedgedriver.exe"
                service = EdgeService(local_driver_path)

            driver = webdriver.Edge(service=service, options=options)
        
        # (Lasciamo Chrome e Firefox come erano, o applica logica simile se serve)
        elif browser_type == "chrome":
             # ... codice chrome esistente ...
             pass
        elif browser_type == "firefox":
             # ... codice firefox esistente ...
             pass
            
        return driver
    except Exception as e:
        print(f"[ERROR] Driver init failed: {e}")
        return None
