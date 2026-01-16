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




