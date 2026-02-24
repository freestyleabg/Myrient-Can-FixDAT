@echo off
setlocal

set "ROOT=%~dp0"
set "PY=%ROOT%.venv\Scripts\python.exe"

if exist "%PY%" (
  "%PY%" -m PyInstaller --onefile --windowed --icon "%ROOT%.github\icon_white.png" --add-data "%ROOT%.github\icon_white.png;.github" --name ESDE-ROM-Formatter "%ROOT%esde_rom_formatter_gui.py"
) else (
  python -m PyInstaller --onefile --windowed --icon "%ROOT%.github\icon_white.png" --add-data "%ROOT%.github\icon_white.png;.github" --name ESDE-ROM-Formatter "%ROOT%esde_rom_formatter_gui.py"
)

endlocal



