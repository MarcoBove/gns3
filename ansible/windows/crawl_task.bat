@echo off
set "CMD_FILE=C:\Users\Student\behavior_generation\worker\current_cmd.txt"

:: --- FASE 1: RICEZIONE DA ANSIBLE ---
if NOT "%~2"=="" goto :MODE_RECEIVE
goto :MODE_EXECUTE

:MODE_RECEIVE
:: Scriviamo TIPO e URL nel file. Esempio: "URL https://youtube.com"
echo %~1 %~2 > "%CMD_FILE%"
schtasks /run /tn OpenBrowser
exit /b 0

:MODE_EXECUTE
set /p MY_CMD=<"%CMD_FILE%"
for /f "tokens=1,2 delims= " %%a in ("%MY_CMD%") do (
    set TYPE=%%a
    set TARGET=%%b
)

:: CLEANUP VECCHI PROCESSI (Importante per Selenium)
taskkill /IM msedge.exe /F /T 2>nul
taskkill /IM python.exe /F /T 2>nul

:: AVVIO SMART WORKER
if "%TYPE%"=="URL" (
    :: Chiama lo script Python che usa Selenium
    python C:\Users\Student\behavior_generation\worker\smart_worker.py %TARGET% generic
)

if "%TYPE%"=="VIDEO" (
    python C:\Users\Student\behavior_generation\worker\smart_worker.py %TARGET% video
)

exit /b 0
