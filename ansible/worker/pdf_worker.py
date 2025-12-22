import sys
import time
import random
import pathlib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# Importa le opzioni corrette a seconda di cosa usi (Firefox o Chrome/Edge)
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

def scroll_reading_mode(driver, duration):
    """
    Simula la lettura di un documento: scroll lento e pause.
    """
    end_time = time.time() + duration
    current_scroll = 0
    
    print("[PDF] Inizio lettura...")
    while time.time() < end_time:
        # Scrolla di una piccola quantità (tra 20 e 100 pixel)
        scroll_step = random.randint(20, 100)
        driver.execute_script(f"window.scrollBy(0, {scroll_step});")
        current_scroll += scroll_step
        
        # Pausa per "leggere" (tra 1 e 4 secondi)
        time.sleep(random.uniform(1.0, 4.0))
        
        # Ogni tanto torna su un pochino (rilegge)
        if random.random() < 0.1:
            driver.execute_script("window.scrollBy(0, -50);")
            time.sleep(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_worker.py <local_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    
    # Conversione da Path Locale a URL (es. /home/user/a.pdf -> file:///home/user/a.pdf)
    # Fondamentale per far capire al browser che è un file locale
    target_url = pathlib.Path(file_path).as_uri()

    print(f"[PDF] Apertura file: {target_url}")

    # --- SETUP DRIVER (Adatta se usi Chrome/Firefox/Edge) ---
    # ESEMPIO FIREFOX (Linux)
    if "linux" in sys.platform:
        options = FirefoxOptions()
        # options.add_argument("--headless") # Togli commento se vuoi headless
        driver = webdriver.Firefox(options=options)
    else:
        # ESEMPIO EDGE (Windows)
        options = EdgeOptions()
        options.use_chromium = True
        # Qui potresti dover puntare al driver se non è nel PATH
        driver = webdriver.Edge(options=options)

    try:
        driver.get(target_url)
        time.sleep(2) # Attesa caricamento PDF
        
        # Simula lettura per un tempo variabile (es. 30-60 secondi)
        reading_time = random.randint(30, 60)
        scroll_reading_mode(driver, reading_time)
        
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        print("[PDF] Chiusura browser.")
        driver.quit()

if __name__ == "__main__":
    main()
