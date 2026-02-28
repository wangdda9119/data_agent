import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

print("Connecting to database...")
for i in range(5):
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5555,
            user=os.getenv('POSTGRES_USER', 'appuser'),
            password=os.getenv('POSTGRES_PASSWORD', 'apppass'),
            database=os.getenv('POSTGRES_DB', 'appdb'),
            connect_timeout=5
        )
        print("✓ Connected!")
        break
    except Exception as e:
        if i < 4:
            print(f"Retry {i+1}/5... ({e})")
            time.sleep(5)
        else:
            print(f"✗ Failed to connect after 5 attempts")
            print(f"Error: {e}")
            raise

cursor = conn.cursor()

sql = """
CREATE TABLE IF NOT EXISTS "user" (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    nickname VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_user_email ON "user"(email);
"""

cursor.execute(sql)
conn.commit()

print("✓ User table created successfully")

cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user' ORDER BY ordinal_position")
columns = cursor.fetchall()

print("\n[USER TABLE STRUCTURE]")
for col in columns:
    print(f"  {col[0]}: {col[1]}")

cursor.close()
conn.close()
