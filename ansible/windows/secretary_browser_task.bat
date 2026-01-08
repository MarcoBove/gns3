@echo off
set "CMD_FILE=C:\Users\Secretary\user_behavior_generation\worker\current_cmd.txt"
set "WORKER_DIR=C:\Users\Secretary\user_behavior_generation\worker"

:: --- FASE 1: RICEZIONE DA ANSIBLE ---
if NOT "%~1"=="" goto :MODE_RECEIVE
goto :MODE_EXECUTE

:MODE_RECEIVE
set "INPUT_TARGET=%~1"
set "ACTION=%~2"
if "%ACTION%"=="" set ACTION=generic

:: Scriviamo nel file
echo %ACTION% %INPUT_TARGET%> "%CMD_FILE%"
schtasks /run /tn OpenBrowser
exit /b 0

:MODE_EXECUTE
:: --- FASE 2: ESECUZIONE VISIBILE ---
set /p MY_CMD=<"%CMD_FILE%"

:: Parsiamo la stringa
for /f "tokens=1* delims= " %%a in ("%MY_CMD%") do (
    set "TYPE=%%a"
    set "TARGET=%%b"
)

cd /d "%WORKER_DIR%"

:: ==========================================================
:: INIZIO DEBUG AREA
:: ==========================================================
cls
echo.
echo ########################################################
echo #                 DEBUG DIAGNOSTICA                    #
echo ########################################################
echo.
echo [1] Contenuto grezzo letto dal file txt:
echo     "%MY_CMD%"
echo.
echo [2] Variabile TYPE estratta:
echo     [%TYPE%]
echo.
echo [3] Variabile TARGET estratta:
echo     [%TARGET%]
echo.
echo [4] Comando Python che sto per lanciare:
echo     .\venv\Scripts\python.exe smart_worker.py "%TARGET%" "%TYPE%"
echo.
echo ########################################################
echo.
echo Premi un tasto per continuare l'esecuzione...
pause
:: ==========================================================
:: FINE DEBUG AREA
:: ==========================================================


:: --- SELEZIONE AZIONE ---

:: CASO 1: STAMPA
if "%TYPE%"=="print" (
    echo Esecuzione Print...
    .\PDFtoPrinter.exe "%TARGET%"
    timeout /t 15 /nobreak
    taskkill /IM AcroRd32.exe /F /T 2>nul
    taskkill /IM msedge.exe /F /T 2>nul
    goto :EOF
)

:: CASO 2: MAIL
if "%TYPE%"=="mail" (
    echo Esecuzione Mail...
    start "" msedge.exe --app=https://mail.google.com/mail/u/0/
    goto :EOF
)

:: CASO 3: PDF
if "%TYPE%"=="pdf" (
    echo Esecuzione PDF Reader...
    taskkill /IM msedge.exe /F /T 2>nul
    .\venv\Scripts\python.exe pdf_worker.py "%TARGET%"
    pause
    goto :EOF
)

:: CASO 4: WEB (Generic / Video)
echo Esecuzione Web Script...
taskkill /IM msedge.exe /F /T 2>nul

:: Lancio lo script (ho messo pause dopo per vedere eventuali errori python)
.\venv\Scripts\python.exe smart_worker.py "%TARGET%" "%TYPE%"
echo.
echo Script Python terminato. Se vedi errori sopra, leggili ora.
pause

:EOF
exit /b 0
