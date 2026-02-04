https://download.sysinternals.com/files/Sysmon.zip

slmgr /rearm

sudo apt update && sudo apt install auditd audispd-plugins

sudo service auditd restart

sudo auditctl -l





logman create trace MyKernelTrace -o C:\KernelLog.etl -pf "C:\percorso\al\tuo\providers.txt" -ets


logman stop MyKernelTrace -ets


logman query MyKernelTrace -ets

Get-WinEvent -Path "C:\KernelLog.etl" -Oldest




sed -i 's/\r//' /etc/audit/rules.d/99-thesis.rules
