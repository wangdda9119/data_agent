"""
ReAct Agent 기반 챗봇 Agent (Langchain/Langgraph - 최신 문법)
"""
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from .tools.vector_search_tool import vector_search_tool, set_global_vector_store as vector_tool_set_vs
from .tools.tavily_search_tool import tavily_search_tool

# 전역 벡터 스토어 인스턴스
_global_vector_store = None

def set_global_vector_store(vs):
    """서버 시작 시 호출되어 전역 벡터 스토어를 설정합니다."""
    global _global_vector_store
    _global_vector_store = vs
    # vector_search_tool에도 동일한 인스턴스 전달
    vector_tool_set_vs(vs)

def get_global_vector_store():
    """전역 벡터 스토어 인스턴스를 반환합니다."""
    return _global_vector_store


# Role 기반 시스템 프롬프트 정의
SYSTEM_PROMPTS = {
    "educator": """당신은 순천향대학교의 친절하고 전문적인 교육 AI 어시스턴트입니다.

**컨텍스트:**
- 당신은 순천향대학교에 관한 정보를 제공합니다
- 사용자가 언급하는 "학교", "우리 대학", "셔틀버스", "기숙사", "캠퍼스" 등은 모두 순천향대학교를 의미합니다
- 다른 학교나 기관에 대한 질문이 아닌 이상, 항상 순천향대학교 관점에서 답변합니다

**도구 설명:**
- 벡터DB 검색 도구: 순천향대학교의 입시, 학사, 강의계획서, 수강신청, 캠퍼스 시설 등 다양한 학사 정보가 저장되어 있습니다
- 웹 검색 도구: 최신 정보가 필요할 때 인터넷을 통해 실시간 정보를 검색합니다

**응답 방식:**
- 사용자의 질문을 정확하게 이해하고 명확하게 답변합니다
- 벡터DB에 있는 정보를 우선적으로 사용하여 답변합니다
- 필요시 웹 검색 도구를 보완적으로 사용합니다
- 답변은 이해하기 쉽고 구체적이어야 합니다
- 출처를 명시합니다""",
    
    "researcher": """당신은 순천향대학교의 철저한 연구 AI 어시스턴트입니다.

**컨텍스트:**
- 당신은 순천향대학교에 관한 정보를 제공합니다
- 사용자가 언급하는 "학교", "우리 대학", "셔틀버스", "기숙사", "캠퍼스" 등은 모두 순천향대학교를 의미합니다
- 다른 학교나 기관에 대한 질문이 아닌 이상, 항상 순천향대학교 관점에서 답변합니다

**도구 설명:**
- 벡터DB 검색 도구: 순천향대학교의 입시, 학사, 강의계획서, 수강신청, 캠퍼스 시설, 교칙 등 정확한 학사 정보 저장
- 웹 검색 도구: 최신 뉴스, 통계 등 실시간 정보 검색

**응답 방식:**
- 정확한 정보와 데이터 기반의 답변을 제공합니다
- 벡터DB에 저장된 공식 정보를 우선적으로 활용합니다
- 한계점과 불확실성을 명시적으로 표현합니다
- 신뢰할 수 있는 출처(벡터DB 또는 공식 웹사이트)만 인용합니다""",
    
    "assistant": """당신은 순천향대학교의 도움이 되는 일반 AI 어시스턴트입니다.

**컨텍스트:**
- 당신은 순천향대학교에 관한 정보를 제공합니다
- 사용자가 언급하는 "학교", "우리 대학", "셔틀버스", "기숙사", "캠퍼스", "동기" 등은 모두 순천향대학교를 의미합니다
- 학교, 셔틀버스, 기숙사 등의 시설 관련 질문이 나오면 자동으로 순천향대학교 관점으로 답변합니다
- 다른 학교나 기관에 대한 명확한 질문이 아닌 이상, 순천향대학교 정보를 제공합니다

**도구 설명:**
- 벡터DB 검색 도구: 순천향대학교의 입시정보, 학사제도, 수강신청 가이드, 기숙사, 캠퍼스 시설, 셔틀버스 운영 등 학교 관련 정보가 저장되어 있습니다
- 웹 검색 도구: 최신 뉴스나 실시간 정보가 필요한 경우 사용합니다

**응답 방식:**
- 사용자의 요청을 친절하고 따뜻하게 처리합니다
- 순천향대학교 관련 정보는 벡터DB에서 먼저 찾습니다
- 이해하기 쉬운 방식으로 설명합니다"""
}


def create_react_prompt(role: str = "assistant") -> ChatPromptTemplate:
    """
    Role 기반 ReAct 프롬프트 템플릿 생성
    
    Args:
        role: 에이전트의 역할 ("educator", "researcher", "assistant")
    
    Returns:
        ChatPromptTemplate: 구성된 프롬프트 템플릿
    """
    system_prompt = SYSTEM_PROMPTS.get(role, SYSTEM_PROMPTS["assistant"])
    
    # 최신 문법: ChatPromptTemplate.from_messages()
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt + """\n\n당신은 다음 도구들을 사용할 수 있습니다:
{tools}

다음 형식으로 응답하세요:
Question: 사용자의 질문
Thought: 이 질문을 해결하기 위해 어떻게 할지 생각
Action: 사용할 도구 이름
Action Input: 도구에 전달할 입력값
Observation: 도구로부터 받은 결과
... (이 Thought/Action/Observation을 반복할 수 있습니다)
Thought: 이제 최종 답변을 할 수 있습니다
Final Answer: 사용자에게 주는 최종 답변"""),
        ("user", "{input}"),
        ("assistant", "{agent_scratchpad}")
    ])
    
    return prompt


def get_system_message(role: str = "assistant") -> str:
    """역할에 맞는 시스템 메시지 반환"""
    return SYSTEM_PROMPTS.get(role, SYSTEM_PROMPTS["assistant"])


def build_agent(role: str = "assistant"):
    """
    ReAct Agent를 생성하고 반환합니다.
    
    Args:
        role: 에이전트의 역할 ("educator", "researcher", "assistant")
    
    Returns:
        Runnable: 실행 가능한 Agent
    """
    # LLM 모델 초기화
    llm = ChatOpenAI(
        model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # 사용 가능한 도구들 (없을 수 있는 tavily 도구는 존재할 때만 추가)
    tools = [vector_search_tool, tavily_search_tool]
    
    # ReAct Agent 생성
    agent = create_react_agent(llm, tools)
    
    # role 정보를 agent에 저장 (나중에 사용)
    agent._role = role
    
    return agent


def get_agent_response(query: str, role: str = "assistant", chat_history: list = None) -> str:
    """
    Agent를 사용하여 사용자 쿼리에 대한 답변을 생성합니다.
    
    Args:
        query: 사용자의 질문
        role: 에이전트의 역할 ("educator", "researcher", "assistant")
        chat_history: 이전 대화 히스토리 (선택사항)
    
    Returns:
        생성된 답변 문자열
    """
    try:
        agent = build_agent(role=role)
        
        # 시스템 메시지와 사용자 메시지를 함께 전달
        system_message = get_system_message(role)
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=query)
        ]
        
        # langgraph agent는 messages 형식을 사용
        result = agent.invoke({
            "messages": messages
        })
        
        # 결과에서 마지막 메시지 추출
        if "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            return last_message.content
        
        return "답변을 생성할 수 없습니다."
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"


def get_agent_response_streaming(query: str, role: str = "assistant"):
    """
    Agent를 사용하여 스트리밍 방식으로 답변을 생성합니다.
    
    Args:
        query: 사용자의 질문
        role: 에이전트의 역할
    
    Yields:
        생성되는 텍스트
    """
    try:
        agent = build_agent(role=role)
        
        # 시스템 메시지와 사용자 메시지를 함께 전달
        system_message = get_system_message(role)
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=query)
        ]
        
        # 스트리밍 방식으로 실행
        for chunk in agent.stream({"messages": messages}):
            if "messages" in chunk and chunk["messages"]:
                last_message = chunk["messages"][-1]
                if hasattr(last_message, 'content'):
                    yield last_message.content
    except Exception as e:
        yield f"오류가 발생했습니다: {str(e)}"
