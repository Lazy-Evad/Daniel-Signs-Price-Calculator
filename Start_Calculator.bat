@echo off
echo Starting Daniel Signs Operations Hub...
echo ----------------------------------------
cd /d "%~dp0"
python -m streamlit run main.py
pause
