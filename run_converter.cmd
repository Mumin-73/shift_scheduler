@echo off
chcp 65001 > nul
cd /d "%~dp0"
call "C:\Users\wjdgy\anaconda3\Scripts\activate.bat" venv_c2
python image2excel.py
pause

:: @echo off
:: chcp 65001 > nul
:: cd /d "%~dp0"
:: python image2excel.py
:: pause
