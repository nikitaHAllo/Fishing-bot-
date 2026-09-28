@echo off
cd /d "c:\Users\Roma\Desktop\Fish bot"
:loop
".venv\Scripts\python.exe" bot.py
ping 127.0.0.1 -n 6 >nul
goto loop
