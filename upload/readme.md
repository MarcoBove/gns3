ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCWb0bPbP9q0uzwhPeLwYkRPrEGPHt1fI/sPTnEbDXRjDz5R1ub2UKzGiECOjymLAFPHHQc+ASGWHewuA5yFgaVHWY8ploEmMbT5a27dnwP93sWPtRBDWNdXfxBicqRjy3Np0uId626B36YjsrnBgClH+BBmdJIbkypjQxc2lOvLJsEZqGUUkz03/9z+Tqht7MrMgB8GyGuEkvqwIb6BTB916YxRUalfsA2sSvmQylCf97XFlX1Tt7VLmXU0ZvvRwpRpFXU/vbmRIZdwQsLBxF8/WMlhkoYAilAhkfRGff/rVomE5TdBKGzs7Spi8x9U29GOj1/xaLAvmDyJO03AZzw6Ghq7FYHnpgN+afRsC019qr1a2cz2rtADAw8tYFgloX/j9PYcuwYMItk+exvkkJm/iOgCLFOCRuFVpfp1Ytwj7CF+ymiwUFs+CwdB8a9A8T7KZZqRPd2pg5OwXF1gwdaoTd61Wta3gVX+Xac9nCM1JlLWtYvQMxM+0VJHX2yxas= osboxes@osboxes


wget https://raw.githubusercontent.com/MarcoBove/gns3/main/upload/dashboard.php




Metodo 1 – PowerShell (consigliato)

Apri PowerShell come Amministratore

Start → cerca PowerShell → tasto destro → Esegui come amministratore

Verifica lo stato di OpenSSH

Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'


Rimuovi forzatamente OpenSSH Server

Remove-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0


(anche se risulta già rimosso, eseguilo comunque)

Riavvia il PC

Reinstalla OpenSSH Server

Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0


Avvia e abilita il servizio

Start-Service sshd
Set-Service -Name sshd -StartupType Automatic


Verifica

Get-Service sshd
