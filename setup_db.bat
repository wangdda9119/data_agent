@echo off

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing psycopg2-binary...
pip install psycopg2-binary python-dotenv

echo.
echo ========================================
echo Step 1: Starting Docker services
echo ========================================
docker compose up -d postgres redis

echo.
echo Waiting 20 seconds for services to start...
timeout /t 20

echo.
echo ========================================
echo Step 2: Testing DB connection
echo ========================================
python test_db_connection.py

echo.
echo ========================================
echo Step 3: Creating student table
echo ========================================
python create_student_table.py

echo.
echo Done!
pause
