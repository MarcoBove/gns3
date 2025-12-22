import sys
import time
import random
import pathlib
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# Import per Firefox (Linux)
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

# Import per Edge (Windows)
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService

def scroll_reading_mode_keyboard(driver, duration):
    """
    Simula la lettura usando la TASTIERA (Freccia Giù).
    Molto più affidabile per i PDF rispetto a JavaScript.
    """
    end_time = time.time() + duration
    
    print(f"[PDF] Inizio lettura simulata per {duration} secondi...")
    
    # Creiamo un oggetto ActionChains per simulare i tasti
    actions = ActionChains(driver)
    
    # Clicchiamo sulla pagina per assicurarci che abbia il focus
    try:
        driver.find_element(By.TAG_NAME, "body").click()
    except:
        pass # Se non riesce a cliccare, prova comunque a scrollare

    while time.time() < end_time:
        # Premiamo "Freccia Giù" alcune volte (simula l'occhio che scende)
        scroll_steps = random.randint(3, 10) # 3-10 pressioni
        
        for _ in range(scroll_steps):
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(random.uniform(0.05, 0.2)) # Piccola pausa tra pressioni tasti
        
        # Pausa di lettura (l'utente si ferma a leggere un paragrafo)
        time.sleep(random.uniform(1.0, 3.0))
        
        # Ogni tanto torna su (Page Up) per rileggere
        if random.random() < 0.1:
            actions.send_keys(Keys.PAGE_UP).perform()
            time.sleep(1.5)

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_worker.py <local_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    
    # Controlliamo se il file esiste
    if not os.path.exists(file_path):
        print(f"[ERROR] File non trovato: {file_path}")
        sys.exit(1)

    # Conversione path -> URL file:///
    target_url = pathlib.Path(file_path).absolute().as_uri()
    print(f"[PDF] Apertura file: {target_url}")

    driver = None

    try:
        # --- CONFIGURAZIONE LINUX (Firefox) ---
        if "linux" in sys.platform:
            options = FirefoxOptions()
            
            # FIX CRITICO: Specifichiamo dov'è il binario di Firefox
            # Se su osboxes il path è diverso, digita 'which firefox' nel terminale per scoprirlo
            options.binary_location = "/usr/bin/firefox"
            
            # Opzionale: Se hai problemi col display
            # options.add_argument("--headless") 

            # FIX CRITICO: Specifichiamo il service per geckodriver
            # Assicurati che geckodriver sia installato o nel path
            # Se non è nel path, specifica executable_path="/path/to/geckodriver" dentro Service()
            service = FirefoxService() 
            
            driver = webdriver.Firefox(options=options, service=service)

        # --- CONFIGURAZIONE WINDOWS (Edge) ---
        else:
            options = EdgeOptions()
            options.use_chromium = True
            # Ingrandisci finestra per vedere bene il PDF
            options.add_argument("--start-maximized")
            
            driver = webdriver.Edge(options=options)

        # --- ESECUZIONE ---
        driver.get(target_url)
        
        # Attesa caricamento PDF (importante!)
        time.sleep(3) 
        
        # Tempo di lettura variabile
        reading_time = random.randint(20, 40)
        scroll_reading_mode_keyboard(driver, reading_time)
        
    except Exception as e:
        print(f"[ERROR] Errore driver: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("[PDF] Chiusura browser.")
            driver.quit()

if __name__ == "__main__":
    main()
