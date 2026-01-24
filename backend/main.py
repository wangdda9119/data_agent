from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from .agent import get_agent_response

# .env 파일 로드 (서버 시작 시)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI()

# CORS 설정 (필요시 원하는 도메인만 허용하도록 수정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (프로덕션에서는 특정 도메인만 허용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
