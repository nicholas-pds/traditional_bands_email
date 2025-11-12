@echo off
REM Change to the script's directory (project root)
cd /d "C:\Users\Partners\Desktop\repos\traditional_bands_email"

REM Run the Python script using uv
powershell.exe -Command "uv run python -m src.main"

pause