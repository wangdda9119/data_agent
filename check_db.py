import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_tables():
    conn = await asyncpg.connect(
        host='localhost',
        port=5555,
        user=os.getenv('POSTGRES_USER', 'appuser'),
        password=os.getenv('POSTGRES_PASSWORD', 'apppass'),
        database=os.getenv('POSTGRES_DB', 'appdb')
    )
    
    print("=" * 50)
    print("DATABASE CONNECTION: SUCCESS")
    print("=" * 50)
    
    # 테이블 목록 조회
    tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    print("\n[TABLES]")
    if tables:
        for table in tables:
            print(f"  - {table['table_name']}")
    else:
        print("  No tables found")
    
    # user 테이블이 있으면 구조 확인
    if any(t['table_name'] == 'user' for t in tables):
        print("\n[USER TABLE STRUCTURE]")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'user'
            ORDER BY ordinal_position
        """)
        
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f"DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']}: {col['data_type']} {nullable} {default}")
        
        # 레코드 수 확인
        count = await conn.fetchval("SELECT COUNT(*) FROM \"user\"")
        print(f"\n[USER TABLE RECORDS]: {count}")
    
    await conn.close()
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(check_tables())
