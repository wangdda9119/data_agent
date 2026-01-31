"""
챗봇 에이전트 인터랙티브 테스트
직접 질문을 해볼 수 있는 대화형 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agent.chatbot_agent import get_agent_response


def interactive_chat():
    """인터랙티브 채팅 시작"""
    print("\n" + "="*60)
    print("챗봇 에이전트 인터랙티브 테스트")
    print("="*60)
    print("\n사용 가능한 역할(role):")
    print("  1. educator   - 교육 전문가 (기본값)")
    print("  2. researcher - 연구원")
    print("  3. assistant  - 일반 어시스턴트")
    print("\n명령어:")
    print("  /role <역할명>  - 역할 변경")
    print("  /exit           - 종료")
    print("  /info           - 현재 설정 확인")
    print("-" * 60 + "\n")
    
    current_role = "educator"
    
    while True:
        try:
            # 사용자 입력
            user_input = input(f"[{current_role}] You: ").strip()
            
            # 입력이 없으면 계속
            if not user_input:
                continue
            
            # 명령어 처리
            if user_input.lower() == "/exit":
                print("\n👋 종료합니다!")
                break
            elif user_input.lower() == "/info":
                print(f"현재 역할: {current_role}")
                continue
            elif user_input.lower().startswith("/role"):
                parts = user_input.split()
                if len(parts) == 2:
                    new_role = parts[1].lower()
                    if new_role in ["educator", "researcher", "assistant"]:
                        current_role = new_role
                        print(f"✓ 역할이 '{current_role}'로 변경되었습니다.\n")
                    else:
                        print(f"✗ 알 수 없는 역할입니다. educator, researcher, assistant 중에서 선택하세요.\n")
                else:
                    print("사용법: /role <educator|researcher|assistant>\n")
                continue
            
            # 에이전트에 쿼리 전송
            print(f"\n⏳ {current_role}가 생각 중입니다...\n")
            response = get_agent_response(user_input, role=current_role)
            print(f"Bot: {response}\n")
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 프로그램 중단됨!")
            break
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}\n")


def sample_conversation():
    """샘플 대화 실행"""
    print("\n" + "="*60)
    print("샘플 대화 시작")
    print("="*60 + "\n")
    
    # 샘플 대화 시나리오
    conversations = [
        {
            "role": "educator",
            "query": "2025학년도 수강신청은 언제인가요?",
            "description": "교육자 역할로 수강신청 일정 질문"
        },
        {
            "role": "researcher",
            "query": "논문 작성에 필요한 정보는?",
            "description": "연구자 역할로 논문 작성 조언"
        },
        {
            "role": "assistant",
            "query": "안녕하세요! 무엇을 도와드릴까요?",
            "description": "어시스턴트 역할로 인사"
        }
    ]
    
    for i, conv in enumerate(conversations, 1):
        print(f"\n[샘플 {i}] {conv['description']}")
        print(f"역할: {conv['role']}")
        print(f"Q: {conv['query']}")
        print("-" * 40)
        
        try:
            response = get_agent_response(conv['query'], role=conv['role'])
            print(f"A: {response}\n")
        except Exception as e:
            print(f"❌ 오류: {e}\n")


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("챗봇 에이전트 테스트")
    print("="*60)
    print("\n선택하세요:")
    print("1. 인터랙티브 채팅 (직접 질문)")
    print("2. 샘플 대화 보기")
    print("3. 종료")
    
    while True:
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == "1":
            interactive_chat()
            break
        elif choice == "2":
            sample_conversation()
            break
        elif choice == "3":
            print("종료합니다!")
            break
        else:
            print("1-3 중에서 선택하세요.")


if __name__ == "__main__":
    main()
