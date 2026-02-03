# Linux Audit Daemon - Log collection Rules

# Author: sranieri@unisa.it
# Based on rules published here: https://github.com/linux-audit/audit-userspace/tree/master/rules
# Commit: 8ed522a

# Creation date: 03/02/2026

# ----------- Syscall rules -----------

## Make the loginuid immutable. This prevents tampering with the auid.
--loginuid-immutable

## If you are on a 64 bit platform, everything _should_ be running
## in 64 bit mode. This rule will detect any use of the 32 bit syscalls
## because this might be a sign of someone exploiting a hole in the 32
## bit ABI.
-a always,exit -F arch=b32 -S all -F key=32bit-abi

## Successful file creation (open with O_CREAT)
# -a always,exit -F arch=b32 -S openat,open_by_handle_at -F a2&0100 -F success=1 -F auid>=1000 -F auid!=unset -F key=successful-create
# -a always,exit -F arch=b64 -S openat,open_by_handle_at -F a2&0100 -F success=1 -F auid>=1000 -F auid!=unset -F key=successful-create
# -a always,exit -F arch=b32 -S open -F a1&0100 -F success=1 -F auid>=1000 -F auid!=unset -F key=successful-create
# -a always,exit -F arch=b64 -S open -F a1&0100 -F success=1 -F auid>=1000 -F auid!=unset -F key=successful-create
# -a always,exit -F arch=b32 -S creat -F success=1 -F auid>=1000 -F auid!=unset -F key=successful-create
# -a always,exit -F arch=b64 -S creat -F success=1 -F auid>=1000 -F auid!=unset -F key=successful-create

## Unsuccessful file creation (open with O_CREAT)
# -a always,exit -F arch=b32 -S openat,open_by_handle_at -F a2&0100 -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-create
# -a always,exit -F arch=b64 -S openat,open_by_handle_at -F a2&0100 -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-create
# -a always,exit -F arch=b32 -S open -F a1&0100 -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-create
# -a always,exit -F arch=b64 -S open -F a1&0100 -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-create
# -a always,exit -F arch=b32 -S creat -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-create
# -a always,exit -F arch=b64 -S creat -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-create
# -a always,exit -F arch=b32 -S openat,open_by_handle_at -F a2&0100 -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-create
# -a always,exit -F arch=b64 -S openat,open_by_handle_at -F a2&0100 -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-create
# -a always,exit -F arch=b32 -S open -F a1&0100 -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-create
# -a always,exit -F arch=b64 -S open -F a1&0100 -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-create
# -a always,exit -F arch=b32 -S creat -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-create
# -a always,exit -F arch=b64 -S creat -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-create

## Unsuccessful file modifications (open for write or truncate)
# -a always,exit -F arch=b32 -S openat,open_by_handle_at -F a2&01003 -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification
# -a always,exit -F arch=b64 -S openat,open_by_handle_at -F a2&01003 -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification
# -a always,exit -F arch=b32 -S open -F a1&01003 -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification
# -a always,exit -F arch=b64 -S open -F a1&01003 -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification
# -a always,exit -F arch=b32 -S truncate,ftruncate -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification
# -a always,exit -F arch=b64 -S truncate,ftruncate -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification
# -a always,exit -F arch=b32 -S openat,open_by_handle_at -F a2&01003 -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification
# -a always,exit -F arch=b64 -S openat,open_by_handle_at -F a2&01003 -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification
# -a always,exit -F arch=b32 -S open -F a1&01003 -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification
# -a always,exit -F arch=b64 -S open -F a1&01003 -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification
# -a always,exit -F arch=b32 -S truncate,ftruncate -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification
# -a always,exit -F arch=b64 -S truncate,ftruncate -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-modification

## Unsuccessful file access (any other opens) This has to go last.
-a always,exit -F arch=b32 -S open,openat,openat2,open_by_handle_at -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-access
-a always,exit -F arch=b64 -S open,openat,openat2,open_by_handle_at -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-access
-a always,exit -F arch=b32 -S open,openat,openat2,open_by_handle_at -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-access
-a always,exit -F arch=b64 -S open,openat,openat2,open_by_handle_at -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-access

## Unsuccessful permission change
-a always,exit -F arch=b32 -S chmod,fchmod,fchmodat,setxattr,lsetxattr,fsetxattr,removexattr,lremovexattr,fremovexattr,fchmodat2,setxattrat,removexattrat,file_setattr -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-perm-change
-a always,exit -F arch=b64 -S chmod,fchmod,fchmodat,setxattr,lsetxattr,fsetxattr,removexattr,lremovexattr,fremovexattr,fchmodat2,setxattrat,removexattrat,file_setattr -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-perm-change
-a always,exit -F arch=b32 -S chmod,fchmod,fchmodat,setxattr,lsetxattr,fsetxattr,removexattr,lremovexattr,fremovexattr,fchmodat2,setxattrat,removexattrat,file_setattr -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-perm-change
-a always,exit -F arch=b64 -S chmod,fchmod,fchmodat,setxattr,lsetxattr,fsetxattr,removexattr,lremovexattr,fremovexattr,fchmodat2,setxattrat,removexattrat,file_setattr -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-perm-change

## Successful permission change
-a always,exit -F arch=b32 -S chmod,fchmod,fchmodat,setxattr,lsetxattr,fsetxattr,removexattr,lremovexattr,fremovexattr,fchmodat2,setxattrat,removexattrat,file_setattr -F success=1 -F auid>=1000 -F auid!=unset -F key=successful-perm-change
-a always,exit -F arch=b64 -S chmod,fchmod,fchmodat,setxattr,lsetxattr,fsetxattr,removexattr,lremovexattr,fremovexattr,fchmodat2,setxattrat,removexattrat,file_setattr -F success=1 -F auid>=1000 -F auid!=unset -F key=successful-perm-change

## Unsuccessful ownership change
-a always,exit -F arch=b32 -S lchown,fchown,chown,fchownat,file_setattr -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-owner-change
-a always,exit -F arch=b64 -S lchown,fchown,chown,fchownat,file_setattr -F exit=-EACCES -F auid>=1000 -F auid!=unset -F key=unsuccessful-owner-change
-a always,exit -F arch=b32 -S lchown,fchown,chown,fchownat,file_setattr -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-owner-change
-a always,exit -F arch=b64 -S lchown,fchown,chown,fchownat,file_setattr -F exit=-EPERM -F auid>=1000 -F auid!=unset -F key=unsuccessful-owner-change

## Successful ownership change
-a always,exit -F arch=b32 -S lchown,fchown,chown,fchownat,file_setattr -F success=1 -F auid>=1000 -F auid!=unset -F key=successful-owner-change
-a always,exit -F arch=b64 -S lchown,fchown,chown,fchownat,file_setattr -F success=1 -F auid>=1000 -F auid!=unset -F key=successful-owner-change


## Privilege escalation via su or sudo. This is entirely handled by pam.
## Special case for systemd-run. It is not audit aware, specifically watch it
-a always,exit -F arch=b32 -F path=/usr/bin/systemd-run -F perm=x -F auid!=unset -F key=maybe-escalation
-a always,exit -F arch=b64 -F path=/usr/bin/systemd-run -F perm=x -F auid!=unset -F key=maybe-escalation
## Special case for pkexec. It is not audit aware, specifically watch it
-a always,exit -F arch=b32 -F path=/usr/bin/pkexec -F perm=x -F key=maybe-escalation
-a always,exit -F arch=b64 -F path=/usr/bin/pkexec -F perm=x -F key=maybe-escalation

## Watch for configuration changes to privilege escalation.
-a always,exit -F arch=b32 -F path=/etc/sudoers -F perm=wa -F key=special-config-changes
-a always,exit -F arch=b64 -F path=/etc/sudoers -F perm=wa -F key=special-config-changes
-a always,exit -F arch=b32 -F dir=/etc/sudoers.d/ -F perm=wa -F key=special-config-changes
-a always,exit -F arch=b64 -F dir=/etc/sudoers.d/ -F perm=wa -F key=special-config-changes

# These rules watch for invocation of things known to install software
-a always,exit -F arch=b32 -F perm=x -F path=/usr/bin/dnf-3 -F key=software-installer
-a always,exit -F arch=b64 -F perm=x -F path=/usr/bin/dnf-3 -F key=software-installer
-a always,exit -F arch=b32 -F perm=x -F path=/usr/bin/yum -F key=software-installer
-a always,exit -F arch=b64 -F perm=x -F path=/usr/bin/yum -F key=software-installer
-a always,exit -F arch=b32 -F perm=x -F path=/usr/bin/pip -F key=software-installer
-a always,exit -F arch=b64 -F perm=x -F path=/usr/bin/pip -F key=software-installer
-a always,exit -F arch=b32 -F perm=x -F path=/usr/bin/npm -F key=software-installer
-a always,exit -F arch=b64 -F perm=x -F path=/usr/bin/npm -F key=software-installer
-a always,exit -F arch=b32 -F perm=x -F path=/usr/bin/cpan -F key=software-installer
-a always,exit -F arch=b64 -F perm=x -F path=/usr/bin/cpan -F key=software-installer
-a always,exit -F arch=b32 -F perm=x -F path=/usr/bin/gem -F key=software-installer
-a always,exit -F arch=b64 -F perm=x -F path=/usr/bin/gem -F key=software-installer
-a always,exit -F arch=b32 -F perm=x -F path=/usr/bin/luarocks -F key=software-installer
-a always,exit -F arch=b64 -F perm=x -F path=/usr/bin/luarocks -F key=software-installer

## This is to check if the system is making or receiving connections
## externally
-a always,exit -F arch=b64 -S accept,connect -F key=external-access

## Anonymous File Creation
### These rules watch the use of memfd_create
### "memfd_create" creates anonymous file and returns a file descriptor to access it
### When combined with "fexecve" can be used to stealthily run binaries in memory without touching disk
-a always,exit -F arch=b64 -S memfd_create -F key=anon_file_create
-a always,exit -F arch=b32 -S memfd_create -F key=anon_file_create

# ----------- Watch rules -----------

## Successful and unsuccessful attempts to read information from the
## audit records 
-w /var/log/audit/ -k audit_log

## Edit to audit configuration that occur while
## the audit collection functions are operating.
-w /etc/audit/        -p wa -k audit_config
-w /etc/libaudit.conf -p wa -k audit_libaudit
-w /etc/audisp/       -p wa -k audit_dispatcher

## Time settings changes
-a exit,always -F arch=b32 -S adjtimex -S settimeofday -S clock_settime -k time
-a exit,always -F arch=b64 -S adjtimex -S settimeofday -S clock_settime -k time


## Cron configuration & scheduled jobs
-w /etc/cron.allow -p wa -k cron
-w /etc/cron.deny -p wa -k cron
-w /etc/cron.d/ -p wa -k cron
-w /etc/cron.daily/ -p wa -k cron
-w /etc/cron.hourly/ -p wa -k cron
-w /etc/cron.monthly/ -p wa -k cron
-w /etc/cron.weekly/ -p wa -k cron
-w /etc/crontab -p wa -k cron
-w /var/spool/cron/crontabs/ -k cron

## User, group, password
-w /etc/group             -p wa -k group_db
-w /etc/passwd            -p wa -k user_db
-w /etc/gshadow           -p wa -k gshadow_db
-w /etc/shadow            -p wa -k shadow_db
-w /etc/security/opasswd  -p wa -k password_history

## Monitor usage of passwd
-w /usr/bin/passwd -p x -k passwd_modification

## Monitor for use of tools to change group identifiers
-w /usr/sbin/groupadd -p x -k group_modification
-w /usr/sbin/groupmod -p x -k group_modification
-w /usr/sbin/addgroup -p x -k group_modification
-w /usr/sbin/useradd -p x -k user_modification
-w /usr/sbin/usermod -p x -k user_modification
-w /usr/sbin/adduser -p x -k user_modification

## Login configuration and information
-w /etc/login.defs -p wa -k login
-w /etc/securetty -p wa -k login
-w /var/log/faillog -p wa -k login
-w /var/log/lastlog -p wa -k login
-w /var/log/tallylog -p wa -k login

## Network configuration
-w /etc/hosts -p wa -k hosts
-w /etc/network/ -p wa -k network

## Process ID change (switching accounts) applications
-w /bin/su -p x -k priv_esc
-w /usr/bin/sudo -p x -k priv_esc
-w /etc/sudoers -p rw -k priv_esc
-w /etc/sudoers.d -p rw -k priv_esc

## Suspicious activity
-w /usr/bin/wget -p x -k susp_activity
-w /usr/bin/curl -p x -k susp_activity
-w /usr/bin/base64 -p x -k susp_activity
-w /bin/nc -p x -k susp_activity
-w /bin/netcat -p x -k susp_activity
-w /usr/bin/ncat -p x -k susp_activity
-w /usr/bin/ss -p x -k susp_activity
-w /usr/bin/netstat -p x -k susp_activity
-w /usr/bin/ssh -p x -k susp_activity
-w /usr/bin/scp -p x -k susp_activity
-w /usr/bin/sftp -p x -k susp_activity
-w /usr/bin/ftp -p x -k susp_activity
-w /usr/bin/socat -p x -k susp_activity
-w /usr/bin/wireshark -p x -k susp_activity
-w /usr/bin/tshark -p x -k susp_activity
-w /usr/bin/rawshark -p x -k susp_activity
-w /usr/bin/rdesktop -p x -k T1219_Remote_Access_Tools
-w /usr/local/bin/rdesktop -p x -k T1219_Remote_Access_Tools
-w /usr/bin/wlfreerdp -p x -k susp_activity
-w /usr/bin/xfreerdp -p x -k T1219_Remote_Access_Tools
-w /usr/local/bin/xfreerdp -p x -k T1219_Remote_Access_Tools
-w /usr/bin/nmap -p x -k susp_activity


## Make the configuration immutable - reboot is required to change audit rules
-e 2