from .vectorStore import get_vector_store
from pathlib import Path

def main():
    print("=== 벡터DB 생성 ===")
    
    vs = get_vector_store()
    
    # embedded 폴더 확인 (vectorDB 폴더 안에 생성)
    vectordb_path = Path(__file__).parent
    embedded_folder = vectordb_path / "embedded"
    
    # 벡터DB도 vectorDB 폴더 안에 저장되도록 설정
    vector_db_path = vectordb_path / "vector_db"
    
    # VectorStore 인스턴스에 경로 설정
    vs.vector_db_path = str(vector_db_path)
    vs.embedded_folder = str(embedded_folder)
    
    if not embedded_folder.exists():
        print("embedded 폴더가 없습니다. 폴더를 생성합니다.")
        embedded_folder.mkdir(parents=True)
        print(f"embedded 폴더 생성됨: {embedded_folder}")
        print("embedded 폴더에 PDF 파일을 넣고 다시 실행하세요.")
        return
    
    pdf_files = list(embedded_folder.glob("*.pdf"))
    if not pdf_files:
        print("embedded 폴더에 PDF 파일이 없습니다.")
        print("PDF 파일을 넣고 다시 실행하세요.")
        return
    
    print(f"발견된 PDF 파일: {len(pdf_files)}개")
    for pdf in pdf_files:
        print(f"  - {pdf.name}")
    
    # 기존 벡터DB 삭제하고 새로 생성
    print("\n벡터DB 생성 중...")
    vs.create_new_embeddings(str(embedded_folder), reset_db=True)
    
    # 결과 확인
    stats = vs.get_stats()
    print(f"\n✅ 벡터DB 생성 완료!")
    print(f"총 문서 수: {stats['total_docs']}개")
    print(f"저장 경로: {stats['vector_db_path']}")
    print("\n이제 test_user.py를 실행하여 검색을 테스트하세요.")

if __name__ == "__main__":
    main()
