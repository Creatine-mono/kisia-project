# DLP (Data Loss Prevention) 프로젝트 전체 아키텍처

> AI 기반 개인정보 탐지 및 차단 시스템
>
> **최종 업데이트:** 2025-11-04

---

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [백엔드 (DLP-BE)](#백엔드-dlp-be)
4. [프론트엔드 (Admin-FE)](#프론트엔드-admin-fe)
5. [프록시 (Proxy)](#프록시-proxy)
6. [통합 데이터 플로우](#통합-데이터-플로우)
7. [개발 워크플로우](#개발-워크플로우)
8. [주요 파일 경로](#주요-파일-경로)

---

## 프로젝트 개요

### 시스템 명칭
- **백엔드:** AI-TLS-DLP Backend v1.2.0
- **프론트엔드:** DS MASKING AI Admin Dashboard
- **프록시:** ChatGPT PII Detection Proxy

### 핵심 기능
1. **2단계 PII 탐지**
   - Stage 1: RoBERTa 기반 NER (Named Entity Recognition)
   - Stage 2: 정책 위반 탐지 (Policy Violation Detection)

2. **실시간 모니터링 대시보드**
   - 탐지 통계 및 시각화
   - 로그 관리 및 필터링
   - PII 설정 관리

3. **ChatGPT 트래픽 차단**
   - MITM 프록시를 통한 실시간 차단
   - 개인정보 포함 요청 자동 차단
   - SSE 형식 블록 응답 생성

### 기술 스택 요약

| 컴포넌트 | 핵심 기술 |
|---------|----------|
| **백엔드** | Python 3.13, FastAPI, PostgreSQL, Elasticsearch, PyTorch, RoBERTa |
| **프론트엔드** | Next.js 15, React 19, TypeScript, Tailwind CSS, Radix UI |
| **프록시** | Python 3.13, mitmproxy 12.1.1 |
| **인프라** | Docker, Docker Compose |

---

## 시스템 아키텍처

### 전체 구성도

```
┌─────────────────────────────────────────────────────────────────┐
│                         사용자 브라우저                          │
│                      (ChatGPT 사용 중)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Proxy 설정: 127.0.0.1:8080
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MITM Proxy (Port 8080)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ proxy.py - 요청 차단 오케스트레이터                       │   │
│  │ ├─ ChatGPT 트래픽 감지                                   │   │
│  │ ├─ 프롬프트 & 파일 추출                                  │   │
│  │ └─ 백엔드 API 호출                                       │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────┬───────────────────────────────────┬────────────────┘
             │                                   │
             │                                   │
             ▼                                   ▼
┌────────────────────────────┐     ┌────────────────────────────┐
│   ChatGPT API (허용시)      │     │   DLP Backend (분석용)      │
│   chatgpt.com              │     │   Port 8000                │
└────────────────────────────┘     │                            │
                                   │ ┌────────────────────────┐ │
                                   │ │ FastAPI Application    │ │
                                   │ │ ┌──────────────────┐   │ │
                                   │ │ │ PII Detection    │   │ │
                                   │ │ │ - RoBERTa NER    │   │ │
                                   │ │ │ - Policy Check   │   │ │
                                   │ │ └──────────────────┘   │ │
                                   │ └────────────────────────┘ │
                                   │                            │
                                   │ ┌────────────────────────┐ │
                                   │ │ PostgreSQL             │ │
                                   │ │ - Users                │ │
                                   │ │ - PII Settings         │ │
                                   │ └────────────────────────┘ │
                                   │                            │
                                   │ ┌────────────────────────┐ │
                                   │ │ Elasticsearch          │ │
                                   │ │ - PII Detection Logs   │ │
                                   │ │ - 30일 보관            │ │
                                   │ └────────────────────────┘ │
                                   └────────────────────────────┘
                                                │
                                                │ API 호출
                                                ▼
                                   ┌────────────────────────────┐
                                   │   Admin Dashboard          │
                                   │   Port 3000                │
                                   │                            │
                                   │ ┌────────────────────────┐ │
                                   │ │ Next.js 15 App         │ │
                                   │ │ ├─ Command Center      │ │
                                   │ │ ├─ Logs Viewer         │ │
                                   │ │ ├─ Settings Manager    │ │
                                   │ │ └─ Statistics Charts   │ │
                                   │ └────────────────────────┘ │
                                   └────────────────────────────┘
```

### 데이터 흐름

```
1. 사용자 → ChatGPT 메시지 전송
2. Proxy → 요청 가로채기
3. Proxy → 프롬프트 & 파일 추출
4. Proxy → Backend API 호출 (POST /api/v1/pii/detect)
5. Backend → PII 분석 (RoBERTa + Policy)
6. Backend → 결과 반환 {has_pii: true/false, entities: [...]}
7. Proxy → 차단 여부 결정
   ├─ 차단: SSE 블록 메시지 생성 → 사용자
   └─ 허용: 요청 ChatGPT로 전달 → 응답 → 사용자
8. Backend → Elasticsearch 로그 저장
9. Admin Dashboard → 로그 & 통계 조회
```

---

## 백엔드 (DLP-BE)

### 디렉토리 구조

```
DLP-BE/
├── app/
│   ├── main.py                    # FastAPI 앱 진입점
│   ├── api/routers/               # API 엔드포인트 (Presentation Layer)
│   │   ├── auth.py                # 인증 (회원가입, 로그인, /me)
│   │   ├── pii.py                 # PII 탐지 (POST /detect)
│   │   ├── admin.py               # 관리자 대시보드 API
│   │   └── pii_settings.py        # PII 설정 관리
│   ├── usecases/                  # Application Layer
│   │   └── auth_usecases.py       # 인증 유즈케이스
│   ├── services/                  # Domain Layer
│   │   ├── pii_service.py         # PII 탐지 서비스 (2단계 탐지)
│   │   ├── pii_settings_service.py # 설정 관리 (캐싱)
│   │   ├── log_service.py         # 로그 서비스
│   │   └── auth/
│   │       ├── user_service.py    # 사용자 도메인 서비스
│   │       └── token_service.py   # JWT 토큰 서비스
│   ├── repository/                # Infrastructure - Data Access
│   │   ├── user_repo.py
│   │   ├── pii_settings_repo.py
│   │   └── elasticsearch_repo.py
│   ├── models/                    # SQLAlchemy Models
│   │   ├── user.py
│   │   └── pii_settings.py
│   ├── schemas/                   # Pydantic Schemas
│   │   ├── auth.py
│   │   ├── pii.py
│   │   ├── pii_settings.py
│   │   └── log.py
│   ├── ai/                        # AI 모델 관리
│   │   ├── model_manager.py       # 싱글톤 모델 매니저
│   │   ├── pii_detector.py        # RoBERTa NER (psh3333/roberta-large-korean-pii5)
│   │   └── policy_detector.py     # 정책 위반 탐지
│   ├── core/                      # Core Infrastructure
│   │   ├── config.py              # 설정 (Pydantic BaseSettings)
│   │   ├── security.py            # JWT & bcrypt
│   │   ├── dependencies.py        # FastAPI Dependencies
│   │   └── elasticsearch.py       # ES 클라이언트 싱글톤
│   ├── db/                        # Database
│   │   ├── base.py
│   │   └── session.py             # AsyncSession 관리
│   └── utils/                     # Utilities
│       ├── entity_extractor.py    # BIO 태그 엔티티 추출
│       ├── tag_parser.py
│       └── ip_utils.py
├── alembic/                       # DB Migrations
│   └── versions/
│       ├── 16a43009c50b_create_users_table.py
│       └── e31ba775f28a_create_pii_settings_table.py
├── tests/                         # 테스트 스위트
│   ├── test_pii_detection.py
│   ├── test_admin_api.py
│   └── test_elasticsearch.py
├── .env                           # 환경 변수
├── pyproject.toml                 # 의존성 (uv)
├── docker-compose.yml             # PostgreSQL, ES, Kibana
└── README.md, ARCHITECTURE.md, CLAUDE.md, TESTING.md
```

### 아키텍처 패턴: Clean Architecture

```
┌─────────────────────────────────────────────┐
│  Presentation (api/routers/)                │  ← HTTP 요청/응답
│  - Input validation (Pydantic)              │
├─────────────────────────────────────────────┤
│  Application (usecases/)                    │  ← 비즈니스 플로우 오케스트레이션
│  - 여러 서비스 조합                          │
├─────────────────────────────────────────────┤
│  Domain (services/)                         │  ← 비즈니스 로직 (프레임워크 독립적)
│  - Single Responsibility                    │
├─────────────────────────────────────────────┤
│  Infrastructure (repository/, db/, ai/)     │  ← 외부 시스템 연동
│  - DB, ES, AI 모델                          │
└─────────────────────────────────────────────┘
```

### 주요 API 엔드포인트

#### 인증 (JWT)
- `POST /api/v1/auth/register` - 회원가입
- `POST /api/v1/auth/login` - 로그인 (JWT 토큰 발급)
- `GET /api/v1/auth/me` - 현재 사용자 정보 (인증 필요)

#### PII 탐지 (인증 불필요 - 프록시용)
- `POST /api/v1/pii/detect` - PII 탐지
- `GET /api/v1/pii/health` - 헬스 체크

#### 관리자 대시보드 (인증 필요)
- `GET /api/v1/admin/logs` - 로그 조회 (필터링, 페이지네이션)
- `GET /api/v1/admin/statistics/overview` - 전체 통계
- `GET /api/v1/admin/statistics/timeline` - 시계열 분석
- `GET /api/v1/admin/statistics/by-pii-type` - PII 타입별 통계
- `GET /api/v1/admin/statistics/by-ip` - IP별 통계

#### PII 설정 관리 (인증 필요)
- `GET /api/v1/admin/pii-settings` - 모든 PII 설정 조회
- `GET /api/v1/admin/pii-settings/{entity_type}` - 특정 타입 설정 조회
- `PATCH /api/v1/admin/pii-settings/{entity_type}` - 설정 업데이트

### PII 탐지 로직 (2단계)

**Stage 1: NER 기반 PII 탐지**
```python
# pii_detector.py (RoBERTa)
Model: psh3333/roberta-large-korean-pii5
탐지 항목:
- PERSON (이름)
- PHONE_NUM (전화번호)
- EMAIL (이메일)
- ID_NUM (주민등록번호)
- ADDRESS (주소)
- CREDIT_CARD (신용카드)
- ACCOUNT (계좌번호)
- ORG (조직명)
- DATE, DATE_OF_BIRTH, AGE
- USERNAME, PASSWORD
- URL_PERSONAL

프로세스:
1. 설정 필터 적용 (enabled, threshold)
2. 토큰화 (max 512 tokens)
3. RoBERTa 추론
4. BIO 태그 → 엔티티 추출
5. has_pii=True이면 즉시 반환
```

**Stage 2: 정책 위반 탐지** (PII 없을 때만 실행)
```python
# policy_detector.py
탐지 항목:
- VIOLATION_PRIVACY_CITIZEN (개인정보 침해)
- VIOLATION_CLASSIFIED (기밀 정보)
- VIOLATION_HR (인사 정보)

반환:
- policy_judgment: "위반" / "정상"
- confidence: 0-1
```

### 데이터베이스

**PostgreSQL (Port 5432)**
```sql
-- Users 테이블
id, username (unique), email (unique), hashed_password,
full_name, is_active, is_superuser, created_at, updated_at

-- PII Settings 테이블
id, entity_type (unique), enabled (boolean),
threshold (0-100), description, created_at, updated_at
```

**Elasticsearch (Port 9200)**
```json
// pii-detection-logs 인덱스
{
  "client_ip": "192.168.1.1",
  "original_text": "검사 텍스트",
  "has_pii": true,
  "entities": [{type, value, confidence}],
  "response_time_ms": 250,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 성능 지표
- **첫 요청:** ~2초 (모델 로딩)
- **이후 요청:** 100-300ms
- **최대 텍스트:** 10,000자
- **모델 토큰 제한:** 512 tokens (~1000 한글 글자)

### 주요 설정 (.env)
```bash
DATABASE_URL=postgresql+asyncpg://admin:password123@localhost:5432/ai_tlsdlp
SECRET_KEY=your-secret-key-32chars+
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PII_MODEL_NAME=psh3333/roberta-large-korean-pii5
DEFAULT_PII_THRESHOLD=0.59
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
```

### 실행 방법
```bash
cd DLP-BE
uv sync                          # 의존성 설치
docker-compose up -d             # PostgreSQL, ES, Kibana 시작
alembic upgrade head             # DB 마이그레이션
uv run uvicorn app.main:app --reload  # 개발 서버 시작 (포트 8000)
```

### 테스트
```bash
pytest -v                        # 전체 테스트
pytest tests/test_pii_detection.py -v
pytest --cov=app --cov-report=html
```

---

## 프론트엔드 (Admin-FE)

### 디렉토리 구조

```
Admin-FE/
├── frontend/
│   ├── app/                       # Next.js 15 App Router
│   │   ├── layout.jsx             # 루트 레이아웃 (Providers)
│   │   ├── page.jsx               # 랜딩 페이지
│   │   ├── globals.css            # 글로벌 스타일 & CSS 변수
│   │   ├── login/                 # 로그인 페이지
│   │   │   └── page.jsx
│   │   └── dashboard/             # 대시보드
│   │       ├── page.jsx           # 대시보드 셸 (사이드바)
│   │       ├── command-center/    # 개요 & 통계 (440줄)
│   │       ├── logs/              # 로그 뷰어 (415줄)
│   │       ├── detection-settings/ # PII 설정 (315줄)
│   │       ├── agent-network/     # 프로젝트 관리 (553줄)
│   │       ├── operations/        # 운영 관리 (359줄)
│   │       ├── intelligence/      # 인텔리전스 (381줄)
│   │       └── systems/           # 시스템 설정 (432줄)
│   ├── components/
│   │   ├── ui/                    # 57개 UI 컴포넌트 (shadcn/ui)
│   │   │   ├── button.jsx, card.jsx, input.jsx
│   │   │   ├── dialog.jsx, dropdown-menu.jsx
│   │   │   ├── table.jsx, tabs.jsx, chart.jsx
│   │   │   └── ... (40+ 컴포넌트)
│   │   ├── gl/                    # WebGL/3D 컴포넌트
│   │   │   ├── index.jsx
│   │   │   ├── particles.jsx
│   │   │   └── shaders/
│   │   ├── header.jsx             # 메인 헤더
│   │   ├── hero.jsx               # 랜딩 히어로 (3D 배경)
│   │   ├── login-form.jsx         # 로그인 폼
│   │   ├── signup-form.jsx        # 회원가입 폼
│   │   └── theme-toggle.jsx       # 테마 토글
│   ├── contexts/
│   │   └── AuthContext.jsx        # 인증 상태 관리 (JWT)
│   ├── hooks/
│   │   ├── use-mobile.jsx         # 모바일 감지
│   │   └── use-toast.js           # 토스트 알림
│   ├── lib/
│   │   ├── api-config.js          # API 설정 중앙화
│   │   ├── api-client.dashboard.js # 대시보드 API
│   │   ├── api-client.logs.js     # 로그 API
│   │   ├── api-client.settings.js # 설정 API
│   │   └── utils.js               # 유틸 함수 (cn)
│   ├── public/                    # 정적 파일
│   ├── package.json               # 의존성
│   ├── tsconfig.json              # TypeScript 설정
│   ├── tailwind.config.js         # Tailwind 설정
│   ├── next.config.mjs            # Next.js 설정
│   ├── Dockerfile                 # 프로덕션 이미지
│   └── Dockerfile.dev             # 개발 이미지
├── docker-compose.yml             # Docker Compose
├── env.example                    # 환경 변수 예제
└── openapi.json                   # 백엔드 API 스펙
```

### 기술 스택

**코어**
- Next.js 15.2.4 (App Router)
- React 19
- TypeScript 5
- Tailwind CSS 3.4.17

**UI 라이브러리**
- Radix UI (40+ 접근성 컴포넌트)
- shadcn/ui (커스터마이징 가능)
- Lucide React (아이콘)
- Recharts (차트)

**3D 그래픽**
- Three.js 0.180.0
- React Three Fiber
- @react-three/drei
- Custom GLSL shaders

**폼 & 검증**
- React Hook Form 7.54.1
- Zod 3.24.1

### 라우팅 구조 (App Router)

```
/                          → 랜딩 페이지 (3D 히어로)
/login                     → 로그인 페이지
/dashboard                 → 대시보드 셸
  ├─ command-center        → 개요 통계 (인페이지 렌더링)
  ├─ logs                  → 로그 뷰어
  ├─ detection-settings    → PII 설정
  ├─ agent-network         → 프로젝트 관리
  ├─ operations            → 운영 관리
  ├─ intelligence          → 인텔리전스
  └─ systems               → 시스템 설정
```

**특징:** 대시보드는 단일 페이지 셸로 조건부 렌더링 사용 (전통적인 중첩 라우팅 대신)

### 상태 관리

**Context API 패턴**
- **AuthContext** (`/contexts/AuthContext.jsx`)
  - `isLoggedIn`, `accessToken`, `loginWithToken()`, `logout()`
  - localStorage에 JWT 토큰 저장
  - 루트 레이아웃에서 전체 앱 래핑

**로컬 상태**
- 각 페이지 컴포넌트가 자체 데이터 페칭 및 UI 상태 관리
- Redux/Zustand 사용 안 함 (의도적으로 간단하게 유지)

### API 통합

**중앙 설정** (`/lib/api-config.js`)
```javascript
// 환경 기반 API URL
NEXT_PUBLIC_API_URL = http://localhost:8000 (기본값)

// 자동 JWT 토큰 주입 (localStorage)
// 401 에러 시 자동 로그아웃
// 에러 핸들링

apiConfig.endpoints = {
  auth: { login, me },
  logs: { list },
  dashboard: { overview, timeline, byPiiType, byIp },
  settings: { list, detail, update }
}
```

**API 클라이언트 모듈**
- `api-client.dashboard.js` - 통계 데이터
- `api-client.logs.js` - 로그 조회
- `api-client.settings.js` - PII 설정 관리

### 테마 시스템

**Light Mode (따뜻한 베이지 톤)**
- Background: 베이지 (40° 20% 94%)
- Primary: 밝은 앰버/골드 (45° 100% 50%)

**Dark Mode (블랙 + 앰버 액센트)**
- Background: 순수 블랙 (0% 0% 0%)
- Primary: 밝은 앰버/골드 (45° 100% 50%)

**테마 전환**
- `next-themes` 사용
- 기본: 랜딩 페이지 다크, 대시보드 라이트
- ThemeToggle 컴포넌트로 전환

### 주요 페이지 기능

**1. Command Center (개요 대시보드)**
- 실시간 PII 탐지 통계
- 타임라인 차트 (시간별/일별)
- IP별 통계
- PII 타입 분포
- 최근 로그 요약

**2. Logs Page**
- 페이지네이션 (20개/페이지)
- IP 주소 검색
- PII 타입 필터
- 시간 범위 필터
- 정렬 가능한 컬럼

**3. Detection Settings**
- PII 탐지 규칙 설정
- 타입별 on/off 토글
- 민감도 임계값 조정 (0-100)
- 실시간 백엔드 업데이트

### Docker 설정

**프로덕션 Dockerfile**
- Multi-stage 빌드 최적화
- Next.js standalone 출력
- Node Alpine 베이스 이미지
- 런타임 환경 변수 주입

**개발 설정** (`docker-compose.dev.yml`)
- 핫 리로드 (볼륨 마운트)
- 포트 3000
- 백엔드 URL 환경 변수

### 실행 방법
```bash
cd Admin-FE/frontend
npm install
npm run dev              # 개발 서버 (포트 3000)
npm run build            # 프로덕션 빌드
npm run start            # 프로덕션 서버

# Docker
cd Admin-FE
docker-compose -f docker-compose.dev.yml up
```

---

## 프록시 (Proxy)

### 디렉토리 구조

```
proxy/
├── proxy.py               # 메인 MITM 프록시 애드온 (12KB)
├── config.py              # 설정 관리 (3.4KB)
├── backend.py             # 백엔드 API 클라이언트 (16KB)
├── extractor.py           # 데이터 추출 모듈 (9.6KB)
├── response.py            # 응답 생성 (10KB)
├── logger.py              # 로깅 관리 (4.6KB)
├── streaming.py           # 스트리밍 핸들러 (3.8KB, 비활성화)
├── run_proxy.py           # 실행 스크립트 (1.7KB)
├── init_certs.py          # SSL 인증서 초기화 (2.5KB)
├── start.sh               # 셸 시작 스크립트
├── pyproject.toml         # 의존성 (uv)
├── Dockerfile             # 컨테이너 설정
├── README.md              # 문서
└── logs/                  # 로그 디렉토리
    ├── prompt_*.json      # 요청 로그
    └── blocked/           # 차단된 요청 로그
```

### 핵심 기술
- **Python 3.13**
- **mitmproxy 12.1.1** (MITM 프레임워크)
- **requests** (HTTP 클라이언트)
- **Pillow** (이미지 처리)

### 주요 컴포넌트

**1. proxy.py - 메인 프록시 애드온**
```python
class SemanticProxy:
    - request(flow) → HTTP 요청 핸들러
    - _handle_stream_request(flow) → 대화 요청 처리
    - _handle_upload(flow) → 파일 업로드 처리
    - _extract_request_data(flow) → 데이터 추출
    - _add_browser_headers(flow) → Cloudflare 우회 헤더
```

**2. config.py - 설정 관리**
```python
# 백엔드 API
BACKEND_URL = http://127.0.0.1:8000
BACKEND_TIMEOUT = 30
BACKEND_RETRY = 2

# 타겟 호스트 (Regex)
TARGET_HOSTS = r"(chatgpt\.com|ab\.chatgpt\.com|...)"

# 차단 설정
BLOCK_MESSAGE = "민감정보가 탐지되어 요청이 차단되었습니다"
BLOCK_ON_BACKEND_ERROR = 0  # 백엔드 다운 시 허용

# 로깅
LOG_DIR = ./logs
LOG_MAX = 1000
LOG_ROTATE = 1
```

**3. backend.py - 백엔드 API 클라이언트**
```python
class BackendClient:
    - comprehensive_analysis(prompt, files_data, metadata)
      → POST /api/v1/analyze/comprehensive
      → (should_block: bool, reason: str, details: dict)

    - check_content(prompt, files_data, metadata)
      → POST /api/v1/pii/detect (레거시)

    - process_file(file_bytes, filename, content_type)
      → POST /api/v1/file/process (미래 구현)

    - health_check()
      → GET /api/v1/pii/health

# 재시도 로직, 타임아웃, Rate Limit 핸들링
```

**4. extractor.py - 데이터 추출**
```python
class DataExtractor:
    - is_stream_request(flow) → 대화 요청 감지
    - is_upload_request(flow) → 업로드 감지
    - extract_prompt_from_json(body) → 프롬프트 추출
    - extract_base64_images(body) → 인라인 이미지 디코딩
    - extract_cdn_urls(body) → CDN URL 추출
    - parse_multipart(raw_bytes, content_type) → Multipart 파싱
```

**5. response.py - 응답 생성**
```python
class ResponseGenerator:
    - create_sse_block_response(flow, message, parent_info, details)
      → ChatGPT 호환 SSE 형식 차단 응답 생성

    - _build_chatgpt_payload()
      → message.id, author.role, content.parts, status

    - format_comprehensive_analysis_message(analysis_result)
      → 사용자 친화적 차단 메시지 생성
```

**6. logger.py - 로깅**
```python
class ProxyLogger:
    - log_request() → 일반 요청 로깅 (JSONL)
    - log_blocked_request() → 차단 요청 로깅
    - cleanup_old_logs(days=30) → 로그 로테이션

# 로그 구조
logs/
├── prompt_2024-01-01.jsonl
├── prompt_latest.json
└── blocked/
    └── blocked_2024-01-01.jsonl
```

### 요청 처리 플로우

```
1. 사용자 브라우저
   POST /backend-api/conversation (ChatGPT)
        ↓
2. MITM Proxy (proxy.py)
   - request() 메서드
   - ChatGPT 도메인 체크 (TARGET_HOSTS 정규식)
   - 요청 타입 판별
     ├─ UPLOAD → _handle_upload()
     └─ STREAM → _handle_stream_request()
        ↓
3. _handle_stream_request()
   - 요청 바디 디코딩
   - _extract_request_data() 호출
     ├─ JSON 파싱
     ├─ messages 배열에서 프롬프트 추출
     ├─ base64 이미지 추출
     └─ CDN URL 추출
   - backend.comprehensive_analysis() 호출
        ↓
4. Backend API Client (backend.py)
   POST /api/v1/analyze/comprehensive
   - 재시도 로직 (2회)
   - 타임아웃: 5s 연결, 30s 읽기
   - Rate Limit 핸들링
   → {blocked, block_reasons, details}
        ↓
5. Response Generation (response.py)
   - 차단 시:
     ├─ SSE 차단 응답 생성
     ├─ ChatGPT 메시지 형식
     └─ blocked/ 디렉토리 로깅
   - 허용 시:
     ├─ 브라우저 헤더 추가 (Cloudflare 우회)
     ├─ 원본 요청 ChatGPT로 전달
     └─ 일반 로그 기록
        ↓
6. 브라우저 응답
   - ChatGPT 응답 (허용) 또는 차단 메시지 (차단)
```

### 타겟 호스트 필터링

```python
TARGET_HOSTS = r"(chatgpt\.com|ab\.chatgpt\.com|ws\.chatgpt\.com|oaiusercontent\.com|upload\.openai\.com)"

비ChatGPT 트래픽 → 무시 (통과)
```

### 요청 라우트 필터링

```
ChatGPT 도메인 요청
├─ /backend-api/files → 업로드 (차단 안 함)
├─ /backend-api/attachments → 업로드 (차단 안 함)
├─ /backend-api/conversation → 스트림 (검사)
├─ /backend-api/conversation/* → 스트림 (검사)
├─ /backend-anon/conversation → 스트림 (검사)
├─ /backend-api/sse/* → 스트림 (검사)
└─ 기타 → 통과
```

### Cloudflare 우회 헤더

```python
# 허용 시 추가되는 헤더
User-Agent: Mozilla/5.0 ... Chrome/120.0.0.0
Accept: text/html,application/xhtml+xml,...
Accept-Language: ko-KR,ko;q=0.9,en;q=0.8
Accept-Encoding: gzip, deflate, br
Sec-CH-UA: "Not_A Brand";v="8", "Chromium";v="120", ...
Referer: https://chatgpt.com/...
```

### 백엔드 API 인터페이스

**종합 분석 엔드포인트**
```
POST /api/v1/analyze/comprehensive

Request:
{
  "text": "사용자 프롬프트 + 파일 텍스트 결합"
}

Response (200):
{
  "blocked": true/false,
  "block_reasons": ["pii_detected", "similarity_detected"],
  "pii_analysis": {
    "has_pii": true,
    "total_entities": 3,
    "entities": [
      {
        "type": "PHONE_NUMBER",
        "value": "010-xxxx-xxxx",
        "confidence": 0.95
      }
    ]
  },
  "similarity_analysis": {...}
}
```

### Fallback 동작 (백엔드 다운 시)

| BLOCK_ON_BACKEND_ERROR | 동작 |
|------------------------|------|
| 1 | 모든 요청 차단 (안전 기본값) |
| 0 | 모든 요청 허용 (서비스 가용성) |

**재시도 전략:**
- 시도: 2회 (설정 가능)
- 백오프: 0.5초, 1초
- 타임아웃: 5초 연결, 30초 읽기

### 로그 구조

**요청 로그 예시**
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "epoch": 1704110400,
  "client_ip": "192.168.1.100",
  "host": "chatgpt.com",
  "prompt": "사용자 입력...",
  "files_count": 1,
  "should_block": false,
  "reason": "analysis_passed",
  "status": "allowed"
}
```

**차단 요청 로그 예시**
```json
{
  "timestamp": "2024-01-01T12:05:00Z",
  "epoch": 1704110700,
  "client_ip": "192.168.1.100",
  "host": "chatgpt.com",
  "prompt": "민감한 내용...",
  "files_count": 0,
  "reason": "pii_detected",
  "details": {
    "message": "🚨 요청이 차단되었습니다.",
    "pii_entities": [...]
  }
}
```

### 실행 방법

```bash
cd proxy
uv sync                  # 의존성 설치

# 방법 1: Shell 스크립트
./start.sh

# 방법 2: Python 스크립트
python run_proxy.py

# 방법 3: 직접 실행
mitmdump --set termlog_verbosity=error --ssl-insecure -p 8080 -s proxy.py

# 백엔드 연결 확인
curl http://127.0.0.1:8000/api/v1/pii/health

# 로그 모니터링
tail -f logs/prompt_latest.json
tail -f logs/blocked/blocked_*.jsonl
```

### 성능 특성
- **지연 시간:** +200-500ms (백엔드 호출)
- **처리량:** 백엔드 분석 속도에 제한됨
- **메모리:** ~50-100MB (Python 프로세스)
- **CPU:** 낮음 (I/O 바운드)

---

## 통합 데이터 플로우

### 전체 시스템 플로우

```
┌─────────────────────────────────────────────────────────────────┐
│ 시나리오: 사용자가 ChatGPT에 개인정보 포함 메시지 전송          │
└─────────────────────────────────────────────────────────────────┘

[1] 사용자 브라우저
    → "안녕하세요, 제 전화번호는 010-1234-5678입니다."
    → POST https://chatgpt.com/backend-api/conversation
    → Proxy: 127.0.0.1:8080으로 설정됨

[2] Proxy (proxy.py)
    → request(flow) 메서드 실행
    → TARGET_HOSTS 정규식 매칭: chatgpt.com ✅
    → 요청 타입 판별: STREAM ✅
    → _handle_stream_request(flow) 실행
    → _extract_request_data(flow) 호출
       ├─ JSON 파싱: {"messages": [...]}
       ├─ 프롬프트 추출: "안녕하세요, 제 전화번호는 010-1234-5678입니다."
       └─ 파일: 없음

[3] Backend Client (backend.py)
    → comprehensive_analysis() 호출
    → POST http://127.0.0.1:8000/api/v1/analyze/comprehensive
    → Request Body: {"text": "안녕하세요, 제 전화번호는 010-1234-5678입니다."}
    → Timeout: 5s 연결, 30s 읽기
    → Retry: 최대 2회

[4] DLP Backend (DLP-BE)
    → FastAPI Router (pii.py)
       └─ POST /api/v1/pii/detect 핸들러

    → PII Service (pii_service.py)
       ├─ Stage 1: PII Detection
       │  └─ pii_detector.py (RoBERTa)
       │     ├─ 토큰화: "안녕하세요 , 제 전화번호 는 010 - 1234 - 5678 입니다 ."
       │     ├─ RoBERTa 추론
       │     ├─ BIO 태그: O O O B-PHONE_NUM I-PHONE_NUM I-PHONE_NUM I-PHONE_NUM I-PHONE_NUM O O
       │     ├─ 엔티티 추출: {type: "PHONE_NUM", value: "010-1234-5678", confidence: 0.98}
       │     └─ has_pii = True → 즉시 반환
       │
       └─ (Stage 2: Policy Detection 건너뜀 - PII 발견됨)

    → Log Service (log_service.py)
       └─ Elasticsearch에 로그 저장
          POST http://localhost:9200/pii-detection-logs/_doc
          {
            "client_ip": "127.0.0.1",
            "original_text": "안녕하세요, 제 전화번호는...",
            "has_pii": true,
            "entities": [{type: "PHONE_NUM", ...}],
            "response_time_ms": 150,
            "timestamp": "2024-01-01T12:00:00Z"
          }

    → Response:
       {
         "has_pii": true,
         "reason": "Personal information detected",
         "details": "Phone number detected",
         "entities": [
           {
             "type": "PHONE_NUM",
             "value": "010-1234-5678",
             "start": 15,
             "end": 28,
             "confidence": 0.98
           }
         ]
       }

[5] Backend Client (backend.py)
    → 응답 수신: HTTP 200
    → should_block = true
    → reason = "pii_detected"
    → details = {...}
    → 반환: (True, "pii_detected", {...})

[6] Proxy (proxy.py)
    → Response Generator (response.py)
       └─ create_sse_block_response() 호출
          ├─ ChatGPT 메시지 구조 생성
          │  {
          │    "message": {
          │      "id": "msg_abc123",
          │      "author": {"role": "assistant"},
          │      "content": {
          │        "parts": ["🚨 요청이 차단되었습니다.\n\n사유: 개인정보 탐지됨\n\n탐지된 정보:\n- PHONE_NUMBER: '010-xxxx-xxxx' (신뢰도: 98.0%)"]
          │      },
          │      "status": "finished_successfully",
          │      "create_time": 1704110400
          │    },
          │    "conversation_id": "...",
          │    "parent": "..."
          │  }
          │
          └─ SSE 형식 변환:
             data: {"message": {...}}

             data: [DONE]


    → Logger (logger.py)
       ├─ log_request() → logs/prompt_2024-01-01.jsonl
       └─ log_blocked_request() → logs/blocked/blocked_2024-01-01.jsonl

    → flow.response 설정
       ├─ Status: 200
       ├─ Content-Type: text/event-stream
       └─ Body: SSE 데이터

[7] 사용자 브라우저
    → ChatGPT UI에 표시:
       🚨 요청이 차단되었습니다.

       사유: 개인정보 탐지됨

       탐지된 정보:
       - PHONE_NUMBER: '010-xxxx-xxxx' (신뢰도: 98.0%)

[8] Admin Dashboard (선택적 조회)
    → 관리자가 대시보드 접속: http://localhost:3000/dashboard
    → Command Center 페이지
       └─ API 호출: GET /api/v1/admin/statistics/overview
          → Backend → Elasticsearch 쿼리
          → 응답:
             {
               "total_requests": 1234,
               "pii_detection_rate": 12.5,
               "blocked_requests": 154,
               "top_pii_types": [
                 {"type": "PHONE_NUM", "count": 89},
                 ...
               ]
             }

    → Logs 페이지
       └─ API 호출: GET /api/v1/admin/logs?has_pii=true&page=1&page_size=20
          → Backend → Elasticsearch 검색
          → 방금 차단된 요청 포함 로그 반환
             [{
               "timestamp": "2024-01-01T12:00:00Z",
               "client_ip": "127.0.0.1",
               "original_text": "안녕하세요, 제 전화번호는...",
               "has_pii": true,
               "entities": [...]
             }]
```

### 성공적인 요청 플로우 (PII 없음)

```
[1] 사용자: "오늘 날씨가 어떤가요?"
[2] Proxy: 프롬프트 추출
[3] Backend API: POST /api/v1/pii/detect
[4] DLP Backend:
    - Stage 1: PII Detection → has_pii = false
    - Stage 2: Policy Detection → policy_judgment = "정상"
    - Response: {has_pii: false, reason: "No PII detected"}
[5] Backend Client: should_block = false
[6] Proxy:
    - _add_browser_headers(flow) 실행 (Cloudflare 우회)
    - 원본 요청 ChatGPT로 전달
    - log_request() 기록 (status: "allowed")
[7] ChatGPT API: 정상 응답 생성
[8] 사용자: ChatGPT 응답 수신 ✅
```

---

## 개발 워크플로우

### 로컬 개발 환경 설정

**1. 백엔드 시작**
```bash
cd DLP-BE
uv sync
docker-compose up -d           # PostgreSQL, Elasticsearch, Kibana
alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

**2. 프론트엔드 시작**
```bash
cd Admin-FE/frontend
npm install
npm run dev                    # 포트 3000
```

**3. 프록시 시작**
```bash
cd proxy
uv sync
./start.sh                     # 포트 8080
```

**4. 서비스 확인**
- 백엔드: http://localhost:8000/docs (Swagger UI)
- 프론트엔드: http://localhost:3000
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601

### 브라우저 프록시 설정

**Chrome/Edge (macOS)**
```
System Preferences → Network → Advanced → Proxies
├─ HTTP Proxy: 127.0.0.1:8080
└─ HTTPS Proxy: 127.0.0.1:8080
```

**mitmproxy 인증서 설치**
```bash
# 브라우저에서 http://mitm.it 접속
# macOS: Download mitmproxy-ca-cert.pem
# 키체인 접근 → 인증서 추가 → 항상 신뢰
```

### 테스트 워크플로우

**1. 백엔드 테스트**
```bash
cd DLP-BE
pytest -v
pytest tests/test_pii_detection.py -v
pytest --cov=app --cov-report=html
```

**2. PII 탐지 테스트 (수동)**
```bash
# 터미널에서 직접 호출
curl -X POST http://localhost:8000/api/v1/pii/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "제 전화번호는 010-1234-5678입니다"}'

# 예상 응답
{
  "has_pii": true,
  "reason": "Personal information detected",
  "entities": [
    {
      "type": "PHONE_NUM",
      "value": "010-1234-5678",
      "confidence": 0.98
    }
  ]
}
```

**3. 프록시 테스트**
```bash
# 프록시 로그 모니터링
tail -f proxy/logs/prompt_latest.json

# ChatGPT에서 테스트 메시지 전송
# → 로그 파일에 요청 기록 확인
```

**4. 프론트엔드 테스트**
- 브라우저: http://localhost:3000
- 로그인 → Dashboard → Command Center
- 통계 데이터 표시 확인

### 데이터베이스 마이그레이션

**새 마이그레이션 생성**
```bash
cd DLP-BE
alembic revision --autogenerate -m "설명"
alembic upgrade head
```

**롤백**
```bash
alembic downgrade -1
```

### Docker 개발 환경

**전체 스택 실행 (권장)**
```bash
# 백엔드
cd DLP-BE
docker-compose up -d

# 프론트엔드
cd Admin-FE
docker-compose -f docker-compose.dev.yml up

# 프록시
cd proxy
docker build -t dlp-proxy .
docker run -p 8080:8080 dlp-proxy
```

### 로그 & 디버깅

**백엔드 로그**
```bash
# Uvicorn 로그 (콘솔)
uv run uvicorn app.main:app --reload --log-level debug

# Elasticsearch 로그 확인
curl http://localhost:9200/pii-detection-logs/_search?pretty
```

**프록시 로그**
```bash
# 모든 요청
cat proxy/logs/prompt_2024-01-01.jsonl | jq

# 차단된 요청만
cat proxy/logs/blocked/blocked_2024-01-01.jsonl | jq

# 실시간 모니터링
tail -f proxy/logs/prompt_latest.json | jq
```

**프론트엔드 로그**
```bash
# 브라우저 콘솔
# Next.js 서버 로그 (터미널)
npm run dev
```

---

## 주요 파일 경로

### 백엔드 (DLP-BE)

**핵심 파일**
- `/DLP-BE/app/main.py` - FastAPI 앱 진입점
- `/DLP-BE/app/core/config.py` - 설정
- `/DLP-BE/.env` - 환경 변수

**API 엔드포인트**
- `/DLP-BE/app/api/routers/auth.py` - 인증 API
- `/DLP-BE/app/api/routers/pii.py` - PII 탐지 API
- `/DLP-BE/app/api/routers/admin.py` - 관리자 API
- `/DLP-BE/app/api/routers/pii_settings.py` - PII 설정 API

**AI 모델**
- `/DLP-BE/app/ai/model_manager.py` - 싱글톤 모델 매니저
- `/DLP-BE/app/ai/pii_detector.py` - RoBERTa PII 탐지기
- `/DLP-BE/app/ai/policy_detector.py` - 정책 위반 탐지기

**서비스**
- `/DLP-BE/app/services/pii_service.py` - PII 탐지 비즈니스 로직
- `/DLP-BE/app/services/pii_settings_service.py` - 설정 관리 (캐싱)
- `/DLP-BE/app/services/log_service.py` - 로그 서비스
- `/DLP-BE/app/services/auth/user_service.py` - 사용자 서비스
- `/DLP-BE/app/services/auth/token_service.py` - JWT 서비스

**데이터베이스**
- `/DLP-BE/app/models/user.py` - User 모델
- `/DLP-BE/app/models/pii_settings.py` - PII Settings 모델
- `/DLP-BE/app/db/session.py` - AsyncSession 관리
- `/DLP-BE/alembic/versions/` - DB 마이그레이션

**문서**
- `/DLP-BE/README.md` - 프로젝트 개요
- `/DLP-BE/ARCHITECTURE.md` - 아키텍처 가이드
- `/DLP-BE/CLAUDE.md` - 개발 가이드
- `/DLP-BE/TESTING.md` - 테스트 가이드

### 프론트엔드 (Admin-FE)

**핵심 파일**
- `/Admin-FE/frontend/app/layout.jsx` - 루트 레이아웃
- `/Admin-FE/frontend/app/page.jsx` - 랜딩 페이지
- `/Admin-FE/frontend/app/globals.css` - 글로벌 스타일

**대시보드 페이지**
- `/Admin-FE/frontend/app/dashboard/page.jsx` - 대시보드 셸
- `/Admin-FE/frontend/app/dashboard/command-center/page.jsx` - 개요 통계
- `/Admin-FE/frontend/app/dashboard/logs/page.jsx` - 로그 뷰어
- `/Admin-FE/frontend/app/dashboard/detection-settings/page.jsx` - PII 설정

**API 통합**
- `/Admin-FE/frontend/lib/api-config.js` - API 설정
- `/Admin-FE/frontend/lib/api-client.dashboard.js` - 대시보드 API
- `/Admin-FE/frontend/lib/api-client.logs.js` - 로그 API
- `/Admin-FE/frontend/lib/api-client.settings.js` - 설정 API

**컴포넌트**
- `/Admin-FE/frontend/components/ui/` - 57개 UI 컴포넌트
- `/Admin-FE/frontend/components/header.jsx` - 헤더
- `/Admin-FE/frontend/components/login-form.jsx` - 로그인 폼

**상태 관리**
- `/Admin-FE/frontend/contexts/AuthContext.jsx` - 인증 컨텍스트

**설정**
- `/Admin-FE/frontend/next.config.mjs` - Next.js 설정
- `/Admin-FE/frontend/tailwind.config.js` - Tailwind 설정
- `/Admin-FE/frontend/tsconfig.json` - TypeScript 설정
- `/Admin-FE/frontend/package.json` - 의존성

**Docker**
- `/Admin-FE/frontend/Dockerfile` - 프로덕션 이미지
- `/Admin-FE/frontend/Dockerfile.dev` - 개발 이미지
- `/Admin-FE/docker-compose.yml` - Docker Compose

### 프록시 (Proxy)

**핵심 파일**
- `/proxy/proxy.py` - 메인 프록시 애드온 (12KB)
- `/proxy/config.py` - 설정 관리 (3.4KB)
- `/proxy/backend.py` - 백엔드 API 클라이언트 (16KB)
- `/proxy/extractor.py` - 데이터 추출 (9.6KB)
- `/proxy/response.py` - 응답 생성 (10KB)
- `/proxy/logger.py` - 로깅 (4.6KB)

**실행 스크립트**
- `/proxy/run_proxy.py` - Python 실행 스크립트
- `/proxy/start.sh` - Shell 시작 스크립트

**설정**
- `/proxy/pyproject.toml` - 의존성 (uv)
- `/proxy/Dockerfile` - 컨테이너 설정

**로그**
- `/proxy/logs/prompt_*.jsonl` - 일별 요청 로그
- `/proxy/logs/blocked/blocked_*.jsonl` - 차단 요청 로그
- `/proxy/logs/prompt_latest.json` - 최신 로그

---

## 추가 정보

### 포트 매핑

| 서비스 | 포트 | 용도 |
|--------|------|------|
| DLP Backend | 8000 | FastAPI 앱 |
| PostgreSQL | 5432 | 사용자 & 설정 DB |
| Elasticsearch | 9200 | 로그 저장 & 검색 |
| Kibana | 5601 | 로그 시각화 |
| Admin Dashboard | 3000 | Next.js 앱 |
| Proxy | 8080 | mitmproxy |

### 환경 변수 요약

**DLP-BE (.env)**
```bash
DATABASE_URL=postgresql+asyncpg://admin:password123@localhost:5432/ai_tlsdlp
SECRET_KEY=your-secret-key-32chars+
ACCESS_TOKEN_EXPIRE_MINUTES=30
PII_MODEL_NAME=psh3333/roberta-large-korean-pii5
DEFAULT_PII_THRESHOLD=0.59
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
```

**Admin-FE (.env)**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Proxy (환경 변수)**
```bash
BACKEND_API_URL=http://127.0.0.1:8000
PROXY_DEBUG=1
BLOCK_ON_BACKEND_ERROR=0
```

### 보안 고려사항

1. **JWT 토큰**
   - 만료 시간: 30분 (프로덕션 권장: 15분)
   - Refresh Token 미구현 (향후 추가 필요)

2. **HTTPS**
   - 프로덕션: HTTPS 강제 필요
   - mitmproxy: SSL 인증서 관리

3. **API 인증**
   - 백엔드: JWT Bearer 토큰
   - 프록시: 선택적 API Key (X-API-Key)

4. **데이터 프라이버시**
   - 로그 보관: 30일 (설정 가능)
   - 원본 텍스트 저장됨 (암호화 권장)
   - 프록시-백엔드 간 암호화 없음 (VPN 권장)

### 성능 최적화

1. **백엔드**
   - 모델 프리로드 (첫 요청 2초 → 이후 100-300ms)
   - PII 설정 인메모리 캐싱
   - Async/Await 전체 적용

2. **프론트엔드**
   - Next.js standalone 출력 (Docker 최적화)
   - 이미지 최적화 비활성화 (빠른 빌드)
   - CSS purging (Tailwind)

3. **프록시**
   - 재시도 로직 (2회)
   - 타임아웃: 5s 연결, 30s 읽기
   - 스트리밍 비활성화 (안정성 우선)

### 향후 개선 사항

**백엔드**
- [ ] Rate Limiting 구현
- [ ] API Key 인증 추가
- [ ] Refresh Token 구현
- [ ] 모델 성능 최적화 (10-20 동시 요청)
- [ ] 로그 암호화

**프론트엔드**
- [ ] 실시간 업데이트 (WebSocket)
- [ ] CSV 내보내기
- [ ] 고급 필터링 (날짜 범위 프리셋)
- [ ] 사용자 권한 관리

**프록시**
- [ ] 파일 처리 완전 구현 (OCR, PDF 파싱)
- [ ] 스트리밍 재활성화
- [ ] Exponential backoff 개선
- [ ] 프록시-백엔드 암호화 (TLS)
- [ ] 클러스터링 지원

---

## 문제 해결

### 백엔드가 시작되지 않을 때
```bash
# PostgreSQL 확인
docker-compose ps
docker-compose logs postgres

# Elasticsearch 확인
curl http://localhost:9200/_cluster/health?pretty

# 마이그레이션 확인
alembic current
alembic upgrade head

# 의존성 재설치
uv sync --reinstall
```

### 프론트엔드 빌드 오류
```bash
# node_modules 삭제 및 재설치
rm -rf node_modules package-lock.json
npm install

# Next.js 캐시 삭제
rm -rf .next

# TypeScript 오류 무시 (개발 중)
# next.config.mjs에서 ignoreBuildErrors: true 확인
```

### 프록시가 요청을 차단하지 않을 때
```bash
# 백엔드 연결 확인
curl http://127.0.0.1:8000/api/v1/pii/health

# 프록시 로그 확인
tail -f logs/prompt_latest.json

# 브라우저 프록시 설정 확인
# System Preferences → Network → Proxies

# mitmproxy 인증서 확인
# http://mitm.it 접속 → 인증서 다운로드 및 신뢰 설정
```

### Elasticsearch 연결 오류
```bash
# Elasticsearch 상태 확인
curl http://localhost:9200/_cat/health?v

# 인덱스 확인
curl http://localhost:9200/_cat/indices?v

# Docker 컨테이너 재시작
docker-compose restart elasticsearch

# 로그 확인
docker-compose logs elasticsearch
```

---

**마지막 업데이트:** 2025-11-04
**작성자:** Claude (Anthropic)
**프로젝트:** DLP (Data Loss Prevention) System
