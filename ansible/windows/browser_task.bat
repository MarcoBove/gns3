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

exit /b 0
