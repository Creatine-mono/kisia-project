"""
프록시 설정 파일
"""
import os
import re
from pathlib import Path

# ==============================================================================
# 디버그 설정
# ==============================================================================
DEBUG = os.getenv("PROXY_DEBUG", "1") == "1"

# ==============================================================================
# 백엔드 API 설정
# ==============================================================================
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")
BACKEND_TIMEOUT = int(os.getenv("BACKEND_TIMEOUT", "30"))
BACKEND_RETRY = int(os.getenv("BACKEND_RETRY", "2"))
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY", "")  # 선택적 API 키

# ==============================================================================
# 타겟 호스트 및 경로 패턴
# ==============================================================================
# ChatGPT 관련 호스트
TARGET_HOSTS = re.compile(
    r"(chatgpt\.com|ab\.chatgpt\.com|ws\.chatgpt\.com|oaiusercontent\.com|upload\.openai\.com)$",
    re.I
)

# 대화/스트림 경로  
PATH_CONVERSATION = re.compile(
    r"^/backend-a(?:pi|non)/(?:f/)?conversation(?:$|/.*)|^/backend-a(?:pi|non)/sse/.*",
    re.I
)

# 업로드 경로
PATH_UPLOAD = re.compile(
    r"^/backend-a(?:pi|non)/files(?:$|/.*)|^/backend-a(?:pi|non)/attachments(?:$|/.*)|^/upload",
    re.I
)

# 외부 업로드 호스트
UPLOAD_HOSTS = re.compile(
    r"(upload\.openai\.com|oaiusercontent\.com|r2\.dev|cloudflarestorage\.com)$",
    re.I
)

# ==============================================================================
# 차단 설정
# ==============================================================================
BLOCK_MESSAGE = os.getenv("BLOCK_MESSAGE", "민감정보가 탐지되어 전송이 차단되었습니다.")
BLOCK_ON_BACKEND_ERROR = os.getenv("BLOCK_ON_BACKEND_ERROR", "0") == "1"

# ==============================================================================
# 로그 설정
# ==============================================================================
LOG_DIR = Path(os.getenv("LOG_DIR", "./logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_BASE = os.getenv("LOG_BASE", "prompt")
LOG_MAX = int(os.getenv("LOG_MAX", "1000"))
LOG_ROTATE = os.getenv("LOG_ROTATE", "1") == "1"
LOG_KEEP_LATEST = os.getenv("LOG_KEEP_LATEST", "1") == "1"

# ==============================================================================
# 콘텐츠 타입 매핑
# ==============================================================================
CONTENT_TYPE_TO_EXT = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff",
    "application/json": ".json",
    "text/plain": ".txt",
    "text/csv": ".csv",
    "text/markdown": ".md",
    "application/xml": ".xml",
    "text/xml": ".xml"
}

# ==============================================================================
# API 엔드포인트
# ==============================================================================
class APIEndpoints:
    CHECK_CONTENT = "/api/v1/pii/detect"  # 기존 PII 검사
    COMPREHENSIVE_ANALYSIS = "/api/v1/analyze/comprehensive"  # [미구현] 종합 분석 (PII + 유사도) - 향후 백엔드 구현 시 사용 예정
    PROCESS_FILE = "/api/v1/file/process"  # [미구현] 파일 처리용 (OCR, PDF 파싱) - 향후 확장
    HEALTH = "/api/v1/pii/health"