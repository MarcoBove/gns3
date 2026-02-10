https://download.sysinternals.com/files/Sysmon.zip

slmgr /rearm

sudo apt update && sudo apt install auditd audispd-plugins

sudo service auditd restart

sudo auditctl -l





logman create trace MyKernelTrace -o C:\KernelLog.etl -pf "C:\percorso\al\tuo\providers.txt" -ets


logman stop MyKernelTrace -ets


logman query MyKernelTrace -ets

Get-WinEvent -Path "C:\KernelLog.etl" -Oldest



System Monitor v15.15 - System activity monitor
By Mark Russinovich and Thomas Garnier
Copyright (C) 2014-2024 Microsoft Corporation
Using libxml2. libxml2 is Copyright (C) 1998-2012 Daniel Veillard. All Rights Reserved.
Sysinternals - www.sysinternals.com

./sysmonconfig.xml:16: parser error : Comment must not contain '--' (double-hyphen)
  -- Process creation (Event ID 1): Uses sysmon-modular rules to log process exe
    ^
./sysmonconfig.xml:18: parser error : Comment must not contain '--' (double-hyphen)
  -- Network connections (Event ID 3): Logs all initiated outbound connections,
    ^
./sysmonconfig.xml:20: parser error : Comment must not contain '--' (double-hyphen)
  -- DNS queries (Event ID 22): Logs all DNS queries.
    ^
./sysmonconfig.xml:21: parser error : Comment must not contain '--' (double-hyphen)
  -- Image loads / DLL loads (Event ID 7): Uses sysmon-modular include/exclude l
    ^
./sysmonconfig.xml:23: parser error : Comment must not contain '--' (double-hyphen)
  -- Process access (Event ID 10): Uses sysmon-modular logic to detect suspiciou
    ^
./sysmonconfig.xml:24: parser error : Comment must not contain '--' (double-hyphen)
  -- Registry events (Event ID 12/13/14): Uses sysmon-modular rules focused on p
    ^
./sysmonconfig.xml:25: parser error : Comment must not contain '--' (double-hyphen)
  -- Named pipes (Event ID 17/18): Uses sysmon-modular logic to catch suspicious
    ^
./sysmonconfig.xml:26: parser error : Comment must not contain '--' (double-hyphen)
  -- Workstation-friendly file telemetry: File creation/deletion is scoped to ty
    ^
./sysmonconfig.xml:28: parser error : Comment must not contain '--' (double-hyphen)
  -- Clipboard logging is enabled (Event ID 24): this can capture sensitive user
    ^
Error: Failed to load xml configuration: .\sysmonconfig.xml (could not read file)
Usage:
Install:                 Sysmon64.exe -i [<configfile>]
Update configuration:    Sysmon64.exe -c [<configfile>]
Install event manifest:  Sysmon64.exe -m
Print schema:            Sysmon64.exe -s
Uninstall:               Sysmon64.exe -u [force]
  -c   Update configuration of an installed Sysmon driver or dump the
       current configuration if no other argument is provided. Optionally
       take a configuration file.
  -i   Install service and driver. Optionally take a configuration file.
  -m   Install the event manifest (done on service install as well)).
  -s   Print configuration schema definition of the specified version.
       Specify 'all' to dump all schema versions (default is latest)).
  -u   Uninstall service and driver. Adding force causes uninstall to proceed
       even when some components are not installed.

The service logs events immediately and the driver installs as a boot-start driver to capture activity from early in
the boot that the service will write to the event log when it starts.

On Vista and higher, events are stored in "Applications and Services Logs/Microsoft/Windows/Sysmon/Operational". On
older systems, events are written to the System event log.

Use the '-? config' command for configuration file documentation. More examples are available on the Sysinternals
website.

Specify -accepteula to automatically accept the EULA on installation, otherwise you will be interactively prompted to
accept it.

Neither install nor uninstall requires a reboot.

PS C:\Users\Student\Desktop\Sysmon>
sed -i 's/\r//' /etc/audit/rules.d/99-thesis.rules
