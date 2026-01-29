import struct
import binascii
import random
import time
import socket
import argparse
import sys

# Importazioni librerie esterne
try:
    import dns.resolver 
    from Crypto.Hash import SHA3_256 
    from Crypto.Cipher import Salsa20
    from ecdsa import SECP256k1, SigningKey, ECDH 
except ImportError as e:
    print(f"[!] Errore: Manca una libreria necessaria. Dettagli: {e}")
    print("[*] Esegui: pip install dnspython pycryptodome ecdsa")
    sys.exit(1)

# --- Funzioni di Utilità (Helpers) ---

def to_hex(data):
    if isinstance(data, str):
        data = data.encode()
    return binascii.hexlify(data).decode()

def from_hex(hex_str):
    return binascii.unhexlify(hex_str)

def get_sha3(data):
    h_obj = SHA3_256.new()
    h_obj.update(data)
    return h_obj.digest()

def get_random_hex(length):
    chars = "0123456789ABCDEF"
    return "".join(random.choice(chars) for _ in range(length))

def add_dns_dots(data):
    packet = ""
    section_count = 0
    for char in data:
        if section_count >= 63:
            packet += "."
            section_count = 0
        packet += char
        section_count += 1
    return packet.rstrip(".")

class Dnscat2Client:
    def __init__(self, domain, dns_server, secret="", dns_port=53):
        self.domain = domain
        self.dns_server = dns_server
        self.dns_port = dns_port
        self.psk = secret.encode() if secret else b""
        self.session_id = get_random_hex(4) 
        self.encryption_keys = {}
        self.sequence_number = random.randint(0, 65535)
        
        # Generazione Chiavi ECDH (P-256) per eventuale cifratura futura
        self.client_sk = SigningKey.generate(curve=SECP256k1)
        self.client_vk = self.client_sk.verifying_key

    def send_dns_query(self, hex_data, record_type="TXT"):
        dns_ready_data = add_dns_dots(hex_data)
        full_query = f"{dns_ready_data}.{self.domain}"
        
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [self.dns_server]
        resolver.port = self.dns_port
        
        try:
            print(f"[*] Invio Query TXT a {self.dns_server}: {full_query[:50]}...") 
            answers = resolver.resolve(full_query, record_type)
            
            if record_type == "TXT":
                for rdata in answers:
                    # Gestione differenze versione dnspython
                    if hasattr(rdata, 'strings'):
                        txt_resp = b"".join(rdata.strings).decode()
                    else:
                        txt_resp = rdata.to_text().strip('"')
                    return txt_resp
            return None
            
        except Exception as e:
            print(f"[!] Errore DNS: {e}")
            return None

    def create_syn_packet(self):
        # Header: Random(4) + Type(00) + SessionID(4) + Seq(4) + Options(4)
        rand_id = get_random_hex(4)
        msg_type = "00" # SYN
        seq_num = f"{self.sequence_number:04x}"
        options = "0000" 
        return f"{rand_id}{msg_type}{self.session_id}{seq_num}{options}"

    def parse_packet(self, hex_response):
        """Analizza la risposta del server"""
        try:
            # Struttura Packet dnscat2: [ID 2 byte][Type 1 byte][SessionID 2 byte]...
            # Nota: I byte sono rappresentati da 2 caratteri hex ciascuno.
            
            if len(hex_response) < 6:
                return "Risposta troppo corta"

            packet_type = hex_response[4:6] # Il 3° byte è il tipo
            
            if packet_type == "02": # Type 02 = FIN (Chiusura/Errore)
                payload_hex = hex_response[18:] 
                try:
                    error_msg = binascii.unhexlify(payload_hex).decode('utf-8', errors='ignore')
                    return f"ERRORE DAL SERVER (FIN): {error_msg}"
                except:
                    return "ERRORE DAL SERVER (FIN) - Impossibile decodificare il messaggio"
            
            elif packet_type == "01": # Type 01 = MSG (Dati)
                return "DATI RICEVUTI (Connessione Attiva)"
            
            elif packet_type == "00": # Type 00 = SYN (Handshake)
                return "HANDSHAKE RICEVUTO - Connessione Stabilita!"
                
            return f"Pacchetto Tipo {packet_type} sconosciuto"
            
        except Exception as e:
            return f"Errore parsing risposta: {e}"

    def start_session(self):
        print(f"\n--- AVVIO CLIENT DNSCAT2 (Simulazione Traffico) ---")
        print(f"[*] Dominio: {self.domain}")
        print(f"[*] Server: {self.dns_server}")
        print(f"[*] Modalità: Plaintext (Assicurati che il server abbia --security=open)")
        
        # 1. Creazione pacchetto SYN
        syn_packet = self.create_syn_packet()
        
        # 2. Invio
        response = self.send_dns_query(syn_packet, "TXT")
        
        if response:
            print(f"[+] Risposta Raw: {response}")
            msg = self.parse_packet(response)
            print(f"[!] STATO: {msg}")
            
            if "ERRORE" in msg:
                print("\n[SUGGERIMENTO] Il server ha rifiutato la connessione.")
                print("Esegui sul server Kali: ruby dnscat2.rb --security=open")
        else:
            print("[-] Nessuna risposta (Packet Loss o Server Offline).")

# --- MAIN ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client Dnscat2 Python per Tesi')
    parser.add_argument('--domain', required=True, help='Il dominio malevolo (es. test.com)')
    parser.add_argument('--dns', required=True, help='IP del server DNS/Gateway (es. 10.0.40.1)')
    parser.add_argument('--secret', default="", help='Non usato in modalità open')
    parser.add_argument('--port', type=int, default=53, help='Porta DNS (Default: 53)')

    args = parser.parse_args()

    client = Dnscat2Client(args.domain, args.dns, args.secret, args.port)
    client.start_session()
