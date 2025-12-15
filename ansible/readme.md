ssh osboxes@10.0.20.10 "export DISPLAY=:0 && firefox https://www.google.com"

ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCWb0bPbP9q0uzwhPeLwYkRPrEGPHt1fI/sPTnEbDXRjDz5R1ub2UKzGiECOjymLAFPHHQc+ASGWHewuA5yFgaVHWY8ploEmMbT5a27dnwP93sWPtRBDWNdXfxBicqRjy3Np0uId626B36YjsrnBgClH+BBmdJIbkypjQxc2lOvLJsEZqGUUkz03/9z+Tqht7MrMgB8GyGuEkvqwIb6BTB916YxRUalfsA2sSvmQylCf97XFlX1Tt7VLmXU0ZvvRwpRpFXU/vbmRIZdwQsLBxF8/WMlhkoYAilAhkfRGff/rVomE5TdBKGzs7Spi8x9U29GOj1/xaLAvmDyJO03AZzw6Ghq7FYHnpgN+afRsC019qr1a2cz2rtADAw8tYFgloX/j9PYcuwYMItk+exvkkJm/iOgCLFOCRuFVpfp1Ytwj7CF+ymiwUFs+CwdB8a9A8T7KZZqRPd2pg5OwXF1gwdaoTd61Wta3gVX+Xac9nCM1JlLWtYvQMxM+0VJHX2yxas= osboxes@osboxes


ssh User@10.0.10.12 "echo https://www.google.com > C:/Users/User/dapt2021/worker/current_url.txt && schtasks /run /tn DaptBrowser"


@echo off
:: Ci assicuriamo di essere nella cartella giusta
cd /d C:\dapt2021\worker

:: Leggiamo l'URL
set /p url=<current_url.txt

:: Stampiamo a video cosa sta succedendo (per debug)
echo ------------------------------------------
echo TENTATIVO DI APERTURA BROWSER
echo URL Letto dal file: %url%
echo ------------------------------------------

:: Lanciamo Python
python browseInternet.py %url%

:: Se c'è un errore, lo vediamo
if %errorlevel% neq 0 (
    echo.
    echo [ERRORE] Python ha restituito il codice: %errorlevel%
)

echo.
echo NON CHIUDERE QUESTA FINESTRA, leggi l'errore sopra.
pause
