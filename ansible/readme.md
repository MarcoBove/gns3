ssh osboxes@10.0.20.10 "export DISPLAY=:0 && firefox https://www.google.com"

ssh User@10.0.10.12 "echo https://www.google.com > C:/Users/User/dapt2021/worker/current_url.txt && schtasks /run /tn DaptBrowser"

ansible workers_windows -i configs/hosts -m raw -a "cmd /c echo https://www.google.com > C:\Users\User\dapt2021\worker\current_url.txt"

ansible workers_windows -i configs/hosts -m raw -a "schtasks /run /tn DaptBrowser"

@echo off
:: Questo script riceve l'URL come primo parametro (%1)

if "%~1"=="" (
    echo ERRORE: Nessun URL fornito.
    exit /b 1
)

:: 1. Scrive l'URL nel file (senza virgolette extra)
echo %~1 > C:\Users\User\dapt2021\worker\current_url.txt

:: 2. Lancia il Task Scheduler
schtasks /run /tn DaptBrowser



C:\Users\User\dapt2021\worker\run_task.bat https://www.repubblica.it

ansible workers_windows -i configs/hosts -m raw -a "C:\Users\User\dapt2021\worker\run_task.bat https://www.google.com"
