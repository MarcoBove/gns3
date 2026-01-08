@echo off
set "CMD_FILE=C:\Users\Secretary\user_behavior_generation\worker\current_cmd.txt"
set "WORKER_DIR=C:\Users\Secretary\user_behavior_generation\worker"

:: --- FASE 1: RICEZIONE DA ANSIBLE ---
if NOT "%~1"=="" goto :MODE_RECEIVE
goto :MODE_EXECUTE

:MODE_RECEIVE
:: %1 = TARGET (File o Url), %2 = ACTION (print, generic, video, pdf, mail)
set TARGET=%~1
set ACTION=%~2

if "%ACTION%"=="" set ACTION=generic

echo %ACTION% %TARGET% > "%CMD_FILE%"
schtasks /run /tn OpenBrowser
exit /b 0

:MODE_EXECUTE
:: --- FASE 2: ESECUZIONE VISIBILE ---
set /p MY_CMD=<"%CMD_FILE%"

for /f "tokens=1,2 delims= " %%a in ("%MY_CMD%") do (
    set TYPE=%%a
    set TARGET=%%b
)

cd /d "%WORKER_DIR%"

:: --- SELEZIONE AZIONE ---

:: CASO 1: STAMPA (Nuovo)
if "%TYPE%"=="print" (
    echo [INFO] Invio stampa di %TARGET% alla stampante predefinita...
    :: Usa PowerShell per stampare senza aprire GUI complicate
    .\PDFtoPrinter.exe %TARGET%
    
    :: Aspettiamo 15 secondi che lo spooler riceva il file
    timeout /t 15 /nobreak
    
    :: Pulizia: Chiudiamo il lettore PDF che potrebbe essere rimasto aperto (Acrobat o Edge)
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
    .\venv\Scripts\python.exe pdf_worker.py %TARGET%
    goto :EOF
)

:: CASO 4: WEB
taskkill /IM msedge.exe /F /T 2>nul
.\venv\Scripts\python.exe smart_worker.py %TARGET% %TYPE%

:EOF
exit /b 0
