# Backend Harness Rules

> FastAPI, SQLAlchemy(Async), Redis, JWT 관련 코드 수정 시 이 문서를 반드시 준수합니다.

---

## 1. 기술 스택 고정

| 항목 | 구현체 | 비고 |
|------|--------|------|
| 웹 프레임워크 | FastAPI + Uvicorn | `backend/main.py` |
| ORM | SQLAlchemy 2.x (Async) | `create_async_engine`, `async_sessionmaker` |
| DB 드라이버 | asyncpg | PostgreSQL 15 전용 |
| 세션 관리 | `AsyncSessionLocal(engine, class_=AsyncSession, expire_on_commit=False)` | |
| Redis 클라이언트 | `redis.asyncio.from_url(REDIS_URL, decode_responses=True)` | |
| JWT 라이브러리 | PyJWT (`import jwt`) | `pyjwt` 패키지 |
| 비밀번호 인코딩 | base64 (`base64.b64encode/b64decode`) | 현재 구현 기준 |

---

## 2. 파일별 책임 분리 (Single Responsibility)

### 2.1 `backend/main.py` — 앱 진입점
- FastAPI 인스턴스 생성 + CORS 미들웨어 등록
- `@app.on_event("startup")`에서 벡터DB 초기화 (`get_vector_store()` → `load_existing_vector_store()` 또는 `create_new_embeddings()`)
- 라우터 등록: `app.include_router(auth_router)`
- 엔드포인트: `GET /` (HTML 반환), `POST /api/chat` (에이전트 응답)
- **수정 시 주의:** `global_vector_store`와 `set_global_vector_store(vs)` 호출 체인을 끊지 말 것

### 2.2 `backend/api/auth.py` — 인증 라우터
**라우터 프리픽스:** `/auth`, **태그:** `["auth"]`

| 엔드포인트 | 메서드 | 핵심 로직 |
|-----------|--------|----------|
| `/auth/signup` | POST | 이메일 중복 확인 → `student_service.create_student()` → 응답(id, email, nickname) |
| `/auth/login` | POST | student 조회 → `is_active` 확인 → 비밀번호 검증 → AT+RT 발급 → Redis `SETEX rt:{id}:{jti}` |
| `/auth/refresh` | POST | RT 디코딩 → `type=="refresh"` 확인 → Redis `EXISTS rt:{uid}:{jti}` → 새 AT 발급 |
| `/auth/logout` | POST | AT에서 jti 추출 → Redis `SETEX bl:{jti}` → RT가 있으면 Redis `DEL rt:{uid}:{jti}` |
| `/auth/me` | GET | `Depends(get_current_user)` → student 정보 반환 |

**`get_current_user()` 디펜던시 (auth.py:114-142):**
```python
# 이 순서를 반드시 지켜야 합니다:
1. Authorization 헤더에서 "Bearer " 이후 토큰 추출
2. auth_service.decode_token(token)으로 JWT 검증
3. payload["type"] == "access" 확인 (아니면 401)
4. Redis EXISTS bl:{jti} 확인 (존재하면 "Token revoked" 401)
5. DB에서 student 조회 (없거나 is_active==False면 401)
6. student 객체 반환
```

### 2.3 `backend/services/auth_service.py` — JWT/패스워드 서비스
- `encode_password(password)` → base64 인코딩
- `verify_password(plain, encoded)` → base64 디코딩 후 비교
- `create_access_token(user_id, email)` → `(token_str, jti_str)` 튜플 반환
- `create_refresh_token(user_id)` → `(token_str, jti_str)` 튜플 반환
- `decode_token(token)` → `jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])`
- `get_token_expire_seconds(token_type)` → 초 단위 만료시간 반환
- **주의:** 모든 함수는 **순수 함수(동기)** — DB/Redis 접근 없음

### 2.4 `backend/services/student_service.py` — Student CRUD
- `get_student_by_email(db, email)` → `select(Student).where(Student.email == email)`
- `get_student_by_id(db, student_id)` → `select(Student).where(Student.id == student_id)`
- `create_student(db, email, password, nickname)` → `Student()` 생성 → `db.add()` → `db.commit()` → `db.refresh()`
- **주의:** 모든 함수는 `async` — `AsyncSession`을 인자로 받음

### 2.5 `backend/models/student.py` — ORM 모델
```python
Base = declarative_base()  # 이 Base를 모든 모델이 공유

class Student(Base):
    __tablename__ = "student"
    id        = Column(BigInteger, primary_key=True, autoincrement=True)
    email     = Column(String(255), unique=True, nullable=False, index=True)
    password  = Column(String, nullable=False)        # base64 인코딩 저장
    nickname  = Column(String(100))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
```
- **새 모델 추가 시:** 반드시 같은 `Base`를 import하여 사용
- **컬럼 추가 시:** Alembic 마이그레이션 스크립트 생성 필수

### 2.6 `backend/config/database.py` — DB 세션 팩토리
```python
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```
- **`Depends(get_db)`로 라우터에 주입** — 수동 세션 생성 금지
- **`expire_on_commit=False`** 설정 변경 금지 (commit 후에도 ORM 객체 속성 접근 필요)

### 2.7 `backend/config/redis_client.py` — Redis 클라이언트
```python
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def get_redis():
    return redis_client
```
- **싱글턴 패턴** — 모듈 로드 시 1회 생성, `get_redis()`로 참조
- **`decode_responses=True`** — 모든 값이 `str`로 반환됨 (bytes 아님)

---

## 3. API 응답 규칙

### 3.1 에러 코드 매핑
| HTTP 코드 | 사용 상황 |
|-----------|----------|
| 400 | 이메일 중복 (`"Email already registered"`) |
| 401 | 토큰 없음, 만료, 블랙리스트, 잘못된 타입, 비활성 사용자 |
| 404 | 리소스 미발견 |
| 500 | 서버 내부 오류 (FastAPI 기본 핸들링) |

### 3.2 성공 응답 포맷
- `/auth/signup` → `{ "id", "email", "nickname" }`
- `/auth/login` → `{ "access_token", "refresh_token", "token_type": "bearer" }`
- `/auth/refresh` → `{ "access_token", "token_type": "bearer" }`
- `/auth/logout` → `{ "message": "Logged out successfully" }`
- `/auth/me` → `{ "id", "email", "nickname", "is_active", "created_at" }`
- `/api/chat` → `{ "answer", "status": "success" | "error" }`

---

## 4. Docker Compose 인프라

```yaml
# docker-compose.yml 핵심 포인트:
postgres:
  - 이미지: postgres:15-alpine
  - 외부포트: 5555 → 내부: 5432
  - 볼륨: pgdata (영속)
  - healthcheck: pg_isready

redis:
  - 이미지: redis:7-alpine
  - 외부포트: 6379
  - 볼륨: redisdata (AOF 영속)
  - command: redis-server --appendonly yes
  - healthcheck: redis-cli ping
```
- **포트 5555** 주의: `DATABASE_URL`에서 `localhost:5555`로 접속 (Docker가 5555→5432 매핑)

---

## 5. 코드 수정 시 체크리스트

신규 엔드포인트 추가 시:
- [ ] 라우터에 적절한 prefix/tags 설정했는가?
- [ ] 인증이 필요하면 `Depends(get_current_user)` 적용했는가?
- [ ] DB 세션은 `Depends(get_db)`로 주입하는가?
- [ ] Redis 접근은 `await get_redis()`로 하는가?
- [ ] 에러 응답은 `HTTPException`으로 일관되게 반환하는가?
- [ ] Pydantic `BaseModel`로 요청/응답 스키마를 정의했는가?

서비스 함수 추가 시:
- [ ] `async def`로 선언하고 `AsyncSession`을 인자로 받는가?
- [ ] `select()` 기반 쿼리를 사용하는가? (raw SQL 최소화)
- [ ] `await db.commit()` 후 `await db.refresh(obj)` 패턴을 따르는가?

모델 수정 시:
- [ ] `student.py`의 `Base`를 공유하는가?
- [ ] Alembic 마이그레이션 스크립트를 생성했는가?
- [ ] `database/schema.sql`에도 DDL 변경을 반영했는가?
