"""
Tavily Search를 사용한 웹 검색 Tool
"""
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import Tool


def create_tavily_search_tool() -> Tool:
    """
    Tavily Search 도구를 생성합니다.
    
    Returns:
        Tool: Tavily Search Tool
    """
    # Tavily API 키 확인
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY 환경변수가 설정되지 않았습니다.")
    
    # TavilySearchResults 초기화
    tavily_search = TavilySearchResults(
        max_results=5,
        include_answer=True,
        include_raw_content=False
    )
    
    return tavily_search


def simple_web_search(query: str) -> str:
    """
    웹에서 정보를 검색합니다.
    
    Args:
        query: 검색 쿼리
    
    Returns:
        검색 결과 문자열
    """
    try:
        tavily_search = create_tavily_search_tool()
        results = tavily_search.invoke(query)
        
        if not results:
            return "검색 결과가 없습니다."
        
        # 결과를 보기 좋은 형식으로 정리
        formatted_results = []
        for i, result in enumerate(results, 1):
            if isinstance(result, dict):
                title = result.get("title", "제목 없음")
                url = result.get("url", "")
                content = result.get("content", "")
                formatted_results.append(f"{i}. {title}\nURL: {url}\n내용: {content[:200]}...\n")
            else:
                formatted_results.append(f"{i}. {str(result)}\n")
        
        return "\n".join(formatted_results)
    
    except Exception as e:
        return f"웹 검색 오류: {str(e)}"


# Agent에서 사용할 Tool 객체
try:
    tavily_search_tool = create_tavily_search_tool()
except ValueError:
    # API 키가 없으면 None으로 설정
    tavily_search_tool = None
