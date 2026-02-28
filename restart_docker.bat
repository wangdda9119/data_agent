@echo off
echo Stopping Docker services...
docker compose down

echo Removing volumes...
docker volume rm data_agent_pgdata 2>nul
docker volume rm data_agent_redisdata 2>nul

echo Starting Docker services with .env...
docker compose up -d

echo Waiting 20 seconds...
timeout /t 20

echo Checking services...
docker ps --filter "name=data_agent"

echo.
echo Done! Connect with:
echo   Host: localhost
echo   Port: 5555
echo   Database: appdb
echo   Username: appuser
echo   Password: apppass
echo.
echo Now run setup_db.bat
pause
