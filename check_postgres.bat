@echo off
echo Checking PostgreSQL environment variables inside container...
docker exec data_agent_postgres env | findstr POSTGRES

echo.
echo Trying to connect as postgres user...
docker exec data_agent_postgres psql -U postgres -c "\du"

echo.
echo Trying to connect as appuser...
docker exec data_agent_postgres psql -U appuser -d appdb -c "SELECT version();"

pause
