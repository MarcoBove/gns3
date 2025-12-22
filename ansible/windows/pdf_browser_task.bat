@echo off
set "CMD_FILE=C:\Users\Student\user_behavior_generation\worker\current_cmd.txt"
set "WORKER_DIR=C:\Users\Student\user_behavior_generation\worker"

:: --- FASE 1: RICEZIONE DA ANSIBLE ---
if NOT "%~1"=="" goto :MODE_RECEIVE
goto :MODE_EXECUTE

:MODE_RECEIVE
:: Ansible ci passa: %1 = FILE_PATH, %2 = ACTION (che sarà "pdf")
set TARGET=%~1
set ACTION=%~2

:: Scriviamo nel file: ACTION spazio TARGET
echo %ACTION% %TARGET% > "%CMD_FILE%"

:: Avvia Task Scheduler (visibile)
schtasks /run /tn OpenBrowser
exit /b 0

:MODE_EXECUTE
:: --- FASE 2: ESECUZIONE VISIBILE ---
set /p MY_CMD=<"%CMD_FILE%"

:: Parsiamo la stringa
for /f "tokens=1,2 delims= " %%a in ("%MY_CMD%") do (
    set TYPE=%%a
    set FILE_TARGET=%%b
)

taskkill /IM msedge.exe /F /T 2>nul
taskkill /IM python.exe /F /T 2>nul

cd /d "%WORKER_DIR%"

:: --- SELEZIONE SCRIPT ---
if "%TYPE%"=="pdf" (
    :: Chiama il nuovo script PDF
    python pdf_worker.py %FILE_TARGET%
) else (
    :: Chiama il vecchio script web (generic/video)
    python smart_worker.py %FILE_TARGET% %TYPE%
)

exit /b 0
