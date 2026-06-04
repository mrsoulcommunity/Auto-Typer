@echo off
cd /d %~dp0
python -m pip install -r requirements.txt
pyinstaller --noconsole --onefile --name AutoTyper auto_typer.py
echo.
echo Build finished. The executable will be in the dist folder.
pause
