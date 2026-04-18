from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os
from .agent import get_agent_response, set_global_vector_store
from .config.vectorDB.vectorStore import get_vector_store
from .api.auth import router as auth_router

# .env 파일 로드 (서버 시작 시)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI()

# 전역 벡터 스토어 인스턴스 (모든 중단 초기화 성공)
global_vector_store = None

# CORS 설정 (환경변수로 제어)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서버 시작 시 벡터DB 초기화
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 벡터DB를 초기화합니다."""
    global global_vector_store
    try:
        vs = get_vector_store()
        vectordb_path = Path(__file__).parent / "config" / "vectorDB"
        vector_db_path = vectordb_path / "vector_db"
        embedded_folder = vectordb_path / "embedded"
        
        vs.vector_db_path = str(vector_db_path)
        vs.embedded_folder = str(embedded_folder)
        
        # index.faiss가 존재하면 로드, 없으면 생성
        index_path = vector_db_path / "index.faiss"
        if index_path.exists():
            vs.load_existing_vector_store()
        else:
            vs.create_new_embeddings(str(embedded_folder), reset_db=True)
        
        # 전역 벡터 스토어로 등록
        global_vector_store = vs
        set_global_vector_store(vs)
        
        print("✓ 벡터DB 초기화 완료")
    except Exception as e:
        print(f"✗ 벡터DB 초기화 실패: {str(e)}")

# 라우터 등록 (SPA catch-all보다 먼저 등록해야 함)
app.include_router(auth_router)


class QueryRequest(BaseModel):
    """질문 요청 모델"""
    query: str


class QueryResponse(BaseModel):
    """응답 모델"""
    answer: str
    status: str = "success"


@app.post("/api/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """
    ReAct Agent를 사용하여 사용자 질문에 답변합니다.
    
    Args:
        request: 사용자 질문이 포함된 요청 (QueryRequest)
    
    Returns:
        QueryResponse: 생성된 답변과 상태 정보
    """
    try:
        answer = get_agent_response(request.query)
        return QueryResponse(answer=answer, status="success")
    except Exception as e:
        return QueryResponse(
            answer=f"오류가 발생했습니다: {str(e)}",
            status="error"
        )


# ── Vue 빌드 정적 파일 서빙 (운영 환경) ──
VUE_DIST = Path(__file__).parent.parent / "frontend" / "sch-landing-vue" / "dist"

if VUE_DIST.exists():
    # assets 디렉토리가 있으면 정적 파일 마운트
    assets_dir = VUE_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """SPA fallback — Vue Router가 처리할 경로는 index.html 반환"""
        # 요청된 경로에 실제 파일이 있으면 해당 파일 반환
        file_path = VUE_DIST / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        # 그 외 모든 경로는 index.html 반환 (Vue Router가 처리)
        return FileResponse(str(VUE_DIST / "index.html"))
else:
    # Vue 빌드가 없으면 기존 템플릿 HTML 반환 (개발 환경)
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """루트 경로 - HTML 페이지 반환"""
        html_path = Path(__file__).parent.parent / "frontend" / "templates" / "index.html"
        if html_path.exists():
            return html_path.read_text(encoding="utf-8")
        return HTMLResponse("<h1>순천향대 AI 챗봇 서비스</h1><p>프론트엔드 빌드가 필요합니다.</p>")
