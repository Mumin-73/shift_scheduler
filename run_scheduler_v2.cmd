@echo off
chcp 65001 > nul
cd /d "%~dp0"
call "C:\Users\wjdgy\anaconda3\Scripts\activate.bat" venv_c2
python shift_scheduler_v2.py
pause

:: @echo off
:: chcp 65001 > nul
:: cd /d "%~dp0"
:: python shift_scheduler_v2.py
:: pause
