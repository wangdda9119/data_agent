from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Supabase 주소를 postgres:// 로 입력했을 때 자동으로 postgresql+asyncpg:// 로 변환
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# DATABASE_URL 환경변수가 누락된 경우 명시적인 에러 발생
if not DATABASE_URL:
    raise ValueError("🚨 [ERROR] DATABASE_URL 환경변수가 설정되지 않았습니다! Render 대시보드(또는 로컬 .env)에서 DATABASE_URL을 등록해주세요.")

# Supabase 등 외부 DB는 SSL 연결 필요
connect_args = {}
if "supabase" in DATABASE_URL:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context

engine = create_async_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
