@echo off
set "CMD_FILE=C:\Users\Student\user_behavior_generation\worker\current_cmd.txt"
set "WORKER_DIR=C:\Users\Student\user_behavior_generation\worker"

:: --- FASE 1: RICEZIONE DA ANSIBLE ---
if NOT "%~1"=="" goto :MODE_RECEIVE
goto :MODE_EXECUTE

:MODE_RECEIVE
:: Ansible ci passa: %1 = FILE_PATH/URL, %2 = ACTION
set INPUT_TARGET=%~1
set ACTION=%~2

:: Se ACTION è vuota, default a "generic" (per gestire gli URL che magari arrivano senza action esplicita)
if "%ACTION%"=="" set ACTION=generic

:: Scriviamo nel file: ACTION spazio TARGET
echo %ACTION% %INPUT_TARGET% > "%CMD_FILE%"

:: Avvia Task Scheduler (visibile)
schtasks /run /tn OpenBrowser
exit /b 0

:MODE_EXECUTE
:: --- FASE 2: ESECUZIONE VISIBILE ---
set /p MY_CMD=<"%CMD_FILE%"

:: Parsiamo la stringa.
:: NOTA IMPORTANTE: Uso "tokens=1*" invece di "1,2".
:: Se il path del file contiene spazi, "tokens=1,2" lo spezzerebbe.
:: "tokens=1*" prende la prima parola come TYPE e TUTTO il resto come FILE_TARGET.
for /f "tokens=1* delims= " %%a in ("%MY_CMD%") do (
    set TYPE=%%a
    set FILE_TARGET=%%b
)

taskkill /IM msedge.exe /F /T 2>nul
taskkill /IM python.exe /F /T 2>nul

cd /d "%WORKER_DIR%"

:: --- SELEZIONE SCRIPT ---
if "%TYPE%"=="pdf" (
    :: Chiama il nuovo script PDF
    .\venv\Scripts\python.exe pdf_worker.py "%FILE_TARGET%"
) else (
    :: Chiama il vecchio script web
    :: ERRORE PRECEDENTE: Qui usavi %TARGET% che era vuoto. Ora uso %FILE_TARGET%
    :: Inoltre ho invertito l'ordine degli argomenti per matchare lo script 1: URL TYPE
    .\venv\Scripts\python.exe smart_worker.py "%FILE_TARGET%" %TYPE%
)

exit /b 0
