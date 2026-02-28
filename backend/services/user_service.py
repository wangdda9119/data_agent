from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.user import User
from backend.services.auth_service import hash_password

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, email: str, password: str, nickname: str = None):
    user = User(
        email=email,
        password_hash=hash_password(password),
        nickname=nickname
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
