@echo off
cd /d "%~dp0"
if exist "dist\AtlanteFormule\AtlanteFormule.exe" (
  start "Atlante Formule" "dist\AtlanteFormule\AtlanteFormule.exe"
  exit /b
)
if exist ".venv\Scripts\pythonw.exe" (
  start "Atlante Formule" ".venv\Scripts\pythonw.exe" "main.py"
) else (
  echo Ambiente mancante. Leggi GUIDA.md per installare e avviare il programma.
  pause
)
