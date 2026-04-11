import jwt
from datetime import datetime, timedelta
import base64
import os
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 14))

def encode_password(password: str) -> str:
    return base64.b64encode(password.encode()).decode()

def verify_password(plain_password: str, encoded_password: str) -> bool:
    try:
        decoded = base64.b64decode(encoded_password.encode()).decode()
        return plain_password == decoded
    except:
        return False

def create_access_token(user_id: int, email: str) -> tuple[str, str]:
    jti = str(uuid4())
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    payload = {
        "sub": str(user_id),
        "email": email,
        "jti": jti,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": exp
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, jti

def create_refresh_token(user_id: int) -> tuple[str, str]:
    jti = str(uuid4())
    exp = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "jti": jti,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "exp": exp
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, jti

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

def get_token_expire_seconds(token_type: str) -> int:
    if token_type == "access":
        return ACCESS_TOKEN_EXPIRE_MIN * 60
    return REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
