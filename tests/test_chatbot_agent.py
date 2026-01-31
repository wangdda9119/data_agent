"""
챗봇 에이전트 테스트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agent.chatbot_agent import get_agent_response, build_agent


def test_agent_creation():
    """Agent 생성 테스트"""
    print("\n=== Agent 생성 테스트 ===")
    try:
        agent = build_agent(role="educator")
        assert agent is not None, "educator 에이전트 생성 실패"
        print("✓ educator 에이전트 생성 성공")
        
        agent = build_agent(role="researcher")
        assert agent is not None, "researcher 에이전트 생성 실패"
        print("✓ researcher 에이전트 생성 성공")
        
        agent = build_agent(role="assistant")
        assert agent is not None, "assistant 에이전트 생성 실패"
        print("✓ assistant 에이전트 생성 성공")
        
    except Exception as e:
        raise AssertionError(f"Agent 생성 실패: {e}")


def test_educator_role():
    """Educator 역할 테스트"""
    print("\n=== Educator 역할 테스트 ===")
    try:
        query = "2025학년도 수강신청에 대해 알려줘"
        print(f"Q: {query}")
        
        response = get_agent_response(query, role="educator")
        print(f"A: {response}\n")
        
        assert response and "오류" not in response, "Educator 응답 실패"
        print("✓ Educator 테스트 성공")
    except Exception as e:
        raise AssertionError(f"Educator 테스트 오류: {e}")


def test_researcher_role():
    """Researcher 역할 테스트"""
    print("\n=== Researcher 역할 테스트 ===")
    try:
        query = "논문 작성에 필요한 정보는?"
        print(f"Q: {query}")
        
        response = get_agent_response(query, role="researcher")
        print(f"A: {response}\n")
        
        assert response and "오류" not in response, "Researcher 응답 실패"
        print("✓ Researcher 테스트 성공")
    except Exception as e:
        raise AssertionError(f"Researcher 테스트 오류: {e}")


def test_assistant_role():
    """Assistant 역할 테스트"""
    print("\n=== Assistant 역할 테스트 ===")
    try:
        query = "안녕하세요"
        print(f"Q: {query}")
        
        response = get_agent_response(query, role="assistant")
        print(f"A: {response}\n")
        
        assert response and "오류" not in response, "Assistant 응답 실패"
        print("✓ Assistant 테스트 성공")
    except Exception as e:
        raise AssertionError(f"Assistant 테스트 오류: {e}")


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*50)
    print("챗봇 에이전트 테스트 시작")
    print("="*50)
    
    test_agent_creation()
    test_educator_role()
    test_researcher_role()
    test_assistant_role()
    
    print("\n" + "="*50)
    print("✓ 모든 테스트 성공!")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_tests()
    sys.exit(0)
