@echo off

if not exist venv (
    echo Virtual environment not found. Please run migrate.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate

echo Checking database tables...
python check_db.py

pause
