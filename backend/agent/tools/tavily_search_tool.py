"""
Tavily Search를 사용한 웹 검색 Tool
"""
import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import StructuredTool, Tool

# .env 파일 로드 (환경변수 우선, 없으면 .env에서 로드)
load_dotenv()

def create_tavily_search_tool() -> Tool:
    """
    Tavily Search 도구를 생성합니다.
    
    Returns:
        Tool: Tavily Search Tool
    """
    # Tavily API 키 확인 (환경변수 또는 .env에서 로드됨)
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY 환경변수가 설정되지 않았습니다.")
    
    # TavilySearchResults 초기화
    tavily_search = TavilySearchResults(
        api_key=api_key,
        max_results=2,
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


# Agent에서 사용할 Tool 객체: 실제 호출 시 `simple_web_search`가 API 키를 체크합니다.
tavily_search_tool = StructuredTool.from_function(
    func=simple_web_search,
    name="tavily_search",
    description="웹에서 Tavily Search를 사용하여 관련 정보를 검색합니다. TAVILY_API_KEY가 필요합니다."
)
 
# 모듈 import 시점에 TAVILY_API_KEY가 없으면 도구를 None으로 설정 (테스트 및 안전성 목적)
if not os.getenv("TAVILY_API_KEY"):
    tavily_search_tool = None

