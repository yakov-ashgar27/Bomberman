@echo off
cd /d "%~dp0"
echo === Bomberman ===
set "PY="
set "PYDIR=%USERPROFILE%\AppData\Local\Programs\Python"
if exist "%PYDIR%\Python313\python.exe" set "PY=%PYDIR%\Python313\python.exe"
if not defined PY if exist "%PYDIR%\Python312\python.exe" set "PY=%PYDIR%\Python312\python.exe"
if not defined PY if exist "%PYDIR%\Python311\python.exe" set "PY=%PYDIR%\Python311\python.exe"
if not defined PY if exist "%PYDIR%\Python310\python.exe" set "PY=%PYDIR%\Python310\python.exe"
if not defined PY if exist "%PYDIR%\Launcher\py.exe" set "PY=%PYDIR%\Launcher\py.exe"
if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo Python is not installed. Download it from https://www.python.org/downloads/
  echo During install, tick "Add Python to PATH". Then run this file again.
  pause
  exit /b 1
)
echo Using: %PY%
"%PY%" --version
"%PY%" -c "import pygame" >nul 2>nul
if errorlevel 1 (
  echo Installing pygame - first time only, needs internet...
  "%PY%" -m pip install --user --quiet -r requirements.txt
)
echo Starting the game...
"%PY%" main.py
if errorlevel 1 pause
