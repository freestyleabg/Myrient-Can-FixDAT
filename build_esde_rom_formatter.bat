@echo off
setlocal

set "ROOT=%~dp0"
set "PY=%ROOT%.venv\Scripts\python.exe"

if exist "%PY%" (
  "%PY%" -m PyInstaller --onefile --windowed --name ESDE-ROM-Formatter "%ROOT%esde_rom_formatter_gui.py"
) else (
  python -m PyInstaller --onefile --windowed --name ESDE-ROM-Formatter "%ROOT%esde_rom_formatter_gui.py"
)

endlocal



