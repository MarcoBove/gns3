https://download.sysinternals.com/files/Sysmon.zip

slmgr /rearm

sudo apt update && sudo apt install auditd audispd-plugins

sudo service auditd restart

sudo auditctl -l





logman create trace MyKernelTrace -o C:\KernelLog.etl -p "Microsoft-Windows-Kernel-Process" 0xffffffff 0xff -p "Microsoft-Windows-Kernel-File" 0xffffffff 0xff -p "Microsoft-Windows-Kernel-Network" 0xffffffff 0xff -p "Microsoft-Windows-Kernel-Registry" 0xffffffff 0xff -p "Microsoft-Windows-PowerShell" 0xffffffff 0xff -p "Microsoft-Windows-DNS-Client" 0xffffffff 0xff -p "OpenSSH" 0xffffffff 0xff -ets


logman stop MyKernelTrace -ets


logman query MyKernelTrace -ets

Get-WinEvent -Path "C:\KernelLog.etl" -Oldest
