@echo off
title Year 9 English Tutor — Streamlit
echo.
echo  Year 9 English Tutor (Streamlit)
echo  ==================================
echo  Installing / checking Streamlit...
echo.

python -m pip install streamlit --quiet --disable-pip-version-check

echo.
echo  Starting tutor — your browser will open automatically.
echo  Press Ctrl+C in this window to quit.
echo.

cd /d "%~dp0"
python -m streamlit run streamlit_app.py --server.headless false

pause
