@echo off
echo Starting Daniel Signs Operations Hub...
echo ----------------------------------------
cd /d "%~dp0"
".\.venv\Scripts\python.exe" -m streamlit run main.py
pause
