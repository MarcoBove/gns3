@echo off
:: --- INPUT VARIABLES ---
:: %1 è l'URL (es. https://www.google.com)
:: %2 è il TIPO (es. generic). Se manca, mettiamo 'generic' di default.

set TARGET_URL=%1
set ACTION_TYPE=%2
if "%ACTION_TYPE%"=="" set ACTION_TYPE=generic

:: --- CLEANUP (Opzionale ma consigliato) ---
:: Chiude vecchi processi per evitare blocchi o RAM piena
taskkill /IM msedge.exe /F /T 2>nul
taskkill /IM chrome.exe /F /T 2>nul
taskkill /IM python.exe /F /T 2>nul

:: --- ESECUZIONE ---
:: Ci spostiamo nella cartella corretta
cd /d C:\Users\Student\user_behavior_generation\worker

:: Eseguiamo lo script Python
:: Assicurati che 'python' sia nel PATH di Windows, oppure scrivi il percorso completo es: C:\Python39\python.exe
python smart_worker.py %TARGET_URL% %ACTION_TYPE%
