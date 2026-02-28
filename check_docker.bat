@echo off
echo Checking Docker services...
docker ps --filter "name=data_agent"

echo.
echo Checking PostgreSQL logs...
docker logs data_agent_postgres --tail 20

echo.
pause
