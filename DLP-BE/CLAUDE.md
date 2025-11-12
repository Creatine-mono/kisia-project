# AI-TLS-DLP Backend - 개발 가이드

## 프로젝트 개요
한국어 개인정보(PII) 탐지를 위한 FastAPI 기반 백엔드 서비스입니다.
허깅페이스의 `psh3333/roberta-large-korean-pii5` 모델을 사용하여 **정규식**과 **BERT NER** 기반 PII 탐지를 수행합니다.

### v1.0.0 - 1차 기능 범위
- ✅ **정규식 기반 PII 탐지**: 전화번호, 이메일 등 패턴 기반 탐지
- ✅ **BERT NER 모델 기반 PII 탐지**: RoBERTa를 활용한 개인정보 엔티티 인식
- ✅ **통합 차단 판단**: 탐지된 PII 기반 자동 차단 여부 결정
- ❌ **문서 업로드 기능**: 2차 개발 예정
- ❌ **유사도 분석 기능**: 2차 개발 예정

## 📁 프로젝트 구조

### 간소화된 아키텍처
```
DLP-BE/
├── app/
│   ├── main.py                    # FastAPI 애플리케이션 진입점
│   ├── api/routers/
│   │   └── pii.py                # PII 탐지 REST API
│   ├── services/
│   │   └── pii_service.py        # PII 탐지 비즈니스 로직
│   ├── ai/
│   │   ├── pii_detector.py       # RoBERTa 한국어 PII 탐지 모델
│   │   └── model_manager.py      # 모델 싱글톤 관리
│   ├── schemas/
│   │   └── pii.py                # Request/Response 스키마
│   ├── utils/
│   │   └── entity_extractor.py   # BIO 태그 엔티티 추출
│   └── core/
│       └── config.py             # 애플리케이션 설정
├── pyproject.toml                 # 의존성 관리
└── CLAUDE.md                      # 프로젝트 문서
```

### 📊 코드 품질 메트릭
- **총 Python 파일**: 약 10개 (핵심 기능만)
- **코드 라인**: 약 600줄 (주요 로직)
- **의존성**: 5개 (최소 필수 라이브러리만)
- **Python 버전**: 3.13
- **아키텍처**: Clean Architecture (간소화)

## 🚀 핵심 기능

### 1. PII 탐지 API

#### 엔드포인트
**POST** `/api/v1/pii/detect`

#### 요청
```json
{
  "text": "제 이름은 홍길동이고 전화번호는 010-1234-5678입니다"
}
```

#### 응답
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

### 2. 헬스체크 API

**GET** `/api/v1/pii/health`

모델 로딩 상태 확인

## 🔧 주요 개선사항

### ✅ 완료된 개선사항

#### 1. **모델 싱글톤 패턴 적용** (2025-08-19)
- **문제**: 매 요청마다 모델 로딩 (2-5초 지연)
- **해결**: `model_manager.py`로 싱글톤 패턴 구현
- **효과**: 첫 요청 후 응답 속도 100-300ms로 개선

#### 2. **BIO 태그 엔티티 추출 로직 완성** (2025-08-19)
- **문제**: 연속된 B-PHONE_NUM 토큰이 여러 엔티티로 분리
- **해결**: `entity_extractor.py`에서 토큰 연속성 확인 로직 추가
- **효과**: 전화번호 등이 1개 엔티티로 정확히 탐지됨

#### 3. **유사도 기능 제거** (2025-10-11)
- **이유**: 1차 개발 범위에서 제외, 정규식 + BERT NER만 집중
- **제거 항목**:
  - 문서 업로드 API (`documents.py`)
  - 유사도 분석 API (`analyze.py`)
  - 벡터 DB 연동 (`vector_repo.py`)
  - KoSimCSE 모델 (`similarity_detector.py`)
  - ChromaDB, sentence-transformers 등 불필요 의존성
- **효과**: 코드베이스 간소화, 의존성 최소화

## 📋 개발 로드맵

### Phase 1: 기본 PII 탐지 (완료) ✅
1. ✅ RoBERTa 모델 통합
2. ✅ 정규식 기반 패턴 매칭
3. ✅ BIO 태깅 정확도 개선
4. ✅ 모델 성능 최적화 (싱글톤)

### Phase 2: 확장 기능 (예정)
1. ⏳ 문서 업로드 및 파싱 (PDF, DOCX)
2. ⏳ 유사도 기반 문서 비교 (KoSimCSE)
3. ⏳ 벡터 DB 연동 (ChromaDB)
4. ⏳ 데이터베이스 통합 (PostgreSQL)

### Phase 3: 운영 준비 (예정)
1. ⏳ 단위/통합 테스트 작성
2. ⏳ 로깅 및 모니터링 시스템
3. ⏳ Rate limiting 및 보안 강화
4. ⏳ Docker 컨테이너화

## 🛠️ 기술 스택

### 현재 스택 (v1.0.0)
- **백엔드**: FastAPI + Python 3.13
- **AI 모델**: Transformers + PyTorch
- **모델**: `psh3333/roberta-large-korean-pii5`
- **패키지 관리**: uv

### 향후 추가 예정
- **데이터베이스**: PostgreSQL + SQLAlchemy 2.0
- **벡터 DB**: ChromaDB
- **유사도 모델**: KoSimCSE
- **캐싱**: Redis
- **모니터링**: Prometheus + Grafana

## 💻 개발 명령어

### 서버 실행
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 의존성 설치
```bash
uv sync
```

### API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 테스트 요청
```bash
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "제 번호는 010-1234-5678입니다"}'
```

## 📊 성능 벤치마크

### 현재 성능 (v1.0.0)
- **요청 처리 시간**: 100-300ms (모델 사전 로딩 후)
- **첫 요청**: 약 2초 (모델 로딩 포함)
- **동시 처리**: 1-2 요청 (CPU 기준)
- **처리 가능 텍스트**: 최대 512 토큰 (약 1000자)

### 목표 성능 (v2.0.0)
- **요청 처리 시간**: 50-150ms (최적화 후)
- **동시 처리**: 10-20 요청 (비동기 처리)
- **처리 가능 텍스트**: 최대 2048 토큰 (약 4000자)

## 🏗️ 아키텍처 설계

### Clean Architecture 적용
```
┌─────────────────────────────────────┐
│   API Layer (Presentation)          │  ← pii.py
├─────────────────────────────────────┤
│   Service Layer (Use Cases)         │  ← pii_service.py
├─────────────────────────────────────┤
│   AI Layer (Infrastructure)         │  ← pii_detector.py
├─────────────────────────────────────┤
│   Utils Layer (Domain)              │  ← entity_extractor.py
└─────────────────────────────────────┘
```

### 의존성 흐름
- API → Service → AI Model
- 각 레이어는 하위 레이어만 의존
- 상위 레이어 변경이 하위 레이어에 영향 없음

## 📈 종합 평가

### 현재 상태 (v1.0.0)
- ✅ **아키텍처**: 클린하고 확장 가능한 구조
- ✅ **성능**: 싱글톤 패턴으로 최적화됨
- ✅ **정확도**: BIO 태깅 로직 완성
- ✅ **간소화**: 1차 목표에 집중, 불필요한 기능 제거
- ⚠️ **테스트**: 단위 테스트 부족
- ⚠️ **운영**: 모니터링, 로깅 미흡

### 강점
1. **명확한 책임 분리**: 각 모듈이 하나의 역할만 수행
2. **최신 기술 스택**: Python 3.13, FastAPI, Transformers
3. **성능 최적화**: 모델 사전 로딩으로 빠른 응답
4. **확장 가능**: 향후 유사도 기능 추가 용이

### 개선 필요
1. **테스트 코드 작성**: 단위/통합 테스트 부족
2. **에러 처리 강화**: 더 세밀한 예외 처리 필요
3. **입력 검증**: XSS, SQL Injection 방어 강화
4. **문서화**: 코드 주석 및 API 문서 보완

## 🔐 보안 고려사항

### 현재 적용된 보안
- ✅ CORS 미들웨어 (개발 환경용)
- ✅ Pydantic 입력 검증

### 향후 추가 필요
- ⏳ Rate limiting (API 남용 방지)
- ⏳ API 키 인증
- ⏳ HTTPS 강제
- ⏳ SQL Injection 방어 (DB 연동 시)
- ⏳ XSS 방어 (HTML 태그 제거)

## 📝 개발 가이드라인

### 코드 스타일
- PEP 8 준수
- 타입 힌트 필수
- 함수 docstring 작성

### 커밋 메시지
- `feat:` 새로운 기능
- `fix:` 버그 수정
- `refactor:` 리팩토링
- `docs:` 문서 수정
- `test:` 테스트 코드

### 브랜치 전략
- `main`: 프로덕션 브랜치
- `develop`: 개발 브랜치
- `feature/*`: 기능 개발 브랜치

## 🎯 결론

**AI-TLS-DLP Backend v1.0.0**은 정규식과 BERT NER을 활용한 **정확하고 빠른 PII 탐지** 기능을 제공합니다.

1차 개발 범위에서 불필요한 기능을 제거하고 **핵심 기능에 집중**하여, 안정적이고 유지보수가 쉬운 코드베이스를 구축했습니다.

향후 2차 개발에서 문서 업로드 및 유사도 분석 기능을 추가하여 완전한 DLP 솔루션으로 발전시킬 예정입니다.