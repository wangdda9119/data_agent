from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from urllib.parse import urlparse

router = APIRouter()
security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"


def _parse_db_config():
    """DATABASE_URL에서 DB 접속 정보 파싱 (개발/운영 통합)"""
    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        # asyncpg 프리픽스 제거 후 파싱
        url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        parsed = urlparse(url)
        config = {
            "host": parsed.hostname,
            "database": parsed.path.lstrip("/"),
            "user": parsed.username,
            "password": parsed.password,
            "port": parsed.port or 5432,
        }
        # Supabase는 SSL 필요
        if "supabase" in db_url:
            config["sslmode"] = "require"
        return config
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "database": os.getenv("DB_NAME", "your_database"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password"),
    }


DB_CONFIG = _parse_db_config()


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다"
        )


@router.get("/mypage")
def get_mypage(payload: dict = Depends(verify_token)):
    student_id = payload.get("user_id")
    
    if not student_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자 정보를 찾을 수 없습니다"
        )
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    s.email,
                    s.name,
                    c.course_name
                FROM student s
                LEFT JOIN course c ON s.course_id = c.id
                WHERE s.id = %s
            """, (student_id,))
            
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="사용자를 찾을 수 없습니다"
                )
            
            return {
                "email": result["email"],
                "name": result["name"],
                "course_name": result["course_name"]
            }
    finally:
        conn.close()
