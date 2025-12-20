@echo off
set "CMD_FILE=C:\Users\Student\user_behavior_generation\worker\current_cmd.txt"
set "WORKER_DIR=C:\Users\Student\user_behavior_generation\worker"

:: --- FASE 1: RICEZIONE DA ANSIBLE ---
:: Se c'è almeno il primo argomento (URL), siamo in modalità scrittura
if NOT "%~1"=="" goto :MODE_RECEIVE

:: Se non ci sono argomenti, siamo stati chiamati dal Task Scheduler
goto :MODE_EXECUTE

:MODE_RECEIVE
:: Ansible ci passa: %1 = URL, %2 = ACTION
set URL=%~1
set ACTION=%~2

:: Se l'azione è vuota, mettiamo default 'generic'
if "%ACTION%"=="" set ACTION=generic

:: Scriviamo nel file: ACTION spazio URL (es: "video https://youtube.com")
echo %ACTION% %URL% > "%CMD_FILE%"

:: Diciamo al Task Scheduler di partire
schtasks /run /tn OpenBrowser
exit /b 0

:MODE_EXECUTE
:: --- FASE 2: ESECUZIONE VISIBILE ---
:: Leggiamo il file creato prima
set /p MY_CMD=<"%CMD_FILE%"

:: Parsiamo la stringa (Token 1=Action, Token 2=URL)
for /f "tokens=1,2 delims= " %%a in ("%MY_CMD%") do (
    set TYPE=%%a
    set TARGET=%%b
)

:: Pulizia processi vecchi
taskkill /IM msedge.exe /F /T 2>nul
taskkill /IM python.exe /F /T 2>nul

:: Esecuzione Script Python
cd /d "%WORKER_DIR%"
.\venv\Scripts\python.exe smart_worker.py %TARGET% %TYPE%

exit /b 0
