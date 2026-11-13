@echo off
cd /d "%~dp0"
echo === Bomberman: create desktop and Start menu shortcuts ===
set "PYDIR=%USERPROFILE%\AppData\Local\Programs\Python"
set "PYW="
for %%V in (313 312 311 310) do if not defined PYW if exist "%PYDIR%\Python%%V\pythonw.exe" set "PYW=%PYDIR%\Python%%V\pythonw.exe"
if not defined PYW for /f "delims=" %%P in ('"%SystemRoot%\System32\where.exe" pythonw 2^>nul') do if not defined PYW set "PYW=%%P"
if not defined PYW (
  echo Python was not found. Install it from https://www.python.org/downloads/ and run this again.
  pause
  exit /b 1
)
set "PY=%PYW:pythonw.exe=python.exe%"
echo Using: %PYW%
"%PY%" -c "import pygame" >nul 2>nul
if errorlevel 1 (
  echo Installing pygame - first time only, needs internet...
  "%PY%" -m pip install --user --quiet -r requirements.txt
)
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\create_shortcut.ps1" -PythonW "%PYW%"
if errorlevel 1 (
  echo Could not create the shortcuts.
  pause
  exit /b 1
)
echo.
echo Done! Open Bomberman from the desktop icon or the Start menu.
pause
