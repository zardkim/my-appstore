"""
파일명 파싱(parser.py)과 파일 분류(classifier.py)에서 공통으로 쓰이는 키워드 세트.

parser.py의 NOISE_WORDS와 classifier.py의 _PATCH_KEYWORDS가 각자 별도로
관리되면서 "fix" 같은 키워드가 classifier에는 있지만 parser에는 없는 등
불일치가 생겼다. 패치/크랙 관련 키워드는 이 모듈에서 한 곳으로 관리한다.
"""

# 패치, 크랙, 키젠 등 정품 인증 우회 관련 핵심 키워드
PATCH_KEYWORDS = frozenset({
    "patch", "hotfix", "fix", "crack", "keygen", "keygenerator",
    "serial", "key", "reg", "loader", "activator", "unlocker", "bypass",
})
