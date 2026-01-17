:MODE_RECEIVE
set "P1=%~1"
set "P2=%~2"
set "P3=%~3"

:: Se esiste un terzo parametro, significa che Windows ha spezzato l'URL sull'uguale (=)
:: P1 = prima parte URL, P2 = ID video, P3 = Azione (video)
if NOT "%P3%"=="" (
    set "INPUT_TARGET=%P1%=%P2%"
    set "ACTION=%P3%"
) else (
    :: Nessuno split, tutto normale
    set "INPUT_TARGET=%P1%"
    set "ACTION=%P2%"
)

if "%ACTION%"=="" set ACTION=generic

:: Scriviamo nel file
echo %ACTION% %INPUT_TARGET%> "%CMD_FILE%"
schtasks /run /tn OpenBrowser
exit /b 0
