import psycopg2
import os

# 여기에 실제 DB 정보 입력
DB_CONFIG = {
    "host": "localhost",
    "database": "appdb",  # 실제 DB 이름으로 변경
    "user": "appuser",
    "password": "apppass",  # 실제 비밀번호로 변경
    "port": 5555
}

def execute_schema():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            with open("database/schema.sql", "r", encoding="utf-8") as f:
                sql = f.read()
                cursor.execute(sql)
            conn.commit()
            print("✅ 스키마 실행 완료")
    except Exception as e:
        conn.rollback()
        print(f"❌ 오류: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    execute_schema()
