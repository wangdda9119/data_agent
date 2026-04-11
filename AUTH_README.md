# Data Agent - JWT 인증 시스템

## 설치 및 실행 가이드

### 1. 환경 설정

`.env` 파일을 생성하고 다음 내용을 설정하세요:

```env
OPENAI_API_KEY=your-openai-api-key

# Database
POSTGRES_DB=appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppass
DATABASE_URL=postgresql+asyncpg://appuser:apppass@localhost:5432/appdb

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MIN=15
REFRESH_TOKEN_EXPIRE_DAYS=14
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. Docker 서비스 시작 및 마이그레이션

```bash
migrate.bat
```

또는 수동으로:

```bash
# Docker 서비스 시작
docker compose up -d

# 마이그레이션 실행
python -m alembic upgrade head
```

### 4. 서버 실행

```bash
start.bat
```

또는:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## API 엔드포인트

### 인증 API

- `POST /auth/signup` - 회원가입
- `POST /auth/login` - 로그인
- `POST /auth/refresh` - 토큰 갱신
- `POST /auth/logout` - 로그아웃
- `GET /auth/me` - 현재 사용자 정보

### 채팅 API

- `POST /api/chat` - AI 챗봇 대화

## 테스트

```bash
pytest tests/
```
