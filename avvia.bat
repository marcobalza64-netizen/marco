@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === Spettro Frequenza ===
echo Microfono -^> grafico frequenze colorato
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo Python non trovato.
  echo Scaricalo da: https://www.python.org/downloads/
  echo Durante l'installazione spunta "Add Python to PATH".
  echo.
  pause
  exit /b 1
)

if not exist ".venv" (
  echo Prima esecuzione: preparo l'ambiente Python...
  python -m venv .venv
  if errorlevel 1 (
    echo Impossibile creare il virtualenv.
    pause
    exit /b 1
  )
)

call .venv\Scripts\activate.bat

echo Controllo dipendenze...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Installazione dipendenze fallita.
  echo Prova da Prompt dei comandi:
  echo   cd "%cd%"
  echo   python -m venv .venv
  echo   .venv\Scripts\activate
  echo   pip install -r requirements.txt
  echo.
  pause
  exit /b 1
)

echo.
echo Avvio in corso...
echo Se Windows chiede il microfono: premi Consenti.
echo Per uscire: chiudi la finestra del grafico.
echo.

python spectrum_visualizer.py

echo.
pause
