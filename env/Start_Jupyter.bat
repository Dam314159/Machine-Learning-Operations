@echo off
cd /d "%~dp0env"

python.exe -m jupyter lab --notebook-dir="%~dp0.."