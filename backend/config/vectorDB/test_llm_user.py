import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .vectorStore import get_vector_store

def build_context(search_results, max_chars: int = 8000) -> tuple[str, int]:
    """컨텍스트 구성 및 관련성 점수 계산"""
    if not search_results:
        return "", 0
    
    parts = []
    total = 0
    relevance_scores = []
    
    for result in search_results:
        src = result["metadata"].get("file_name", "unknown")
        page = result["metadata"].get("page", "?")
        text = result["content"].strip()
        score = result.get("score", 0)
        
        relevance_scores.append(score)
        block = f"[출처: {src}, 페이지: {page}]\n{text}"
        
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
    
    context = "\n\n---\n\n".join(parts)
    avg_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
    
    return context, avg_score

def main():
    vs = get_vector_store()

    print("벡터DB 상태 확인 중...")
    
    # vectorDB 폴더 안에 벡터DB 저장되도록 설정
    vectordb_path = Path(__file__).parent
    vector_db_path = vectordb_path / "vector_db"
    embedded_folder = vectordb_path / "embedded"
    
    vs.vector_db_path = str(vector_db_path)
    vs.embedded_folder = str(embedded_folder)
    
    stats = vs.get_stats()
    if not stats.get("loaded", False):
        print("기존 벡터DB가 없어 embedded 폴더로 새로 생성합니다.")
        vs.create_new_embeddings(str(embedded_folder), reset_db=True)
        stats = vs.get_stats()

    print(f"✅ 벡터DB 로드 완료 (총 {stats['total_docs']}개 문서)")

    # LangChain ChatOpenAI 모델 초기화
    llm = ChatOpenAI(
        model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Role 기반 프롬프트 템플릿 (최신 문법)
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """당신은 제공된 문서를 기반으로만 답변하는 전문 어시스턴트입니다.

핵심 규칙:
1. 제공된 컨텍스트에 명확한 근거가 있을 때만 답변하세요
2. 컨텍스트가 없거나 관련성이 낮으면 "제공된 문서에서 해당 질문에 대한 충분한 정보를 찾을 수 없습니다."라고 답하세요
3. 추측하거나 일반적인 지식으로 답변하지 마세요
4. 답변할 때는 반드시 출처를 명시하세요
5. 불확실하면 답변하지 마세요"""),
        ("human", "컨텍스트: {context}\n\n질문: {question}")
    ])

    print("\n질문을 입력하세요 (종료: 'quit' 또는 'exit'):\n")

    while True:
        q = input("질문: ").strip()
        if not q:
            continue
        if q.lower() in ("quit", "exit"):
            break

        print("관련 문서 검색 중...")
        search_results = vs.search(q, k=10)
        print(f"✅ {len(search_results)}개 문서 검색됨")
        
        context, avg_score = build_context(search_results)
        
        # 관련성 임계값 설정 (점수가 너무 낮으면 답변 안함)
        MIN_RELEVANCE_SCORE = 0.7
        MIN_CONTEXT_LENGTH = 50
        
        if not context or len(context) < MIN_CONTEXT_LENGTH or avg_score < MIN_RELEVANCE_SCORE:
            print("\n답변:")
            print("❌ 제공된 문서에서 해당 질문에 대한 충분한 정보를 찾을 수 없습니다.")
            print(f"   (검색된 문서: {len(search_results)}개, 관련성 점수: {avg_score:.2f})")
            print()
            continue
        
        try:
            # 프롬프트 생성 및 실행
            messages = prompt_template.format_messages(
                context=context,
                question=q
            )
            
            response = llm.invoke(messages)
            answer = response.content
            
            print("\n답변:")
            print(answer)
            print(f"\n📊 검색 정보: {len(search_results)}개 문서, 관련성: {avg_score:.2f}")
            print()

        except Exception as e:
            print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
