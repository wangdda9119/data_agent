# 벡터DB 검색 시스템

## 사용 방법

### 1단계: 벡터DB 생성
```bash
python run_create_db.py
```
- vectorDB/embedded 폴더의 PDF 파일들을 임베딩하여 벡터DB를 생성합니다
- 기존 벡터DB가 있으면 삭제하고 새로 생성합니다

### 2단계: 검색 테스트
```bash
python run_test.py
```
- 생성된 벡터DB에서 검색을 테스트할 수 있습니다
- 'quit' 입력으로 종료

### 3단계: LLM 연동 테스트
```bash
python run_llm_test.py
```
- OpenAI GPT와 벡터DB를 연동한 질의응답 테스트
- 'quit' 또는 'exit' 입력으로 종료

## 파일 구조
```
env_test/
├── vectorDB/                    # 벡터DB 모듈
│   ├── __init__.py
│   ├── vectorStore.py           # 벡터DB 핵심 로직
│   ├── create_vector_db.py      # 벡터DB 생성 스크립트
│   ├── test_user.py             # 검색 테스트 스크립트
│   ├── test_llm_user.py         # LLM 연동 테스트 스크립트
│   ├── embedded/                # PDF 파일들을 넣는 폴더
│   └── vector_db/               # 생성된 벡터DB 저장 폴더
├── run_create_db.py             # 벡터DB 생성 실행기
├── run_test.py                  # 검색 테스트 실행기
├── run_llm_test.py              # LLM 테스트 실행기
└── .env                         # 환경변수 파일
```

## 필요한 환경변수 (.env 파일)
```
OPENAI_API_KEY=your_api_key_here
```