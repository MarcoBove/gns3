import sys
import time
import random
import os

# Import Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Gestori Driver automatici
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

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
                local_driver_path = r"C:\Users\Student\user_behavior_generation\worker\msedgedriver.exe"
                service = EdgeService(local_driver_path)

            driver = webdriver.Edge(service=service, options=options)
        
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

def human_scroll(driver):
    """Simula lo scroll umano."""
    try:
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        # Scrolla un po', non necessariamente fino in fondo se la pagina è lunghissima
        # Facciamo max 5 step di scroll per non perdere troppo tempo sullo stesso url
        steps = random.randint(3, 8)
        
        current_pos = 0
        for _ in range(steps):
            scroll_ammount = random.randint(300, 700)
            current_pos += scroll_ammount
            
            if current_pos > total_height:
                break
                
            driver.execute_script(f"window.scrollTo(0, {current_pos});")
            time.sleep(random.uniform(0.5, 1.5))
    except:
        pass

def browse_continuously(driver, duration):
    """
    Sostituisce crawl_recursive.
    Naviga (Scroll + Click) finché non scade il tempo 'duration'.
    """
    start_time = time.time()
    print(f"[BROWSE] Inizio navigazione continua per {duration} secondi...")

    while (time.time() - start_time) < duration:
        
        # 1. Scrolla la pagina corrente (lettura)
        human_scroll(driver)
        
        # Controllo tempo post-scroll
        if (time.time() - start_time) >= duration:
            break

        # 2. Cerca un link per cambiare pagina
        try:
            links = driver.find_elements(By.TAG_NAME, "a")
            # Filtro base per trovare link "veri"
            valid_links = [l for l in links if l.get_attribute('href') and "http" in l.get_attribute('href') and len(l.get_attribute('href')) > 10]
            
            if len(valid_links) > 0:
                target = random.choice(valid_links)
                url_next = target.get_attribute('href')
                print(f"[CLICK] Vado su: {url_next}")
                driver.get(url_next)
                time.sleep(3) # Attesa caricamento
            else:
                print("[NAV] Nessun link valido trovato. Torno indietro.")
                driver.back()
                time.sleep(2)
        except Exception as e:
            print(f"[WARN] Errore navigazione: {e}. Ricarico o passo oltre.")
            time.sleep(2)

def watch_video(driver, duration):
    """Guarda il video per tutta la durata assegnata."""
    print(f"[VIDEO] Guardo video per {duration} secondi...")
    try:
        play_buttons = driver.find_elements(By.CLASS_NAME, "ytp-play-button")
        if play_buttons:
            play_buttons[0].click()
    except:
        pass
    
    # Dorme per la durata richiesta
    time.sleep(duration)

# --- MAIN ---
if __name__ == "__main__":
    
    # --- CONFIGURAZIONE TEMPO ---
    # Se vuoi testare a mano, metti un numero qui (es. 60). 
    # Se lasci None, sceglie random tra 5 e 7 minuti (300-420s).
    OVERRIDE_DURATION = None 
    
    if OVERRIDE_DURATION is not None:
        duration = OVERRIDE_DURATION
    else:
        duration = random.randint(300, 420)
    # ----------------------------

    # Argomenti: 1=URL, 2=TIPO (video, news, shop)
    if len(sys.argv) < 2:
        print("Usage: smart_worker.py <URL> [TYPE]")
        sys.exit(1)

    url = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "generic"
    
    # Scegli browser in base all'OS
    browser = "edge" if os.name == 'nt' else "firefox"
    
    driver = setup_driver(browser)
    
    if driver:
        try:
            print(f"[OPEN] {url} - Durata prevista: {duration}s")
            driver.get(url)
            time.sleep(3) # Attesa caricamento
            
            if "youtube" in url or mode == "video":
                watch_video(driver, duration)
            else:
                # Modalità Navigazione a tempo (NON più ricorsiva)
                browse_continuously(driver, duration)
                
            print("[DONE] Tempo scaduto. Sessione finita.")
            
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            driver.quit()
