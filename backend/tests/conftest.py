"""
테스트 공통 설정.

app.config.Settings 가 SECRET_KEY 를 필수로 요구하므로, import 전에 넣어둔다.
1계층 테스트(순수 함수)는 DB 에 접속하지 않지만, app 패키지를 import 하는 순간
settings 가 생성되기 때문에 값이 필요하다.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-used-in-production")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

# backend/ 를 import 경로에 추가 (pytest 를 backend/ 에서 실행)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
