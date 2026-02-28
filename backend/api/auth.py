from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from backend.config.database import get_db
from backend.config.redis_client import get_redis
from backend.services import student_service, auth_service
import jwt

router = APIRouter(prefix="/auth", tags=["auth"])

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    nickname: str = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str = None

@router.post("/signup")
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    existing = await student_service.get_student_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    student = await student_service.create_student(db, req.email, req.password, req.nickname)
    return {"id": student.id, "email": student.email, "nickname": student.nickname}

@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    redis = await get_redis()
    student = await student_service.get_student_by_email(db, req.email)
    
    if not student or not student.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not auth_service.verify_password(req.password, student.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token, access_jti = auth_service.create_access_token(student.id, student.email)
    refresh_token, refresh_jti = auth_service.create_refresh_token(student.id)
    
    refresh_key = f"rt:{student.id}:{refresh_jti}"
    await redis.setex(refresh_key, auth_service.get_token_expire_seconds("refresh"), "1")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh(req: RefreshRequest):
    redis = await get_redis()
    
    try:
        payload = auth_service.decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = int(payload["sub"])
        refresh_jti = payload["jti"]
        
        refresh_key = f"rt:{user_id}:{refresh_jti}"
        if not await redis.exists(refresh_key):
            raise HTTPException(status_code=401, detail="Token revoked or expired")
        
        access_token, _ = auth_service.create_access_token(user_id, payload.get("email", ""))
        return {"access_token": access_token, "token_type": "bearer"}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/logout")
async def logout(req: LogoutRequest, authorization: str = Header(None)):
    redis = await get_redis()
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    access_token = authorization.split(" ")[1]
    
    try:
        payload = auth_service.decode_token(access_token)
        access_jti = payload["jti"]
        user_id = int(payload["sub"])
        exp = payload["exp"]
        
        ttl = exp - int(jwt.datetime.datetime.utcnow().timestamp())
        if ttl > 0:
            await redis.setex(f"bl:{access_jti}", ttl, "1")
        
        if req.refresh_token:
            try:
                refresh_payload = auth_service.decode_token(req.refresh_token)
                refresh_jti = refresh_payload["jti"]
                await redis.delete(f"rt:{user_id}:{refresh_jti}")
            except:
                pass
        
        return {"message": "Logged out successfully"}
        
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(authorization: str = Header(None), db: AsyncSession = Depends(get_db)):
    redis = await get_redis()
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = authorization.split(" ")[1]
    
    try:
        payload = auth_service.decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        jti = payload["jti"]
        if await redis.exists(f"bl:{jti}"):
            raise HTTPException(status_code=401, detail="Token revoked")
        
        user_id = int(payload["sub"])
        student = await student_service.get_student_by_id(db, user_id)
        
        if not student or not student.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        return student
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/me")
async def get_me(student = Depends(get_current_user)):
    return {
        "id": student.id,
        "email": student.email,
        "nickname": student.nickname,
        "is_active": student.is_active,
        "created_at": student.created_at
    }
