# 순천향대학교 AI 챗봇 서비스 — AI Agent Harness

> 이 파일은 AI 에이전트(코파일럿, Claude, Gemini 등)가 본 프로젝트에서 코드를 수정·추가·삭제할 때 **반드시 최우선으로 읽고 준수해야 하는 루트 명세서**입니다.
> 상세 영역별 규칙은 `.agent_rules/` 폴더를 추가로 참조하십시오.

---

## 1. 프로젝트 개요

PDF 기반 RAG(Retrieval-Augmented Generation) 아키텍처와 JWT+Redis 인증 시스템을 결합한 대학교 AI 어시스턴트 서비스입니다.

| 계층 | 기술 | 핵심 파일 |
|------|------|-----------|
| Frontend | Vue 3, TypeScript, Tailwind CSS | `frontend/sch-landing-vue/src/` |
| Backend API | FastAPI, Uvicorn, Python | `backend/main.py`, `backend/api/auth.py` |
| AI/LLM Agent | LangGraph, LangChain, GPT-4o-mini | `backend/agent/chatbot_agent.py` |
| Vector DB | FAISS, OpenAI text-embedding-3-small | `backend/config/vectorDB/vectorStore.py` |
| Database | PostgreSQL 15 (asyncpg), SQLAlchemy Async | `backend/config/database.py` |
| Cache/Session | Redis 7 (redis.asyncio) | `backend/config/redis_client.py` |
| Infra | Docker Compose | `docker-compose.yml` |

---

## 2. 폴더 구조 맵 (절대 변경 금지 계층)

```
data_agent/
├── CLAUDE.md                          ← 이 파일 (AI Harness 루트 명세)
├── .agent_rules/                      ← 도메인별 상세 규칙
│   ├── backend.md
│   ├── frontend.md
│   └── ai_agent.md
├── backend/
│   ├── __init__.py
│   ├── main.py                        ← FastAPI 앱 진입점, startup에서 벡터DB 초기화
│   ├── agent/
│   │   ├── __init__.py                ← get_agent_response, set_global_vector_store 공개
│   │   ├── chatbot_agent.py           ← ReAct Agent (build_agent, SYSTEM_PROMPTS)
│   │   └── tools/
│   │       ├── vector_search_tool.py  ← FAISS 검색 + GPT 답변 (StructuredTool)
│   │       └── tavily_search_tool.py  ← Tavily 웹 검색 (StructuredTool)
│   ├── api/
│   │   └── auth.py                    ← /auth/* 라우터 + get_current_user 디펜던시
│   ├── config/
│   │   ├── database.py                ← create_async_engine, AsyncSessionLocal, get_db
│   │   ├── redis_client.py            ← redis.asyncio from_url, get_redis
│   │   └── vectorDB/
│   │       ├── vectorStore.py         ← VectorStore 클래스 (638줄, 핵심 모듈)
│   │       ├── embedded/              ← 원본 PDF 파일 보관
│   │       └── vector_db/             ← FAISS 인덱스 (index.faiss + index.pkl)
│   ├── models/
│   │   ├── student.py                 ← Student ORM (Base = declarative_base())
│   │   └── user.py
│   └── services/
│       ├── auth_service.py            ← JWT 생성/검증, base64 비밀번호 인코딩
│       ├── student_service.py         ← get_student_by_email/id, create_student (async)
│       └── user_service.py
├── api/
│   └── mypage.py                      ← Mypage API (psycopg2 동기 방식 — 리팩터링 대상)
├── database/
│   ├── schema.sql                     ← DDL (course, student 테이블)
│   └── assign_courses.sql
├── frontend/
│   └── sch-landing-vue/src/
│       ├── api/
│       │   ├── client.ts              ← ApiClient 클래스 (토큰 관리, fetch 래핑)
│       │   └── authModal.js
│       ├── app/components/
│       │   ├── Header.vue             ← 전역 헤더
│       │   ├── Home.vue               ← 랜딩 페이지 (Hero, About, Departments 등 조합)
│       │   ├── Chatbot.vue            ← 플로팅 챗봇 UI
│       │   ├── ChatbotPage.vue        ← /chatbot 전용 페이지
│       │   ├── Mypage.vue             ← /mypage 학생 정보 + 수강과정
│       │   ├── Login.vue              ← 로그인 모달
│       │   └── Signup.vue             ← 회원가입 모달
│       ├── router.ts                  ← Vue Router (/, /chatbot, /mypage)
│       └── main.ts                    ← 앱 부트스트랩
├── rules/
│   ├── 개발규칙.md                     ← 사용자 의사결정 규칙
│   └── 실행계획.md                     ← 초기 아키텍처 설계 명세
├── docker-compose.yml                 ← PostgreSQL 15 + Redis 7
├── requirements.txt                   ← Python 의존성
├── .env                               ← 비밀키 (Git 제외)
└── .env.exmaple                       ← 환경변수 템플릿
```

---

## 3. 절대 불변 원칙 (Golden Rules)

### 3.1 비동기 I/O 강제
- **DB:** `create_async_engine` + `AsyncSession` + `asyncpg` 드라이버만 사용
- **Redis:** `redis.asyncio`의 `from_url()` + `decode_responses=True` 방식만 사용
- **금지:** `psycopg2` 동기 방식 신규 코드 작성 금지 (기존 `api/mypage.py`는 레거시로 분류)

### 3.2 JWT + Redis 세션 설계 (변경 금지)
```
Access Token:
  - 알고리즘: HS256 (JWT_ALGORITHM 환경변수)
  - 만료: 15분 (ACCESS_TOKEN_EXPIRE_MIN)
  - 클레임: { sub: user_id, email, jti: UUID, type: "access", iat, exp }
  - 로그아웃 시: Redis에 bl:{jti} 키로 블랙리스트 등록 (TTL = 잔여 만료 시간)

Refresh Token:
  - 알고리즘: HS256
  - 만료: 14일 (REFRESH_TOKEN_EXPIRE_DAYS)
  - 클레임: { sub: user_id, jti: UUID, type: "refresh", iat, exp }
  - 로그인 시: Redis에 rt:{user_id}:{jti} 키로 화이트리스트 저장 (TTL = 14일)
  - 로그아웃 시: DEL rt:{user_id}:{jti}

인가 미들웨어 (get_current_user):
  1. Authorization 헤더에서 Bearer 토큰 추출
  2. JWT 서명 검증 → type == "access" 확인
  3. Redis EXISTS bl:{jti} → 블랙리스트에 있으면 401
  4. DB에서 student 조회 → is_active == false이면 401
```

### 3.3 ReAct Agent 자율성 보장
- `create_react_agent(llm, tools)`로 생성된 에이전트가 `vector_search_tool`과 `tavily_search_tool` 중 어느 것을 사용할지 **LLM이 자율 판단**
- if-else 기반 강제 라우팅 금지 — Thought → Action → Observation 루프를 훼손하지 말 것

### 3.4 FAISS 임베딩 무결성
- 중복 임베딩 방지: `_already_indexed_source()` 로직에서 `docstore._dict`의 `metadata.source` 비교로 판단
- 증분 추가: 기존 인덱스에 `add_documents()`로 추가, `from_documents()`는 최초 생성 시에만 사용
- Windows 비ASCII 경로: `_make_faiss_path_safe()` 로직 유지 필수

### 3.5 개발 절차 규칙 (사용자 합의)
- `rules/개발규칙.md` 기반:
  1. **의사결정은 반드시 사용자에게 허가를 받고 진행**
  2. **개발 실행 전 실행계획을 반드시 먼저 보고하고 허가받고 진행**

---

## 4. 환경 변수 명세 (.env)

| 변수명 | 용도 | 기본값 | 필수 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API 인증 | — | ✅ |
| `TAVILY_API_KEY` | Tavily 웹 검색 API | — | ⚠️ (없으면 웹검색 비활성화) |
| `DATABASE_URL` | PostgreSQL 접속 (asyncpg) | `postgresql+asyncpg://appuser:apppass@localhost:5555/appdb` | ✅ |
| `REDIS_URL` | Redis 접속 | `redis://localhost:6379/0` | ✅ |
| `JWT_SECRET` | JWT 서명 비밀키 | — | ✅ |
| `JWT_ALGORITHM` | JWT 알고리즘 | `HS256` | ❌ |
| `ACCESS_TOKEN_EXPIRE_MIN` | AT 만료(분) | `15` | ❌ |
| `REFRESH_TOKEN_EXPIRE_DAYS` | RT 만료(일) | `14` | ❌ |
| `CHAT_MODEL` | LLM 모델명 | `gpt-4o-mini` | ❌ |
| `EMBEDDING_MODEL` | 임베딩 모델명 | `text-embedding-3-small` | ❌ |
| `CHUNK_SIZE` | 텍스트 청크 크기 | `512` | ❌ |
| `CHUNK_OVERLAP` | 청크 오버랩 | `50` | ❌ |
| `POSTGRES_DB` | Docker PostgreSQL DB명 | `appdb` | ❌ |
| `POSTGRES_USER` | Docker PostgreSQL 유저 | `appuser` | ❌ |
| `POSTGRES_PASSWORD` | Docker PostgreSQL 비밀번호 | `apppass` | ❌ |

---

## 5. 핵심 의존성 (변경 시 반드시 사용자 허가)

### Python (requirements.txt)
```
fastapi, uvicorn                          # 웹 서버
langchain, langchain-core, langchain-openai, langchain-community  # LLM 프레임워크
langgraph                                 # ReAct Agent (create_react_agent)
faiss-cpu                                 # 벡터 검색
pypdf                                     # PDF 로딩
watchdog                                  # PDF 파일 감시 (Watchdog Observer)
sqlalchemy[asyncio], asyncpg              # 비동기 ORM + DB 드라이버
redis                                     # Redis 비동기 클라이언트
pyjwt                                     # JWT 인코딩/디코딩
rich                                      # 로깅 마크다운 렌더링
```

### Frontend (package.json)
```
vue@3, typescript, tailwindcss, vue-router, axios
```

---

## 6. 금지 사항 (Strict Constraints)

1. **동기식 DB/Redis 코드 신규 작성 금지** — `psycopg2`, `redis.Redis()` (동기) 사용 불가
2. **JWT 블랙리스트 검증 우회 금지** — `get_current_user()`의 `EXISTS bl:{jti}` 단계를 생략하거나 무력화하지 말 것
3. **`requirements.txt` / `package.json` 무단 수정 금지** — 새 패키지 추가 시 반드시 사용자 보고 + 허가
4. **ORM Base 분리 금지** — `student.py`에서 `Base = declarative_base()` 선언, 모든 모델이 이 Base를 공유
5. **FAISS 인덱스 전체 재생성 남용 금지** — `from_documents()`는 `reset_db=True` 경우에만, 평시에는 `add_documents()` 사용
6. **프론트엔드 `any` 타입 사용 금지** — TypeScript 엄격 타입 준수
7. **`SYSTEM_PROMPTS` 딕셔너리 구조 변경 금지** — `educator`, `researcher`, `assistant` 3개 역할은 고정. 새 역할 추가는 가능하되 기존 삭제 불가
8. **`.env` 파일의 변수명 변경 금지** — 기존 코드가 해당 이름으로 참조 중

---

## 7. 도메인별 상세 규칙 참조

| 작업 영역 | 규칙 파일 | 핵심 내용 |
|-----------|-----------|-----------|
| FastAPI, DB, Redis, JWT | `.agent_rules/backend.md` | 라우터 구조, 세션 관리, 에러 코드, 서비스 레이어 패턴 |
| Vue 3, TypeScript, Tailwind | `.agent_rules/frontend.md` | ApiClient 사용법, 컴포넌트 설계, 토큰 흐름, 라우터 규칙 |
| LangGraph, FAISS, RAG | `.agent_rules/ai_agent.md` | ReAct 루프, VectorStore 클래스, 프롬프트 규칙, Watchdog |

---

## 8. 실행 방법

```bash
# 1. 인프라 (PostgreSQL + Redis)
docker-compose up -d

# 2. Python 의존성
pip install -r requirements.txt

# 3. 백엔드 서버
uvicorn backend.main:app --reload

# 4. 프론트엔드 (별도 터미널)
cd frontend/sch-landing-vue
npm install
npm run dev
```
