# ChatGPT 민감정보 차단 프록시

ChatGPT와의 통신을 모니터링하고 민감정보 포함 시 차단하는 MITM 프록시입니다.

## 📁 프로젝트 구조

```
semantic-proxy/
├── proxy.py          # 메인 프록시 애드온
├── config.py         # 설정 관리
├── logger.py         # 로깅 모듈
├── backend.py        # 백엔드 API 클라이언트
├── extractor.py      # 데이터 추출 모듈
├── response.py       # 응답 생성 모듈
├── pyproject.toml    # uv 의존성
└── logs/            # 로그 디렉토리
    ├── prompt_*.json
    └── blocked/
```

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
#python 및 uv 설치 필요
uv sync
```

### 2. 환경 변수 설정
```bash
# 백엔드 API 설정
export BACKEND_API_URL="http://localhost:8000"
export BACKEND_TIMEOUT="10"
export BACKEND_RETRY="2"
export BACKEND_API_KEY="your-api-key"  # 선택사항

# 프록시 설정
export PROXY_DEBUG="1"  # 디버그 모드
export BLOCK_MESSAGE="민감정보가 탐지되어 전송이 차단되었습니다."
export BLOCK_ON_BACKEND_ERROR="0"  # 백엔드 오류시 차단 여부

# 로그 설정
export LOG_DIR="./logs"
export LOG_MAX="1000"
```

### 3. 프록시 실행
```bash
# 방법 1: 쉘 스크립트 사용 (권장)
./start.sh

# 방법 2: Python 스크립트 사용
python run_proxy.py

# 방법 3: 직접 실행
mitmdump --set termlog_verbosity=error --ssl-insecure -p 8080 -s proxy.py --quiet
```

## 🧪 테스트 (백엔드 개발 전)

**현재는 테스트 모드로 동작합니다:**

### ✅ 차단 테스트
ChatGPT에 "777"이 포함된 메시지를 보내면 차단됩니다.
```
예시 입력: "오늘은 777일입니다"
결과: 🚫 [차단됨] test_block_777
```

### ✅ 통과 테스트  
"777"이 없는 일반 메시지는 통과됩니다.
```
예시 입력: "안녕하세요"
결과: ✅ [통과] test_allow
```

## 📊 출력 예시

```
🟢 프록시 시작됨 - 백엔드 연결 정상 (테스트 모드: 777 차단)

[GPT 통신] POST chatgpt.com/backend-api/conversation
[사용자 입력] 777이 포함된 테스트 메시지
🚫 [차단됨] test_block_777
   메시지: 테스트: 777이 포함된 내용이 차단되었습니다.

[GPT 통신] POST chatgpt.com/backend-api/conversation
[사용자 입력] 안녕하세요, 오늘 날씨가 어떤가요?
✅ [통과] test_allow
```

**주의**: ChatGPT 도메인 통신만 표시되며, 다른 사이트 통신은 출력되지 않습니다.

## 🔌 백엔드 API 인터페이스

### 콘텐츠 검사 엔드포인트
```http
POST /api/check
Content-Type: application/json
X-API-Key: {optional}

{
    "prompt": "사용자 입력 텍스트",
    "files": [
        {
            "filename": "document.pdf",
            "content_type": "application/pdf",
            "text": "추출된 텍스트",
            "size": 1024
        }
    ],
    "metadata": {
        "client_ip": "192.168.1.1",
        "path": "/backend-api/conversation",
        "timestamp": "2024-01-01T00:00:00"
    }
}

Response:
{
    "block": true,
    "reason": "PII_DETECTED",
    "details": {
        "message": "개인정보가 포함되어 있습니다.",
        "categories": ["주민번호", "전화번호"],
        "confidence": 0.95
    }
}
```

### 파일 처리 엔드포인트
```http
POST /api/process-file
Content-Type: multipart/form-data
X-API-Key: {optional}

file: (binary)

Response:
{
    "filename": "document.pdf",
    "content_type": "application/pdf",
    "text": "추출된 텍스트 내용...",
    "metadata": {
        "pages": 10,
        "ocr_applied": true
    }
}
```

### 헬스 체크 엔드포인트
```http
GET /api/health

Response:
{
    "status": "healthy",
    "version": "1.0.0"
}
```

## 🏗️ 모듈 설명

### `proxy.py`
- 메인 프록시 애드온
- 요청 인터셉트 및 라우팅
- 차단 로직 조정

### `config.py`
- 모든 설정값 중앙 관리
- 환경 변수 로드
- 정규식 패턴 정의

### `logger.py`
- 구조화된 로깅
- 로그 파일 회전
- 차단 로그 별도 관리

### `backend.py`
- 백엔드 API와의 통신
- 재시도 로직
- 타임아웃 처리

### `extractor.py`
- HTTP 요청 파싱
- 프롬프트 추출
- 멀티파트 데이터 처리
- Base64 이미지 디코딩

### `response.py`
- SSE 형식 응답 생성
- ChatGPT 호환 메시지 포맷
- 에러 응답 처리

## 🔧 커스터마이징

### 새로운 백엔드 엔드포인트 추가
```python
# config.py
class APIEndpoints:
    CHECK_CONTENT = "/api/check"
    PROCESS_FILE = "/api/process-file"
    CUSTOM_ENDPOINT = "/api/custom"  # 추가

# backend.py
def custom_api_call(self, data):
    endpoint = f"{self.base_url}{APIEndpoints.CUSTOM_ENDPOINT}"
    # 구현...
```


## 📝 주의사항

1. **SSL 인증서**: HTTPS 트래픽 검사를 위해 mitmproxy 인증서 설치 필요
2. **백엔드 의존성**: 백엔드 API가 다운되면 설정에 따라 통과/차단 결정
3. **성능**: 대용량 파일은 백엔드 처리 시간 고려
4. **보안**: API 키 사용 권장, 프로덕션 환경에서는 HTTPS 백엔드 사용

## 🐛 디버그

```bash
# 디버그 모드 활성화
export PROXY_DEBUG="1"

# mitmproxy 웹 인터페이스 사용
mitmweb -s proxy.py

# 상세 로그 확인
tail -f logs/prompt_latest.json
```

## 📄 라이선스

[라이선스 정보]