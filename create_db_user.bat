@echo off
echo Creating database and user manually...

docker exec -i data_agent_postgres psql -U postgres << EOF
CREATE USER appuser WITH PASSWORD 'apppass';
CREATE DATABASE appdb OWNER appuser;
GRANT ALL PRIVILEGES ON DATABASE appdb TO appuser;
\q
EOF

echo.
echo Done! Now try connecting with DBeaver:
echo Host: localhost
echo Port: 5432
echo Database: appdb
echo Username: appuser
echo Password: apppass

pause
