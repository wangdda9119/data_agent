from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from .agent import get_agent_response, set_global_vector_store
from .config.vectorDB.vectorStore import get_vector_store

# .env 파일 로드 (서버 시작 시)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI()

# 전역 벡터 스토어 인스턴스 (모든 중단 초기화 성공)
global_vector_store = None

# CORS 설정 (필요시 원하는 도메인만 허용하도록 수정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (프로덕션에서는 특정 도메인만 허용)
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


class QueryRequest(BaseModel):
    """질문 요청 모델"""
    query: str


class QueryResponse(BaseModel):
    """응답 모델"""
    answer: str
    status: str = "success"


@app.get("/", response_class=HTMLResponse)
async def root():
    """루트 경로 - HTML 페이지 반환"""
    html_path = Path(__file__).parent.parent / "frontend" / "templates" / "index.html"
    return html_path.read_text(encoding="utf-8")


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
