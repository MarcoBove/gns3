@echo off
set "CMD_FILE=C:\Users\Secretary\user_behavior_generation\worker\current_cmd.txt"
set "WORKER_DIR=C:\Users\Secretary\user_behavior_generation\worker"

:: --- FASE 1: RICEZIONE DA ANSIBLE ---
if NOT "%~1"=="" goto :MODE_RECEIVE
goto :MODE_EXECUTE

:MODE_RECEIVE
:: %1 = TARGET (File o Url), %2 = ACTION
set "INPUT_TARGET=%~1"
set "ACTION=%~2"

if "%ACTION%"=="" set ACTION=generic

:: NOTA: Ho tolto lo spazio prima di > per evitare spazi fantasma alla fine della riga
echo %ACTION% %INPUT_TARGET%> "%CMD_FILE%"
schtasks /run /tn OpenBrowser
exit /b 0

:MODE_EXECUTE
:: --- FASE 2: ESECUZIONE VISIBILE ---
set /p MY_CMD=<"%CMD_FILE%"

:: CORREZIONE CRITICA:
:: 1. Usa "tokens=1*" invece di "1,2". Se il nome file ha spazi, "1*" prende tutto il resto della riga.
:: 2. Usa le virgolette nel SET: set "TARGET=%%b". Questo protegge le URL che contengono "&".
for /f "tokens=1* delims= " %%a in ("%MY_CMD%") do (
    set "TYPE=%%a"
    set "TARGET=%%b"
)

cd /d "%WORKER_DIR%"

:: --- SELEZIONE AZIONE ---

:: CASO 1: STAMPA
if "%TYPE%"=="print" (
    echo [INFO] Invio stampa...
    .\PDFtoPrinter.exe "%TARGET%"
    timeout /t 15 /nobreak
    taskkill /IM AcroRd32.exe /F /T 2>nul
    taskkill /IM msedge.exe /F /T 2>nul
    goto :EOF
)

:: CASO 2: MAIL
if "%TYPE%"=="mail" (
    start "" msedge.exe --app=https://mail.google.com/mail/u/0/
    goto :EOF
)

:: CASO 3: PDF (Lettura a video)
if "%TYPE%"=="pdf" (
    taskkill /IM msedge.exe /F /T 2>nul
    :: Aggiunte virgolette attorno al TARGET per gestire spazi nei nomi file
    .\venv\Scripts\python.exe pdf_worker.py "%TARGET%"
    goto :EOF
)

:: CASO 4: WEB (Default)
taskkill /IM msedge.exe /F /T 2>nul
:: CORREZIONE: Aggiunte virgolette. Se l'URL ha "&", senza virgolette il comando si rompe qui.
.\venv\Scripts\python.exe smart_worker.py "%TARGET%" "%TYPE%"

:EOF
exit /b 0
