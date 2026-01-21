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
from webdriver_manager.firefox import GeckoDriverManager

# Import per Edge (Windows)
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService

def scroll_reading_mode_keyboard(driver, duration):
    """Simula la lettura usando la TASTIERA."""
    end_time = time.time() + duration
    print(f"[PDF] Inizio lettura simulata per {duration} secondi...")
    
    actions = ActionChains(driver)
    
    # Clicchiamo sulla pagina per il focus
    try:
        driver.find_element(By.TAG_NAME, "body").click()
    except:
        pass 

    while time.time() < end_time:
        scroll_steps = random.randint(3, 10) 
        for _ in range(scroll_steps):
            try:
                actions.send_keys(Keys.ARROW_DOWN).perform()
            except:
                pass
            time.sleep(random.uniform(0.05, 0.2)) 
        
        time.sleep(random.uniform(1.0, 3.0))
        
        if time.time() >= end_time:
            break

        if random.random() < 0.1:
            try:
                actions.send_keys(Keys.PAGE_UP).perform()
            except:
                pass
            time.sleep(1.5)

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_worker.py <local_file_path> [duration]")
        sys.exit(1)

    file_path = sys.argv[1]
    
    # Gestione Durata
    if len(sys.argv) > 2:
        try:
            reading_time = int(sys.argv[2])
        except ValueError:
            reading_time = random.randint(240, 300)
    else:
        reading_time = random.randint(240, 300)

    if not os.path.exists(file_path):
        print(f"[ERROR] File non trovato: {file_path}")
        sys.exit(1)

    target_url = pathlib.Path(file_path).absolute().as_uri()
    print(f"[PDF] Apro: {target_url} - Durata: {reading_time}s")

    driver = None

    try:
        # --- CONFIGURAZIONE LINUX (Firefox Headless) ---
        if "linux" in sys.platform:
            options = FirefoxOptions()
            options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")

            user = os.environ.get('USER', 'student')
            os.environ["TMPDIR"] = f"/home/{user}/tmp_firefox"
            
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)

        # --- CONFIGURAZIONE WINDOWS (Edge Ottimizzato) ---
        else:
            options = EdgeOptions()
            options.use_chromium = True
            options.add_argument("--start-maximized")
            options.add_argument("--headless") # Scommenta se vuoi nasconderlo su Windows
            options.add_argument("--window-size=1920,1080")
            
            # --- CURA PER GLI ERRORI ROSSI ---
            options.add_argument("--disable-gpu")  # Disabilita GPU (rimuove err GpuInfo)
            options.add_argument("--log-level=3")  # Nasconde i log di sistema inutili
            options.add_argument("--disable-features=msEdgeLLM") # Disabilita AI Edge
            # ---------------------------------
            
            driver = webdriver.Edge(options=options)

        # --- ESECUZIONE ---
        driver.get(target_url)
        time.sleep(3)
        
        scroll_reading_mode_keyboard(driver, reading_time)
        
    except Exception as e:
        print(f"[ERROR] Errore driver: {e}")
        
    finally:
        if driver:
            print("[PDF] Chiusura browser...")
            try:
                driver.quit()
            except:
                pass
            print("[DONE] Finito.")

if __name__ == "__main__":
    main()
