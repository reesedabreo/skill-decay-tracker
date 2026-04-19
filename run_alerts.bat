@echo off
cd /d C:\Users\91917\OneDrive\Desktop\skilldk
call venv\Scripts\activate
python manage.py send_alerts > scheduler_log.txt 2>&1