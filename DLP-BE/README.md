# AI-TLS-DLP Backend v1.1.0

## 프로젝트 개요

한국어 개인정보(PII) 탐지를 위한 **정규식 + BERT NER** 기반 FastAPI 백엔드 서비스입니다.

허깅페이스의 `psh3333/roberta-large-korean-pii5` 모델을 사용하여 실시간 PII 탐지 및 차단 기능을 제공합니다.

## ✨ 주요 기능 (v1.1.0)

- ✅ **JWT 기반 인증 시스템**: 회원가입, 로그인, 토큰 인증
- ✅ **정규식 기반 PII 탐지**: 전화번호, 이메일 등 패턴 매칭
- ✅ **BERT NER 기반 PII 탐지**: RoBERTa 모델을 활용한 개인정보 엔티티 인식
- ✅ **실시간 차단 판단**: 탐지된 PII 기반 자동 차단 여부 결정
- ✅ **RESTful API**: FastAPI 기반 고성능 API
- ✅ **자동 문서화**: Swagger UI 제공
- ✅ **PostgreSQL 데이터베이스**: 사용자 정보 및 인증 관리

## 🏗️ 프로젝트 구조

```
DLP-BE/
├── app/
│   ├── main.py                # FastAPI 진입점
│   ├── api/routers/
│   │   ├── auth.py           # 인증 API (회원가입, 로그인)
│   │   └── pii.py            # PII 탐지 API (인증 필요)
│   ├── services/
│   │   └── pii_service.py    # 비즈니스 로직
│   ├── ai/
│   │   ├── pii_detector.py   # RoBERTa PII 탐지 모델
│   │   └── model_manager.py  # 모델 싱글톤 관리
│   ├── schemas/
│   │   ├── auth.py           # 인증 스키마
│   │   └── pii.py            # PII 스키마
│   ├── models/
│   │   └── user.py           # User 데이터 모델
│   ├── repository/
│   │   └── user_repo.py      # User 데이터 접근 레이어
│   ├── db/
│   │   ├── base.py           # SQLAlchemy Base
│   │   └── session.py        # DB 세션 관리
│   ├── core/
│   │   ├── config.py         # 설정
│   │   ├── security.py       # JWT 및 암호화
│   │   └── dependencies.py   # 인증 의존성
│   └── utils/
│       └── entity_extractor.py # BIO 태그 엔티티 추출
├── alembic/                   # DB 마이그레이션
│   └── versions/             # 마이그레이션 파일들
├── docker-compose.yml         # PostgreSQL 컨테이너
├── alembic.ini               # Alembic 설정
├── .env                      # 환경 변수 (생성 필요)
├── pyproject.toml            # 의존성 관리
└── CLAUDE.md                 # 개발 문서
```

## 🚀 빠른 시작 (새로운 PC에서 실행)

### 1. 요구사항

- Python 3.13+
- Docker & Docker Compose
- uv (또는 pip)

### 2. 프로젝트 클론 및 이동

```bash
git clone <repository-url>
cd DLP-BE
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 작성합니다:

```bash
# 데이터베이스
DATABASE_URL=postgresql+asyncpg://admin:password123@localhost:5432/ai_tlsdlp

# JWT 인증
SECRET_KEY=dlp-secret-key-change-in-production-minimum-32-characters-required
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI 모델 설정
PII_MODEL_NAME=psh3333/roberta-large-korean-pii5
DEFAULT_PII_THRESHOLD=0.59

# 앱 설정
DEBUG=True
```

### 4. 의존성 설치

```bash
# uv 사용 (권장)
uv sync

# 또는 pip 사용
pip install -e .
```

### 5. PostgreSQL 컨테이너 시작

```bash
# Docker 데몬이 실행 중인지 확인 후
docker-compose up -d

# 컨테이너 상태 확인
docker-compose ps
```

### 6. 데이터베이스 마이그레이션 적용

```bash
# Alembic으로 users 테이블 생성
alembic upgrade head
```

### 7. 서버 실행

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🔄 다른 PC에서 동일 환경 구축 요약

**순서대로 실행하세요:**

```bash
# 1. 프로젝트 클론
git clone <repository-url> && cd DLP-BE

# 2. .env 파일 생성 (위 내용 복사)
nano .env

# 3. 의존성 설치
uv sync

# 4. PostgreSQL 시작
docker-compose up -d

# 5. DB 마이그레이션 (테이블 생성)
alembic upgrade head

# 6. 서버 실행
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

이제 http://localhost:8000/docs 에서 API를 사용할 수 있습니다!

## 📡 API 사용법

### 1. 회원가입

**엔드포인트**: `POST /api/v1/auth/register`

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "테스트 사용자"
  }'
```

**응답**:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "테스트 사용자",
  "is_active": true,
  "is_superuser": false
}
```

### 2. 로그인

**엔드포인트**: `POST /api/v1/auth/login`

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

**응답**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. 현재 사용자 정보 조회

**엔드포인트**: `GET /api/v1/auth/me` (인증 필요)

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

### 4. PII 탐지 (인증 필요)

**엔드포인트**: `POST /api/v1/pii/detect`

```bash
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"text": "제 이름은 홍길동이고 전화번호는 010-1234-5678입니다"}'
```

**응답 예시**:
```json
{
  "has_pii": true,
  "reason": "개인정보 2개 탐지됨 (PERSON, PHONE_NUM)",
  "details": "탐지된 개인정보: PERSON '홍길동' (신뢰도: 95.0%), PHONE_NUM '010-1234-5678' (신뢰도: 89.0%)",
  "entities": [
    {
      "type": "PERSON",
      "value": "홍길동",
      "confidence": 0.95,
      "token_count": 2
    },
    {
      "type": "PHONE_NUM",
      "value": "010-1234-5678",
      "confidence": 0.89,
      "token_count": 7
    }
  ]
}
```

### 5. 헬스체크 (인증 필요)

**엔드포인트**: `GET /api/v1/pii/health`

```bash
curl -X GET "http://localhost:8000/api/v1/pii/health" \
  -H "Authorization: Bearer <access_token>"
```

**⚠️ 주의**: v1.1.0부터 모든 PII API는 JWT 인증이 필요합니다!

## 🛠️ 기술 스택

- **백엔드**: FastAPI + Python 3.13
- **데이터베이스**: PostgreSQL 15 + SQLAlchemy 2.0 (Async)
- **인증**: JWT (python-jose) + bcrypt (passlib)
- **마이그레이션**: Alembic
- **AI 모델**: Transformers + PyTorch
- **PII 모델**: `psh3333/roberta-large-korean-pii5`
- **패키지 관리**: uv
- **컨테이너**: Docker + Docker Compose

## 📊 성능

- **첫 요청**: ~2초 (모델 로딩 포함)
- **이후 요청**: 100-300ms
- **처리 가능 텍스트**: 최대 512 토큰 (약 1000자)

## 🗺️ 로드맵

### Phase 1: 기본 PII 탐지 + 인증 시스템 (완료) ✅
- RoBERTa 모델 통합
- 정규식 기반 패턴 매칭
- BIO 태깅 정확도 개선
- 모델 성능 최적화
- JWT 기반 인증/인가 시스템
- PostgreSQL + Alembic 마이그레이션

### Phase 2: 확장 기능 (예정)
- 문서 업로드 및 파싱 (PDF, DOCX)
- 유사도 기반 문서 비교 (KoSimCSE)
- 벡터 DB 연동 (ChromaDB)
- 관리자 대시보드

### Phase 3: 운영 준비 (예정)
- 단위/통합 테스트
- 로깅 및 모니터링
- Rate limiting 및 보안 강화
- Docker 컨테이너화 (전체 앱)

## 🔧 데이터베이스 관리

### 새로운 마이그레이션 생성

```bash
# 모델 변경 후 마이그레이션 파일 자동 생성
alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
alembic upgrade head
```

### 마이그레이션 롤백

```bash
# 이전 버전으로 되돌리기
alembic downgrade -1

# 특정 버전으로 되돌리기
alembic downgrade <revision_id>
```

### 마이그레이션 히스토리 확인

```bash
alembic history
alembic current
```

## 📖 문서

자세한 개발 문서는 [CLAUDE.md](./CLAUDE.md)를 참고하세요.

## 🤝 기여

이 프로젝트는 KISIA 프로젝트의 일부입니다.

## 📄 라이선스

이 프로젝트의 라이선스는 프로젝트 소유자와 협의하세요.

## 📧 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.

---

**AI-TLS-DLP Backend v1.1.0** - JWT 인증 + 정규식 + BERT NER 기반 PII 탐지 시스템