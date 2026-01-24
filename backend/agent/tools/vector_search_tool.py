"""
벡터DB 검색 및 LLM 답변 생성 Tool
"""
import os
from pathlib import Path
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from ...config.vectorDB.vectorStore import get_vector_store


def build_context(search_results, max_chars: int = 8000) -> tuple[str, float]:
    """컨텍스트 구성 및 관련성 점수 계산"""
    if not search_results:
        return "", 0.0
    
    parts = []
    total = 0
    relevance_scores = []
    
    for result in search_results:
        src = result["metadata"].get("file_name", "unknown")
        page = result["metadata"].get("page", "?")
        text = result["content"].strip()
        score = result.get("score", 0.0)
        
        relevance_scores.append(score)
        block = f"[출처: {src}, 페이지: {page}]\n{text}"
        
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
    
    context = "\n\n---\n\n".join(parts)
    avg_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    return context, avg_score


def search_and_answer(question: str) -> str:
    """
    벡터DB에서 관련 문서를 검색하고 LLM을 사용하여 답변을 생성합니다.
    
    Args:
        question: 사용자의 질문
    
    Returns:
        생성된 답변 문자열
    """
    # VectorStore 초기화 및 경로 설정
    vs = get_vector_store()
    vectordb_path = Path(__file__).parent.parent.parent / "config" / "vectorDB"
    vector_db_path = vectordb_path / "vector_db"
    embedded_folder = vectordb_path / "embedded"
    
    vs.vector_db_path = str(vector_db_path)
    vs.embedded_folder = str(embedded_folder)
    
    # 벡터DB가 없으면 생성
    stats = vs.get_stats()
    if not stats.get("loaded", False):
        vs.create_new_embeddings(str(embedded_folder), reset_db=True)
        stats = vs.get_stats()
    
    # 벡터DB에서 관련 문서 검색
    search_results = vs.search(question, k=10)
    
    if not search_results:
        return "제공된 문서에서 해당 질문에 대한 정보를 찾을 수 없습니다."
    
    # 컨텍스트 구성
    context, avg_score = build_context(search_results)
    
    # 관련성 임계값 설정
    MIN_CONTEXT_LENGTH = 50
    
    if not context or len(context) < MIN_CONTEXT_LENGTH:
        return "제공된 문서에서 해당 질문에 대한 충분한 정보를 찾을 수 없습니다."
    
    try:
        # LLM 초기화
        llm = ChatOpenAI(
            model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # 프롬프트 템플릿
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """당신은 제공된 문서를 기반으로만 답변하는 전문 어시스턴트입니다.

핵심 규칙:
1. 제공된 컨텍스트에 명확한 근거가 있을 때만 답변하세요
2. 컨텍스트가 없거나 관련성이 낮으면 "제공된 문서에서 해당 질문에 대한 충분한 정보를 찾을 수 없습니다."라고 답하세요
3. 추측하거나 일반적인 지식으로 답변하지 마세요
4. 답변할 때는 반드시 출처를 명시하세요
5. 불확실하면 답변하지 마세요
6. 답변은 간결하고 정확하게 작성하세요"""),
            ("human", "컨텍스트:\n{context}\n\n질문: {question}")
        ])
        
        # 프롬프트 생성 및 실행
        messages = prompt_template.format_messages(
            context=context,
            question=question
        )
        
        response = llm.invoke(messages)
        return response.content
        
    except Exception as e:
        return f"답변 생성 중 오류가 발생했습니다: {str(e)}"


# LangChain Tool로 래핑
vector_search_tool = StructuredTool.from_function(
    func=search_and_answer,
    name="vector_search",
    description="""벡터 데이터베이스에서 관련 문서를 검색하고 LLM을 사용하여 질문에 대한 답변을 생성합니다.
이 도구는 사용자의 질문에 대해 벡터DB에서 관련 문서를 찾아 답변을 제공합니다.
질문에는 명확하고 구체적인 정보가 포함되어야 합니다.""",
)
