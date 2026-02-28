import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("Testing PostgreSQL Connection")
print("=" * 50)

host = 'localhost'
port = 5555
user = os.getenv('POSTGRES_USER', 'appuser')
password = os.getenv('POSTGRES_PASSWORD', 'apppass')
database = os.getenv('POSTGRES_DB', 'appdb')

print(f"\nHost: {host}")
print(f"Port: {port}")
print(f"User: {user}")
print(f"Database: {database}")
print(f"Password: {'*' * len(password)}")

try:
    print("\nConnecting...")
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        connect_timeout=5
    )
    print("✓ Connection successful!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"\nPostgreSQL version: {version[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Connection failed!")
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check if Docker is running: docker ps")
    print("2. Check PostgreSQL logs: docker logs data_agent_postgres")
    print("3. Verify .env file has correct credentials")
