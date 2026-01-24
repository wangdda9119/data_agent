"""
ReAct Agent 기반 챗봇 Agent
"""
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from .tools.vector_search_tool import vector_search_tool


def create_agent():
    """
    ReAct Agent를 생성하고 반환합니다.
    
    Returns:
        callable: 실행 가능한 Agent
    """
    # LLM 모델 초기화
    llm = ChatOpenAI(
        model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # 사용 가능한 도구들
    tools = [vector_search_tool]
    
    # ReAct Agent 생성 (langgraph 사용)
    agent_executor = create_react_agent(llm, tools)
    
    return agent_executor


def get_agent_response(query: str) -> str:
    """
    Agent를 사용하여 사용자 쿼리에 대한 답변을 생성합니다.
    
    Args:
        query: 사용자의 질문
    
    Returns:
        생성된 답변 문자열
    """
    try:
        from langchain_core.messages import HumanMessage
        
        agent = create_agent()
        
        # langgraph agent는 messages 형식을 사용
        result = agent.invoke({
            "messages": [HumanMessage(content=query)]
        })
        
        # 결과에서 마지막 메시지 추출
        if "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            return last_message.content
        
        return "답변을 생성할 수 없습니다."
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"
