#!/usr/bin/env python3
"""
LLM과 벡터DB를 연동한 질의응답 테스트 스크립트
"""
import sys
from pathlib import Path

# vectorDB 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from vectorDB.test_llm_user import main

if __name__ == "__main__":
    main()