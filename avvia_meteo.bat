@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === Meteo Bordighera ===
echo.

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  set "PY=py -3"
  goto :run
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
  set "PY=python"
  goto :run
)

where python3 >nul 2>&1
if %ERRORLEVEL%==0 (
  set "PY=python3"
  goto :run
)

echo Python non trovato su questo PC Windows.
echo Scaricalo da: https://www.python.org/downloads/
echo Durante l'installazione spunta "Add python.exe to PATH".
echo.
pause
exit /b 1

:run
echo Avvio server web locale...
echo Il browser si apre su http://127.0.0.1:8787
echo Per uscire: chiudi questa finestra oppure premi Ctrl+C
echo.
%PY% meteo_app.py
echo.
pause
