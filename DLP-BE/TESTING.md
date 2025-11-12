# 테스트 가이드

PII 검사 로그 시스템의 기능 테스트 가이드입니다.

---

## 📋 목차

1. [테스트 환경 설정](#테스트-환경-설정)
2. [테스트 실행](#테스트-실행)
3. [테스트 구성](#테스트-구성)
4. [수동 테스트](#수동-테스트)
5. [문제 해결](#문제-해결)

---

## 테스트 환경 설정

### 1. 의존성 설치

```bash
# 개발 의존성 포함 설치
uv sync --extra dev

# 또는 pip 사용 시
pip install -e ".[dev]"
```

설치되는 테스트 패키지:
- `pytest` - 테스트 프레임워크
- `pytest-asyncio` - 비동기 테스트 지원
- `httpx` - FastAPI 테스트 클라이언트
- `pytest-cov` - 코드 커버리지

### 2. Elasticsearch & PostgreSQL 실행

```bash
# Docker Compose로 실행
docker-compose up -d

# 상태 확인
docker-compose ps

# Elasticsearch 연결 확인
curl http://localhost:9200/_cluster/health?pretty
```

### 3. 환경 변수 설정 (선택)

`.env` 파일이 없으면 기본값 사용:

```env
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
DATABASE_URL=postgresql+asyncpg://admin:password123@localhost:5432/ai_tlsdlp
```

---

## 테스트 실행

### 전체 테스트 실행

```bash
# 모든 테스트 실행
pytest

# verbose 모드
pytest -v

# 진행 상황 표시
pytest -v --tb=short
```

### 특정 테스트 파일 실행

```bash
# PII 검사 테스트만
pytest tests/test_pii_detection.py -v

# 관리자 API 테스트만
pytest tests/test_admin_api.py -v

# Elasticsearch 통합 테스트만
pytest tests/test_elasticsearch.py -v
```

### 특정 테스트 클래스/함수 실행

```bash
# 특정 클래스
pytest tests/test_pii_detection.py::TestPIIDetectionAPI -v

# 특정 함수
pytest tests/test_pii_detection.py::TestPIIDetectionAPI::test_detect_pii_with_person_and_phone -v
```

### 키워드로 테스트 필터링

```bash
# 이름에 "pii"가 포함된 테스트만
pytest -k "pii" -v

# 이름에 "admin"이 포함된 테스트만
pytest -k "admin" -v

# 이름에 "elasticsearch"가 포함된 테스트만
pytest -k "elasticsearch" -v
```

### 코드 커버리지 확인

```bash
# 커버리지 리포트 생성
pytest --cov=app --cov-report=html

# 브라우저에서 확인
open htmlcov/index.html
```

### 실패한 테스트만 재실행

```bash
# 마지막 실행에서 실패한 테스트만
pytest --lf

# 실패한 테스트 먼저, 그 다음 나머지
pytest --ff
```

---

## 테스트 구성

### 1. PII 검사 API 테스트 (`test_pii_detection.py`)

**테스트 케이스**:
- ✅ 이름과 전화번호 탐지
- ✅ PII 미탐지 (일반 텍스트)
- ✅ 빈 텍스트 입력
- ✅ 전화번호 탐지 (다양한 형식)
- ✅ 이메일 탐지
- ✅ 한국어 이름 탐지
- ✅ 최대 길이 제한 (10,000자)
- ✅ IP 헤더 처리 (X-Forwarded-For)
- ✅ 헬스체크
- ✅ 동시 요청 처리 (10개)

**실행**:
```bash
pytest tests/test_pii_detection.py -v
```

**예상 소요 시간**: 30-60초 (AI 모델 로딩 포함)

### 2. 관리자 API 테스트 (`test_admin_api.py`)

**테스트 케이스**:

**인증 관련**:
- ✅ 사용자 등록
- ✅ 로그인 (JWT 토큰 발급)
- ✅ 잘못된 비밀번호 로그인

**로그 조회**:
- ✅ 인증 없이 로그 조회 시도 (401)
- ✅ 인증 후 로그 조회
- ✅ 필터링 (has_pii, client_ip 등)
- ✅ 페이징

**통계 API**:
- ✅ 인증 없이 통계 조회 시도 (401)
- ✅ 전체 통계 개요
- ✅ 시간대별 추세
- ✅ PII 타입별 통계
- ✅ IP별 통계

**실행**:
```bash
pytest tests/test_admin_api.py -v
```

**예상 소요 시간**: 20-40초

### 3. Elasticsearch 통합 테스트 (`test_elasticsearch.py`)

**테스트 케이스**:

**연결 테스트**:
- ✅ ES 클라이언트 연결
- ✅ 헬스 체크

**저장소 테스트**:
- ✅ 인덱스 생성
- ✅ 로그 인덱싱
- ✅ 로그 검색
- ✅ 필터링 검색
- ✅ 통계 집계
- ✅ 시간대별 집계

**성능 테스트**:
- ✅ 대량 인덱싱 (100개)

**실행**:
```bash
pytest tests/test_elasticsearch.py -v
```

**참고**: Elasticsearch가 실행 중이 아니면 자동으로 skip됩니다.

---

## 수동 테스트

자동화된 테스트 외에 수동으로 시스템을 테스트할 수 있습니다.

### 1. 백엔드 서버 실행

```bash
# 서버 시작
uv run uvicorn app.main:app --reload --port 8000

# 서버 상태 확인
curl http://localhost:8000/
```

### 2. PII 검사 테스트

```bash
# PII 탐지 (이름 + 전화번호)
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "제 이름은 홍길동이고 전화번호는 010-1234-5678입니다"}'

# PII 미탐지
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "오늘 날씨가 정말 좋습니다"}'

# IP 헤더 포함
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -H "X-Forwarded-For: 192.168.1.100" \
  -d '{"text": "김철수 test@example.com"}'
```

### 3. 관리자 계정 생성 및 로그인

```bash
# 1) 관리자 등록
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2) 로그인 (토큰 발급)
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 4. 관리자 API 테스트

```bash
# 로그 조회
curl "http://localhost:8000/api/v1/admin/logs?start_date=2025-01-01T00:00:00Z&end_date=2025-12-31T23:59:59Z" \
  -H "Authorization: Bearer $TOKEN" | jq

# 전체 통계
curl "http://localhost:8000/api/v1/admin/statistics/overview?start_date=2025-01-01T00:00:00Z&end_date=2025-12-31T23:59:59Z" \
  -H "Authorization: Bearer $TOKEN" | jq

# 시간대별 추세
curl "http://localhost:8000/api/v1/admin/statistics/timeline?start_date=2025-10-29T00:00:00Z&end_date=2025-10-29T23:59:59Z&interval=1h" \
  -H "Authorization: Bearer $TOKEN" | jq

# PII 타입별 통계
curl "http://localhost:8000/api/v1/admin/statistics/by-pii-type?start_date=2025-01-01T00:00:00Z&end_date=2025-12-31T23:59:59Z" \
  -H "Authorization: Bearer $TOKEN" | jq

# IP별 통계
curl "http://localhost:8000/api/v1/admin/statistics/by-ip?start_date=2025-01-01T00:00:00Z&end_date=2025-12-31T23:59:59Z&size=10" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 5. Elasticsearch 직접 확인

```bash
# 인덱스 목록
curl "http://localhost:9200/_cat/indices?v"

# 최근 로그 10개 조회
curl "http://localhost:9200/pii-detection-logs/_search?size=10&sort=timestamp:desc&pretty"

# 통계 조회
curl "http://localhost:9200/pii-detection-logs/_stats?pretty"

# PII 탐지된 로그만
curl -X POST "http://localhost:9200/pii-detection-logs/_search?pretty" \
  -H "Content-Type: application/json" \
  -d '{"query": {"term": {"has_pii": true}}, "size": 5}'
```

---

## 문제 해결

### 1. 테스트 실패 시

**증상**: `pytest` 실행 시 대부분의 테스트 실패

**해결 방법**:

1. **의존성 재설치**:
   ```bash
   uv sync --extra dev --force
   ```

2. **Docker 서비스 확인**:
   ```bash
   docker-compose ps
   # 모든 서비스가 "Up" 상태여야 함
   ```

3. **데이터베이스 초기화**:
   ```bash
   docker-compose down -v
   docker-compose up -d
   # 볼륨까지 삭제하고 재시작
   ```

### 2. Elasticsearch 테스트 Skip

**증상**: `test_elasticsearch.py` 테스트가 모두 skip됨

**원인**: Elasticsearch가 실행 중이 아님

**해결**:
```bash
# Elasticsearch 시작
docker-compose up -d elasticsearch

# 연결 확인
curl http://localhost:9200/_cluster/health?pretty
```

### 3. AI 모델 로딩 느림

**증상**: 첫 테스트 실행 시 30초 이상 소요

**원인**: HuggingFace에서 모델 다운로드 중

**해결**: 첫 실행 후에는 캐시되어 빨라집니다. 기다리세요.

### 4. JWT 토큰 만료

**증상**: 관리자 API 테스트 중 401 Unauthorized

**원인**: 토큰 유효기간 30분 경과

**해결**: 테스트는 자동으로 새 토큰을 생성합니다. 수동 테스트 시에는 재로그인하세요.

### 5. 포트 충돌

**증상**: `Address already in use` 에러

**해결**:
```bash
# 사용 중인 포트 확인
lsof -i :8000
lsof -i :9200
lsof -i :5432

# 프로세스 종료
kill -9 <PID>
```

---

## CI/CD 통합

### GitHub Actions 예시

`.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password123
          POSTGRES_DB: ai_tlsdlp
        ports:
          - 5432:5432

      elasticsearch:
        image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
        env:
          discovery.type: single-node
          xpack.security.enabled: false
        ports:
          - 9200:9200

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync --extra dev

      - name: Run tests
        run: pytest -v --cov=app

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 테스트 베스트 프랙티스

1. **테스트 격리**: 각 테스트는 독립적으로 실행 가능해야 함
2. **명확한 이름**: 테스트 함수명에서 무엇을 테스트하는지 명확히
3. **AAA 패턴**: Arrange (준비), Act (실행), Assert (검증)
4. **빠른 피드백**: 단위 테스트를 자주 실행
5. **CI/CD**: 모든 커밋에 대해 자동 테스트 실행

---

**문서 작성일**: 2025-10-29
**버전**: 1.0