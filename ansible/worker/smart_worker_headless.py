import sys
import time
import random
import os

# Import Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException

# Gestori Driver automatici
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

def setup_driver(browser_type="edge"):
    """
    Inizializza il browser. 
    - Windows (Edge): Visibile e Massimizzato.
    - Linux (Firefox): Headless (invisibile) e risoluzione forzata.
    """
    driver = None
    try:
        # --- WINDOWS (EDGE) ---
        if browser_type == "edge":
            options = webdriver.EdgeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--headless") # Scommenta se vuoi nasconderlo su Windows
            options.add_argument("--window-size=1920,1080")
            
            try:
                service = EdgeService(EdgeChromiumDriverManager().install())
            except Exception as e:
                print(f"[WARN] Driver online fallito. Uso locale. {e}")
                local_driver_path = r"C:\Users\Student\user_behavior_generation\worker\msedgedriver.exe"
                service = EdgeService(local_driver_path)

            driver = webdriver.Edge(service=service, options=options)
        
        # --- LINUX (FIREFOX) ---
        elif browser_type == "firefox":
            options = webdriver.FirefoxOptions()
            
            # --- HEADLESS (Fondamentale per VM Linux) ---
            options.add_argument("--headless") 
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            # --------------------------------------------

            user = os.environ.get('USER', 'student')
            os.environ["TMPDIR"] = f"/home/{user}/tmp_firefox"
            
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            
        elif browser_type == "chrome":
             options = webdriver.ChromeOptions()
             options.add_argument("--start-maximized")
             driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        # --- CONFIGURAZIONE TIMEOUT (SALVA VITA) ---
        if driver:
            # Se la pagina non carica entro 30 secondi, lancia errore (che gestiremo)
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(30)
            
        return driver
    except Exception as e:
        print(f"[ERROR] Driver init failed: {e}")
        return None

def human_scroll(driver):
    """Simula lo scroll umano per leggere la pagina."""
    try:
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        # Fai tra 3 e 8 scrollate
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
    Naviga (Scroll + Click) finché non scade il tempo 'duration'.
    Gestisce i blocchi di caricamento pagina (Timeout).
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
            # Filtro per link validi (http e lunghezza decente)
            # Recupera il dominio base (es. "wikipedia.org")
            current_domain = driver.current_url.split("/")[2]

            # Filtra: tieni solo i link che contengono lo stesso dominio
            valid_links = [
                l for l in links 
                if l.get_attribute('href') 
                and "http" in l.get_attribute('href') 
                and len(l.get_attribute('href')) > 10
                and current_domain in l.get_attribute('href') # <--- QUESTA È LA PROTEZIONE
            ]
            
            if len(valid_links) > 0:
                target = random.choice(valid_links)
                url_next = target.get_attribute('href')
                print(f"[CLICK] Vado su: {url_next}")
                
                # --- BLOCCO DI SICUREZZA PER CARICAMENTO ---
                try:
                    driver.get(url_next)
                except TimeoutException:
                    print("[WARN] Pagina troppo lenta! Interrompo caricamento e proseguo.")
                    driver.execute_script("window.stop();") # Ferma la rotellina
                except Exception as e:
                    print(f"[WARN] Errore caricamento link: {e}")
                # -------------------------------------------

                time.sleep(3) # Piccola attesa post-caricamento
            else:
                print("[NAV] Nessun link valido trovato. Torno indietro.")
                driver.back()
                time.sleep(2)
        except Exception as e:
            print(f"[WARN] Errore navigazione generico: {e}. Passo oltre.")
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
    # Se None, usa random tra 240s (4min) e 300s (5min)
    OVERRIDE_DURATION = None 
    
    if OVERRIDE_DURATION is not None:
        duration = OVERRIDE_DURATION
    else:
        duration = random.randint(240, 300)
    # ----------------------------

    # Argomenti: 1=URL, 2=TIPO (video, generic)
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
            print(f"[OPEN] {url} - Durata: {duration}s - Browser: {browser}")
            
            # Primo caricamento con gestione timeout
            try:
                driver.get(url)
            except TimeoutException:
                print("[WARN] Il sito iniziale è lento, fermo il caricamento e inizio a navigare.")
                driver.execute_script("window.stop();")
            
            time.sleep(3)
            
            if "youtube" in url or mode == "video":
                watch_video(driver, duration)
            else:
                browse_continuously(driver, duration)
                
            print("[DONE] Tempo scaduto. Sessione finita.")
            
        except Exception as e:
            print(f"[ERROR] Main execution error: {e}")
        finally:
            print("[CLOSE] Chiusura driver.")
            driver.quit()
