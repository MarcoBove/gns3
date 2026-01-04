import sys
import time
import random
import os

# Import Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Gestori Driver automatici (scaricano il driver giusto da soli)
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
                # ATTENZIONE: Assicurati che il percorso sia corretto!
                local_driver_path = r"C:\Users\Student\user_behavior_generation\worker\msedgedriver.exe"
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

def human_scroll(driver):
    """Simula lo scroll umano (preso dall'idea di DAPT)"""
    try:
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        # Scrolla a passi casuali
        for i in range(1, total_height, random.randint(300, 700)):
            driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(random.uniform(0.2, 0.8))
    except:
        pass

def crawl_recursive(driver, depth=2):
    """
    Simula il WebpageSpider di DAPT ma usando Selenium (Visivo).
    Cerca un link nella pagina e lo clicca.
    """
    if depth <= 0: return

    print(f"[CRAWL] Cerco link... Depth: {depth}")
    try:
        # Trova tutti i link <a> che hanno un href valido
        links = driver.find_elements(By.TAG_NAME, "a")
        valid_links = [l for l in links if l.get_attribute('href') and "http" in l.get_attribute('href')]
        
        if len(valid_links) > 0:
            target = random.choice(valid_links)
            url = target.get_attribute('href')
            print(f"[CRAWL] Clicco su: {url}")
            driver.get(url)
            time.sleep(3)
            human_scroll(driver)
            # Ricorsione: cerca un altro link nella nuova pagina
            crawl_recursive(driver, depth - 1)
    except Exception as e:
        print(f"[WARN] Crawling interrotto: {e}")

def watch_video(driver, duration):
    """Logica simile a browseVideo di DAPT"""
    print(f"[VIDEO] Guardo video per {duration} secondi...")
    try:
        # Tenta di cliccare Play se c'è un bottone ovvio (euristica)
        play_buttons = driver.find_elements(By.CLASS_NAME, "ytp-play-button")
        if play_buttons:
            play_buttons[0].click()
    except:
        pass
    
    time.sleep(duration)

# --- MAIN ---
if __name__ == "__main__":
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
            print(f"[OPEN] {url}")
            driver.get(url)
            time.sleep(3) # Attesa caricamento
            
            if "youtube" in url or mode == "video":
                watch_time = random.randint(10, 60)
                watch_video(driver, watch_time)
            
            else:
                # Modalità Navigazione (News, Amazon, Blog)
                human_scroll(driver)
                # Prova a cliccare su 2 link successivi (Crawling)
                crawl_recursive(driver, depth=2)
                
            print("[DONE] Sessione finita.")
            
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            driver.quit()
