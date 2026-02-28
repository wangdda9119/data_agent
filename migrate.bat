@echo off

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing dependencies...
pip install psycopg2-binary

echo Starting Docker services...
docker compose up -d postgres redis

echo Waiting for services to be ready...
timeout /t 20

echo Creating database table...
python create_table.py

echo Done!
pause
