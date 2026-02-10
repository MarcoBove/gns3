https://download.sysinternals.com/files/Sysmon.zip

slmgr /rearm

sudo apt update && sudo apt install auditd audispd-plugins

sudo service auditd restart

sudo auditctl -l





logman create trace MyKernelTrace -o C:\KernelLog.etl -pf "C:\percorso\al\tuo\providers.txt" -ets


logman stop MyKernelTrace -ets


logman query MyKernelTrace -ets

Get-WinEvent -Path "C:\KernelLog.etl" -Oldest


PS C:\Users\Student\Desktop\Sysmon>
sed -i 's/\r//' /etc/audit/rules.d/99-thesis.rules


ls -1 /usr/bin/wget /usr/bin/curl /usr/bin/base64 /bin/nc /bin/netcat /usr/bin/ncat /usr/bin/socat /usr/bin/ssh /usr/bin/scp /usr/bin/sftp /usr/bin/ftp /usr/bin/ss /usr/bin/netstat /usr/bin/wireshark /usr/bin/tshark /usr/bin/rawshark /usr/bin/nmap
