/tmp/web_openssl.cnf

[req]
default_bits        = 2048
prompt              = no
default_md          = sha256
distinguished_name  = dn
req_extensions      = v3_req

[dn]
C=IT
ST=Campania
L=Salerno
O=Portal
OU=LAB
CN=uni.local

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = uni.local
DNS.2 = uni
IP.1  = 10.0.2.10
IP.2  = 203.0.213.3

Genera key + CSR (la key viene creata da questo comando; se esiste la sovrascrive — fai backup se serve):

```bash
sudo openssl req -new -nodes -newkey rsa:2048 \
  -keyout /etc/ssl/private/webserver.key \
  -out /tmp/webserver.csr \
  -config /tmp/web_openssl.cnf

```

Imposta permessi sicuri sulla chiave:

```bash
sudo chmod 600 /etc/ssl/private/webserver.key
sudo chown root:root /etc/ssl/private/webserver.key

```

Verifica CSR e SAN:

```bash
openssl req -in /tmp/webserver.csr -noout -text | sed -n '1,120p'

openssl req -in /tmp/webserver.csr -noout -text | grep -A2 "Subject Alternative Name"

```

---

Poi copia `/tmp/webserver.csr` sul server CA (via SCP, WinSCP, ecc.)

copia dal server la rootca alla debian



Apri **PowerShell** (come amministratore) e digita:

```powershell
certreq -submit -attrib "CertificateTemplate:WebServer" C:\temp\webserver.csr C:\temp\webserver.cer

```


### Portare certificato sul Debian e convertire/creare fullchain

Copia `web_lab_local.cer` e `rootCA.cer` sul Debian (es. nella home via scp).

Converti/rinomina in `.crt` (se sono in PEM base64, basta rinominare; ma facciamo una conversione sicura):

```bash
# se sono già in Base-64 PEM:
sudo cp /home/you/web_lab_local.cer /etc/ssl/certs/webserver.crt
sudo cp /home/you/rootCA.cer /etc/ssl/certs/rootCA.crt

# in alternativa converti da DER a PEM (solo se file binario):
# sudo openssl x509 -inform DER -in web_lab_local.cer -out /etc/ssl/certs/webserver.crt

```

Crea il fullchain (server cert seguito dalla CA radice):

```bash
sudo sh -c 'cat /etc/ssl/certs/webserver.crt /etc/ssl/certs/rootCA.crt > /etc/ssl/certs/web_fullchain.crt'
sudo chmod 644 /etc/ssl/certs/web_fullchain.crt

```

Verifica il certificato e SAN:

```bash
openssl x509 -in /etc/ssl/certs/webserver.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/webserver.crt -noout -text | grep -A4 "Subject Alternative Name"

```

---

Esegui solo:

```bash
sudo cp /etc/ssl/certs/rootCA.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

```

E **non** installare la fullchain o il certificato del webserver nel trust store.

