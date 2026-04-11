# AI Agent / RAG Harness Rules

> LangGraph ReAct Agent, FAISS VectorStore, Tavily 웹 검색, Watchdog 파일 감시 관련 코드 수정 시 이 문서를 반드시 준수합니다.

---

## 1. 기술 스택 고정

| 항목 | 구현체 | 핵심 파일 |
|------|--------|-----------|
| Agent Framework | LangGraph `create_react_agent` | `backend/agent/chatbot_agent.py` |
| LLM | OpenAI `gpt-4o-mini` (ChatOpenAI, temperature=0.1) | |
| Vector DB | FAISS (`faiss-cpu`) | `backend/config/vectorDB/vectorStore.py` |
| Embedding | OpenAI `text-embedding-3-small` | |
| 텍스트 분할 | `RecursiveCharacterTextSplitter` (chunk_size=512, overlap=50) | |
| PDF 로딩 | `PyPDFLoader` | |
| 웹 검색 | Tavily Search API (`TavilySearchResults`) | `backend/agent/tools/tavily_search_tool.py` |
| 파일 감시 | Watchdog (`Observer` + `FileSystemEventHandler`) | |
| 로깅 | Rich (`RichHandler` + `FileHandler`) | `vectorstore.log` |

---

## 2. 파일별 책임 분리

### 2.1 `chatbot_agent.py` — ReAct Agent 빌드 (216줄)

**전역 상태 관리:**
```python
_global_vector_store = None  # main.py startup에서 set_global_vector_store(vs)로 설정

def set_global_vector_store(vs):
    """main.py → agent/__init__.py → chatbot_agent.py → vector_search_tool.py 체인"""
    global _global_vector_store
    _global_vector_store = vs
    vector_tool_set_vs(vs)  # tools/vector_search_tool.py에도 전파
```
- **이 체인을 끊으면 벡터 검색이 작동하지 않음** — 절대 수정 금지

**SYSTEM_PROMPTS 딕셔너리 (3개 역할):**
```python
SYSTEM_PROMPTS = {
    "educator": "...",    # 교육 AI — 벡터DB 우선, 출처 명시
    "researcher": "...",  # 연구 AI — 정확성, 한계 명시
    "assistant": "...",   # 일반 AI — 친절, 순천향대 관점
}
```
- **기존 3개 키 삭제 금지, 내용 변경 시 사용자 허가 필요**
- 새 역할 추가는 자유 (예: `"counselor"`, `"faq"`)
- 모든 프롬프트에 공통으로 포함된 핵심 지시:
  - "순천향대학교"를 기본 맥락으로 답변
  - 벡터DB 도구 우선 사용
  - 웹 검색은 보완적 사용

**build_agent(role):**
```python
def build_agent(role="assistant"):
    llm = ChatOpenAI(
        model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    tools = [vector_search_tool, tavily_search_tool]
    agent = create_react_agent(llm, tools)  # ← LangGraph 핵심
    agent._role = role
    return agent
```
- **temperature=0.1** — 일관성 높은 응답 보장, 변경 시 사용자 허가
- **tools 리스트:** `[vector_search_tool, tavily_search_tool]` — 순서·구성 변경 금지
- **`create_react_agent`의 자율성:** LLM이 Thought → Action → Observation 사이클에서 어느 도구를 쓸지 스스로 판단. if-else 기반 강제 라우팅 금지

**get_agent_response(query, role, chat_history):**
```python
# 실행 흐름:
1. build_agent(role) 호출
2. SystemMessage(role별 프롬프트) + HumanMessage(query) 구성
3. agent.invoke({"messages": messages})
4. result["messages"][-1].content 반환
```
- **스트리밍 버전:** `get_agent_response_streaming()` — `agent.stream()` 사용, yield 방식

### 2.2 `tools/vector_search_tool.py` — FAISS 벡터 검색 도구 (129줄)

**전역 벡터 스토어:**
```python
_global_vector_store = None  # chatbot_agent.py에서 set_global_vector_store()로 주입
```

**build_context(search_results, max_chars=8000):**
```python
# 검색 결과 → 컨텍스트 문자열 변환
# 각 청크: "[출처: 파일명, 페이지: N]\n본문"
# 구분자: "\n\n---\n\n"
# max_chars(8000) 초과 시 이후 청크 무시
# 반환: (context_str, avg_score)
```
- **max_chars=8000** 변경 시 GPT 토큰 제한 고려 필요

**search_and_answer(question):**
```python
# 실행 흐름:
1. vs.search(question, k=2)  ← FAISS 유사도 검색 (top-2)
2. build_context() → 컨텍스트 구성
3. MIN_CONTEXT_LENGTH = 50 → 50자 미만이면 "정보 부족" 반환
4. ChatOpenAI(gpt-4o-mini, temp=0.1) + 프롬프트 → 답변 생성
```

**Anti-Hallucination 프롬프트 (절대 수정 금지):**
```
핵심 규칙:
1. 제공된 컨텍스트에 명확한 근거가 있을 때만 답변하세요
2. 컨텍스트가 없거나 관련성이 낮으면 "정보를 찾을 수 없습니다"
3. 추측하거나 일반적인 지식으로 답변하지 마세요
4. 답변할 때는 반드시 출처를 명시하세요
5. 불확실하면 답변하지 마세요
6. 답변은 간결하고 정확하게 작성하세요
```

**StructuredTool 등록:**
```python
vector_search_tool = StructuredTool.from_function(
    func=search_and_answer,
    name="vector_search",
    description="벡터 데이터베이스에서 관련 문서를 검색하고..."
)
```
- **name="vector_search"** — 에이전트가 이 이름으로 도구 호출, 변경 금지

### 2.3 `tools/tavily_search_tool.py` — 웹 검색 도구 (80줄)

```python
tavily_search = TavilySearchResults(
    api_key=api_key,
    max_results=2,          # 웹 결과 최대 2개
    include_answer=True,    # Tavily 자체 답변 포함
    include_raw_content=False
)
```

**Graceful Degradation:**
```python
if not os.getenv("TAVILY_API_KEY"):
    tavily_search_tool = None  # API 키 없으면 도구 비활성화
```
- 이 패턴으로 TAVILY_API_KEY가 없어도 서버 자체는 정상 기동

**StructuredTool 등록:**
```python
tavily_search_tool = StructuredTool.from_function(
    func=simple_web_search,
    name="tavily_search",
    description="웹에서 Tavily Search를 사용하여 관련 정보를 검색합니다..."
)
```
- **name="tavily_search"** — 변경 금지

### 2.4 `vectorStore.py` — VectorStore 클래스 (638줄, 핵심 모듈)

**초기화 파라미터 (환경변수 + 기본값):**
```python
VectorStore(
    embedding_model_name = EMBEDDING_MODEL or "text-embedding-3-small"
    chunk_size           = CHUNK_SIZE or 512
    chunk_overlap        = CHUNK_OVERLAP or 50
    vector_db_path       = VECTOR_DB_PATH or "vector_db"  → _make_faiss_path_safe() 적용
    embedded_folder      = EMBEDDED_FOLDER or "embedded"
    use_stopwords        = True
)
```

**불용어 세트 (45종):**
- 한국어 30종: `은/는/이/가/을/를/에/의/와/과/도/로/으로/에서/에게/한테/께/및/또는/그리고/또한/등/수/좀/더/때/것/거/때문/관련/대해/대한`
- 영어 15종: `a/an/the/and/or/to/of/in/on/for/with/as/at/by/is/are/was/were/be/been/it/this/that/these/those`

**텍스트 전처리 파이프라인 (_preprocess_documents):**
```
1. _clean_text():
   ① unicodedata.normalize("NFKC")     → 유니코드 정규화
   ② re.sub([\r\n\t]+, " ")            → 줄바꿈/탭 제거
   ③ re.sub([\x00-\x08\x0b-\x1f\x7f])  → 제어문자 제거
   ④ re.sub(\\[nrtqvf])                → 이스케이프 시퀀스 제거
   ⑤ re.sub(\s{2,}, " ")               → 다중 공백 → 단일 공백

2. _remove_stopwords():
   공백 기준 토큰화 → stopwords 세트에 포함된 토큰 제거

3. 20자 미만 청크 필터링:
   len(content) < 20 → skip (의미 없는 단편)
```

**FAISS 인덱스 관리:**
```python
# 저장: index.faiss + index.pkl (vector_db_path 디렉토리)
def _save_vector_store():
    Path(self.vector_db_path).mkdir(parents=True, exist_ok=True)
    self.vector_store.save_local(self.vector_db_path)

# 로드
def load_existing_vector_store():
    self.vector_store = FAISS.load_local(
        self.vector_db_path, self.embeddings,
        allow_dangerous_deserialization=True  # ← 반드시 True
    )

# 검색
def search(query, k=8, top_k=None):
    docs_and_scores = self.vector_store.similarity_search_with_score(query, k=final_k)
    # 반환: [{"rank", "score", "content", "metadata"}, ...]
```

**중복 임베딩 방지 (`_already_indexed_source`):**
```python
def _already_indexed_source(self, source_path: str) -> bool:
    for _, doc in docstore._dict.items():
        if doc.metadata.get("source") == source_path:
            return True  # 이미 인덱싱됨 → 스킵
    return False
```
- **이 로직을 삭제/우회하면 서버 재시작 시마다 전체 PDF가 중복 임베딩됨**

**증분 업데이트 규칙:**
```python
# 최초 생성 (vector_store가 None일 때만):
self.vector_store = FAISS.from_documents(chunks, self.embeddings)

# 이후 추가 (기존 인덱스에 append):
self.vector_store.add_documents(chunks)
```
- **`from_documents()`는 최초 1회 또는 명시적 `reset_db=True` 시에만 사용**
- **평시에는 반드시 `add_documents()`로 증분 추가**

**Watchdog 파일 감시:**
```python
class PDFWatcher(FileSystemEventHandler):
    on_created(event):  # .pdf 파일 생성 시 → process_file()
    on_moved(event):    # .pdf 파일 이동 시 → process_file()

def start_watching(recursive=True):
    # 1. 기존 embedded/ 폴더 전체 임베딩
    # 2. Observer로 실시간 감시 시작

def _wait_until_file_stable(path, timeout_sec=30):
    # 파일 크기가 3회 연속 동일할 때까지 0.2초 간격 체크
    # → 파일 쓰기가 완료된 것으로 판단
```
- **0.2초 간격, 3회 연속 stable** — 이 파라미터 변경 시 대용량 PDF 업로드에 영향

**Windows 비ASCII 경로 안전 처리:**
```python
def _make_faiss_path_safe(path_str):
    # path_str.encode("ascii") 시도
    # 실패 시 → "vector_db" (ASCII 안전 경로)로 대체
```
- FAISS의 `save_local()`이 한글 경로에서 실패하는 문제 해결

---

## 3. 에이전트 호출 체인 (전체 흐름)

```
[서버 시작]
  backend/main.py::startup_event()
    → get_vector_store() → VectorStore() 인스턴스 생성
    → vs.load_existing_vector_store() 또는 vs.create_new_embeddings()
    → set_global_vector_store(vs)
      → chatbot_agent.py::_global_vector_store 설정
      → vector_search_tool.py::_global_vector_store 설정

[사용자 질문]
  POST /api/chat { "query": "..." }
    → get_agent_response(query)
      → build_agent(role="assistant")
        → ChatOpenAI(gpt-4o-mini, temp=0.1)
        → create_react_agent(llm, [vector_search_tool, tavily_search_tool])
      → agent.invoke({ "messages": [SystemMessage, HumanMessage] })
        → LLM 자율 판단:
          → vector_search → search_and_answer(question)
              → vs.search(query, k=2)
              → build_context() → 프롬프트 → GPT 답변
          → tavily_search → simple_web_search(query)
              → TavilySearchResults.invoke(query)
      → result["messages"][-1].content → 반환
```

---

## 4. 코드 수정 시 체크리스트

에이전트 로직 수정 시:
- [ ] `create_react_agent`의 tools 인자가 `[vector_search_tool, tavily_search_tool]` 형태를 유지하는가?
- [ ] SYSTEM_PROMPTS의 기존 3개 역할(educator, researcher, assistant)을 삭제하지 않았는가?
- [ ] `set_global_vector_store` 체인(main→agent→tools)이 온전한가?
- [ ] temperature 값을 변경했다면 사용자에게 보고했는가?

벡터 검색 수정 시:
- [ ] Anti-Hallucination 프롬프트의 6가지 핵심 규칙을 유지했는가?
- [ ] `build_context()`의 출처 포맷 `[출처: 파일명, 페이지: N]`을 유지했는가?
- [ ] `search_and_answer`의 k=2 (top-2 검색)를 변경했다면 사용자에게 보고했는가?

VectorStore 수정 시:
- [ ] `_already_indexed_source()` 중복 방지 로직이 온전한가?
- [ ] `_wait_until_file_stable()`의 3회 연속 체크 로직이 유지되는가?
- [ ] `_make_faiss_path_safe()`의 비ASCII 경로 처리가 유지되는가?
- [ ] `allow_dangerous_deserialization=True`가 `load_local()`에 포함되어 있는가?
- [ ] 증분 업데이트 시 `add_documents()`를 사용하고 불필요한 `from_documents()`를 호출하지 않는가?

새 도구 추가 시:
- [ ] `StructuredTool.from_function()`으로 래핑했는가?
- [ ] `build_agent()`의 `tools` 리스트에 추가했는가?
- [ ] TAVILY처럼 API 키 미설정 시 graceful degradation을 구현했는가?
