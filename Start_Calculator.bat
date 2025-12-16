@echo off
echo Starting Daniel Signs Quote Calculator...
echo ----------------------------------------
cd /d "%~dp0"
".\.venv\Scripts\python.exe" -m streamlit run main.py
pause
