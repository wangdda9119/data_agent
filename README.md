# 순천향대학교 AI 챗봇 서비스

> PDF 기반 RAG(Retrieval-Augmented Generation) 아키텍처와 JWT 인증 시스템을 결합한 대학교 AI 어시스턴트

---

## 프로젝트 개요

순천향대학교의 학사 정보(수강신청, 셔틀버스, 등록금, 논문 작성 등)를 PDF로 벡터화하여 저장하고,  
학생이 질문하면 AI가 관련 문서를 검색해 정확한 답변을 제공하는 서비스입니다.

- 개발 기간: 2024
- 개발 인원: 개인 프로젝트

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| Backend | FastAPI, Python, Uvicorn |
| AI / LLM | LangGraph, LangChain, OpenAI GPT-4o-mini |
| Vector DB | FAISS, OpenAI Embeddings (text-embedding-3-small) |
| Web Search | Tavily Search API |
| Database | PostgreSQL 15, SQLAlchemy (async + asyncpg) |
| Cache | Redis 7 (Refresh Token 저장, Access Token 블랙리스트) |
| Auth | JWT (PyJWT), Access Token 15분 / Refresh Token 14일 |
| Frontend | Vue 3, TypeScript, Axios, Vue Router, Tailwind CSS |
| Infra | Docker, Docker Compose |
| Monitoring | Watchdog (PDF 파일 감시), Rich (로깅) |

---

## 시스템 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                     Vue 3 SPA (Frontend)                     │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Login   │  │  Signup  │  │ Chatbot  │  │  Mypage    │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
│       │              │             │               │         │
│       └──────────────┴─────────────┴───────────────┘         │
│                         ApiClient (client.ts)                │
│              localStorage: access_token / refresh_token      │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTP REST API
┌──────────────────────────────▼───────────────────────────────┐
│                      FastAPI Server                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                   Auth Router (/auth)                │    │
│  │  POST /signup  →  이메일 중복 확인 → student 생성    │    │
│  │  POST /login   →  비밀번호 검증 → AT + RT 발급       │    │
│  │  POST /refresh →  Redis RT 확인 → 새 AT 발급         │    │
│  │  POST /logout  →  AT 블랙리스트 등록 + RT 삭제       │    │
│  │  GET  /me      →  AT 검증 → 사용자 정보 반환         │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │               Chat Router (POST /api/chat)           │    │
│  │                                                      │    │
│  │   query → get_agent_response()                       │    │
│  │              │                                       │    │
│  │              ▼                                       │    │
│  │        build_agent()                                 │    │
│  │     LangGraph ReAct Agent                            │    │
│  │     (GPT-4o-mini + tools)                            │    │
│  │              │                                       │    │
│  │    ┌─────────┴──────────┐                            │    │
│  │    ▼                    ▼                            │    │
│  │  vector_search_tool   tavily_search_tool             │    │
│  │  FAISS 유사도 검색     실시간 웹 검색                 │    │
│  │  → LLM 답변 생성       → 결과 반환                   │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Mypage Router (GET /mypage)             │    │
│  │  JWT 검증 → student LEFT JOIN course → 정보 반환     │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                         Data Layer                           │
│                                                              │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐  │
│  │  PostgreSQL 15  │  │    Redis 7        │  │   FAISS    │  │
│  │                 │  │                  │  │            │  │
│  │  student 테이블 │  │  rt:{uid}:{jti}  │  │ index.faiss│  │
│  │  course 테이블  │  │  bl:{jti}        │  │ index.pkl  │  │
│  │  (async ORM)    │  │  (TTL 자동 만료) │  │            │  │
│  └─────────────────┘  └──────────────────┘  └────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## RAG 파이프라인 상세

### 1. PDF 전처리 및 임베딩

```
[PDF 문서 5종 - embedded/ 폴더]
  셔틀버스 운행시간표 / 등록금 수납 안내
  수강신청 안내 / 논문 작성 요령 / 학교 소개
        │
        ▼
[PyPDFLoader] - 페이지 단위 로드
        │
        ▼
[텍스트 전처리 - _clean_text() + _remove_stopwords()]
  ① unicodedata.normalize("NFKC")  → 유니코드 정규화
  ② re.sub 노이즈 문자 제거        → 제어문자, 이스케이프 시퀀스
  ③ 한국어 불용어 제거             → 은/는/이/가/을/를 등 30종
  ④ 영어 불용어 제거               → a/an/the/and 등 15종
  ⑤ 20자 미만 청크 필터링          → 의미 없는 단편 제거
        │
        ▼
[RecursiveCharacterTextSplitter]
  chunk_size=512, chunk_overlap=50
        │
        ▼
[OpenAI text-embedding-3-small]
  각 청크를 벡터로 변환
        │
        ▼
[FAISS.from_documents() / add_documents()]
  index.faiss + index.pkl 로컬 저장
```

### 2. 중복 임베딩 방지

새 PDF가 추가될 때 FAISS docstore의 metadata.source를 순회하여  
이미 인덱싱된 파일 경로와 비교합니다. 동일한 source가 존재하면 임베딩을 건너뜁니다.

```python
# _already_indexed_source() 핵심 로직
for _, doc in docstore._dict.items():
    if doc.metadata.get("source") == source_path:
        return True  # 이미 처리됨 → 스킵
```

### 3. 검색 및 답변 생성

```
사용자 질문
        │
        ▼
[FAISS.similarity_search_with_score(query, k=2)]
  코사인 유사도 기반 top-2 청크 반환
        │
        ▼
[build_context()]
  출처(파일명, 페이지) + 본문 조합
  최대 8,000자로 컨텍스트 구성
        │
        ▼
[GPT-4o-mini]
  "제공된 컨텍스트에 근거가 있을 때만 답변"
  출처 명시 강제 / 추측 금지 프롬프트
        │
        ▼
최종 답변 반환
```

### 4. PDF 자동 감지 (Watchdog)

서버 시작 시 `embedded/` 폴더를 Watchdog Observer로 감시합니다.  
새 PDF 파일이 추가되거나 이동되면 `on_created` / `on_moved` 이벤트가 발생하고,  
파일이 완전히 저장될 때까지 0.2초 간격으로 크기를 체크한 뒤(stable 3회 연속 확인) 자동 임베딩합니다.

---

## JWT 인증 및 Redis 캐시 구조

### 토큰 설계

| 항목 | Access Token | Refresh Token |
|------|-------------|---------------|
| 유효기간 | 15분 | 14일 |
| 저장 위치 | 클라이언트 localStorage | 클라이언트 localStorage + Redis |
| Redis 키 | `bl:{jti}` (블랙리스트) | `rt:{user_id}:{jti}` |
| Redis TTL | 토큰 잔여 만료 시간 | 14일 |

### Redis 활용 상세

```
[Refresh Token 저장]
  로그인 성공 시
  → SETEX rt:{user_id}:{jti}  {14일 TTL}  "1"
  → Redis에 RT 존재 = 유효한 세션

[Access Token 블랙리스트]
  로그아웃 시
  → SETEX bl:{jti}  {AT 잔여 만료 시간}  "1"
  → 이후 해당 AT로 요청 시 Redis EXISTS 확인 → 401 반환
  → TTL 만료 시 자동 삭제 (메모리 낭비 없음)

[토큰 갱신]
  → Redis EXISTS rt:{user_id}:{jti} 확인
  → 존재하면 새 AT 발급 (RT는 그대로 유지)
  → 존재하지 않으면 401 (로그아웃된 세션)

[로그아웃]
  → AT → bl:{jti} 등록
  → RT → rt:{user_id}:{jti} DEL
```

### 인증 흐름

```
[회원가입 POST /auth/signup]
  이메일 중복 확인 → base64 인코딩 비밀번호 저장
  → student 테이블 INSERT

[로그인 POST /auth/login]
  student 조회 → is_active 확인 → 비밀번호 검증
  → uuid4() JTI 생성
  → Access Token (HS256, 15분) 발급
  → Refresh Token (HS256, 14일) 발급
  → Redis SETEX rt:{user_id}:{jti}

[API 요청]
  Authorization: Bearer {access_token}
  → JWT 서명 검증 (HS256)
  → type == "access" 확인
  → Redis EXISTS bl:{jti} → 블랙리스트 확인
  → student 조회 + is_active 확인
  → 통과 시 요청 처리

[토큰 갱신 POST /auth/refresh]
  → RT 서명 검증 + type == "refresh" 확인
  → Redis EXISTS rt:{user_id}:{jti}
  → 새 Access Token 발급

[로그아웃 POST /auth/logout]
  → AT JTI → Redis bl:{jti} 등록 (잔여 TTL)
  → RT → Redis rt:{user_id}:{jti} DEL
```

---

## ReAct Agent 동작 방식

LangGraph의 `create_react_agent`를 사용해 LLM이 스스로 도구를 선택하고 실행하는 루프를 구성합니다.

```
사용자 질문 입력
        │
        ▼
[SystemMessage] - 역할 정의 (educator / researcher / assistant)
[HumanMessage]  - 사용자 질문
        │
        ▼
[GPT-4o-mini] - 어떤 도구를 쓸지 판단
        │
   ┌────┴────┐
   ▼         ▼
vector_    tavily_
search     search
_tool      _tool
   │         │
   └────┬────┘
        ▼
[Observation] - 도구 실행 결과
        │
        ▼
[GPT-4o-mini] - 결과를 보고 추가 도구 호출 or 최종 답변 결정
        │
        ▼
messages[-1].content → 최종 답변 반환
```

두 도구의 역할 분리:
- `vector_search_tool`: FAISS에서 학교 공식 문서 검색 → 컨텍스트 기반 답변 (출처 명시)
- `tavily_search_tool`: 벡터DB에 없는 최신 정보나 외부 정보 실시간 웹 검색

---

## DB 스키마

```sql
CREATE TABLE course (
    id          SERIAL PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE student (
    id          BIGSERIAL PRIMARY KEY,
    email       VARCHAR(255) UNIQUE NOT NULL,
    password    VARCHAR NOT NULL,        -- base64 인코딩
    nickname    VARCHAR(100),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    course_id   INTEGER REFERENCES course(id) ON DELETE SET NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

마이페이지 조회 쿼리 (LEFT JOIN으로 course 미등록 학생도 조회):

```sql
SELECT s.email, s.nickname, c.course_name
FROM student s
LEFT JOIN course c ON s.course_id = c.id
WHERE s.id = $1;
```

---

## 프로젝트 구조

```
data_agent/
├── backend/
│   ├── main.py                        # FastAPI 앱 진입점, startup 시 벡터DB 초기화
│   ├── agent/
│   │   ├── chatbot_agent.py           # ReAct Agent 빌드, 역할별 시스템 프롬프트
│   │   └── tools/
│   │       ├── vector_search_tool.py  # FAISS 검색 + GPT-4o-mini 답변 생성
│   │       └── tavily_search_tool.py  # Tavily 실시간 웹 검색
│   ├── api/
│   │   └── auth.py                    # 인증 라우터 (signup/login/refresh/logout/me)
│   ├── config/
│   │   ├── database.py                # SQLAlchemy async 엔진 + 세션
│   │   ├── redis_client.py            # redis.asyncio 클라이언트
│   │   └── vectorDB/
│   │       ├── vectorStore.py         # VectorStore 클래스 (임베딩/검색/Watchdog)
│   │       ├── embedded/              # 원본 PDF 파일 (5종)
│   │       └── vector_db/             # FAISS 인덱스 (index.faiss + index.pkl)
│   ├── models/
│   │   └── student.py                 # SQLAlchemy ORM 모델
│   └── services/
│       ├── auth_service.py            # JWT 생성/검증, 비밀번호 인코딩
│       └── student_service.py         # 학생 CRUD (async)
├── api/
│   └── mypage.py                      # 마이페이지 API (psycopg2 직접 쿼리)
├── database/
│   ├── schema.sql                     # 테이블 생성 DDL
│   └── assign_courses.sql             # 학생-코스 배정 SQL
├── frontend/
│   └── sch-landing-vue/
│       └── src/
│           ├── api/
│           │   └── client.ts          # ApiClient 클래스 (토큰 관리 + API 호출)
│           ├── app/components/
│           │   ├── Chatbot.vue        # 플로팅 챗봇 UI (빠른 질문 버튼 포함)
│           │   ├── Mypage.vue         # 학생 정보 + 수강 과정 조회
│           │   ├── Login.vue          # 로그인 모달
│           │   └── Signup.vue         # 회원가입 모달
│           └── router.ts              # Vue Router (/, /chatbot, /mypage)
├── docker-compose.yml                 # PostgreSQL 15 + Redis 7 컨테이너
└── requirements.txt
```

---

## 실행 방법

**1. 인프라 실행**
```bash
docker-compose up -d
```

**2. 패키지 설치**
```bash
pip install -r requirements.txt
```

**3. 환경변수 설정 (.env)**
```
OPENAI_API_KEY=<your_openai_api_key>
TAVILY_API_KEY=<your_tavily_api_key>
DATABASE_URL=postgresql+asyncpg://appuser:apppass@localhost:5555/appdb
JWT_SECRET=<your_jwt_secret>
REDIS_URL=redis://localhost:6379/0
```

**4. 서버 실행**
```bash
uvicorn backend.main:app --reload
```

---

## 핵심 구현 포인트

**ReAct Agent 루프**  
LangGraph `create_react_agent`로 LLM이 Thought → Action → Observation 사이클을 반복하며 스스로 도구를 선택하고 최종 답변을 생성합니다. 벡터DB 검색과 웹 검색을 상황에 따라 조합합니다.

**Redis 기반 토큰 무효화**  
JWT는 stateless라 서버에서 강제 만료가 불가능합니다. 이를 해결하기 위해 로그아웃 시 Access Token의 JTI를 Redis 블랙리스트에 등록하고, 모든 API 요청마다 `EXISTS bl:{jti}`를 확인합니다. TTL을 토큰 잔여 만료 시간으로 설정해 Redis 메모리를 자동 정리합니다.

**PDF 자동 감지 및 증분 임베딩**  
Watchdog Observer가 `embedded/` 폴더를 실시간 감시합니다. 새 파일 감지 시 파일 크기가 3회 연속 동일할 때까지 대기(쓰기 완료 확인)한 뒤 임베딩을 실행합니다. 기존 FAISS 인덱스에 `add_documents()`로 추가하므로 전체 재임베딩 없이 증분 업데이트가 가능합니다.

**중복 임베딩 방지**  
FAISS docstore의 `_dict`를 순회해 `metadata.source`(절대 경로)가 동일한 문서가 이미 존재하면 임베딩을 건너뜁니다. 서버 재시작 후에도 중복 처리가 발생하지 않습니다.

**Windows 비ASCII 경로 안전 처리**  
한글 폴더명 경로에서 FAISS `save_local()`이 실패하는 문제를 해결했습니다. 경로 문자열을 ASCII 인코딩 시도로 검사하고, 비ASCII 경로일 경우 자동으로 `vector_db`(ASCII) 경로로 대체합니다.

**SQLAlchemy 비동기 처리**  
`asyncpg` 드라이버와 `AsyncSession`을 사용해 DB I/O가 FastAPI 이벤트 루프를 블로킹하지 않도록 구성했습니다. `async_sessionmaker`로 세션을 관리하고 `Depends(get_db)`로 라우터에 주입합니다.
