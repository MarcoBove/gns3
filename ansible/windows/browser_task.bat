@echo off
set "URL_FILE=C:\Users\User\dapt2021\worker\current_url.txt"

:: --- FASE 1: CONTROLLO INPUT ---
:: Se c'è un parametro (%1), siamo stati chiamati da Ansible via SSH.
if NOT "%~1"=="" goto :MODE_RECEIVE

:: Se non c'è parametro, siamo stati chiamati dal Task Scheduler.
goto :MODE_EXECUTE

:MODE_RECEIVE
:: ---------------------------------------------------------
:: SIAMO IN SESSIONE SSH (BACKGROUND)
:: 1. Scriviamo l'URL nel file
echo %~1 > "%URL_FILE%"
:: 2. Svegliamo il Task Scheduler
schtasks /run /tn DaptBrowser
:: 3. Usciamo
exit /b 0

:MODE_EXECUTE
:: ---------------------------------------------------------
:: SIAMO IN SESSIONE UTENTE (DESKTOP ATTIVO)
:: 1. Leggiamo l'URL dal file
set /p TARGET_URL=<"%URL_FILE%"

:: 2. Apriamo il browser (o il tuo script python)
start msedge %TARGET_URL%
:: Oppure se usi python: python browseInternet.py %TARGET_URL%

:: -----------------------------------------------------
:: CLEANUP: Chiude le finestre vecchie prima di aprire le nuove
:: -----------------------------------------------------
:: /IM = Image Name (nome programma)
:: /F = Force (forza chiusura)
:: /T = Tree (chiude anche i processi figli)
:: 2>nul = Nasconde l'errore se il programma non era aperto

taskkill /IM msedge.exe /F /T 2>nul

:: Aspetta 1 secondo per essere sicuri che si sia chiuso tutto
timeout /t 1 /nobreak >nul

exit /b 0
