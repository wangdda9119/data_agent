from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.student import Student
from backend.services.auth_service import encode_password

async def get_student_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(Student).where(Student.email == email))
    return result.scalar_one_or_none()

async def get_student_by_id(db: AsyncSession, student_id: int):
    result = await db.execute(select(Student).where(Student.id == student_id))
    return result.scalar_one_or_none()

async def create_student(db: AsyncSession, email: str, password: str, nickname: str = None):
    student = Student(
        email=email,
        password=encode_password(password),
        nickname=nickname
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student
