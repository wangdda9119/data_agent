#!/usr/bin/env python3
"""
벡터DB 생성 스크립트
"""
import sys
from pathlib import Path

# vectorDB 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from vectorDB.create_vector_db import main

if __name__ == "__main__":
    main()