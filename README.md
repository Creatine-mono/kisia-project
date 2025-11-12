# DLP (Data Loss Prevention) - AI 기반 개인정보 탐지 및 차단 시스템

> **ChatGPT와 같은 AI 서비스 사용 시 개인정보 유출을 실시간으로 탐지하고 차단하는 통합 솔루션**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.2-black.svg)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Educational-orange.svg)]()

---

## 📖 목차

- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [시스템 구조](#시스템-구조)
- [빠른 시작](#빠른-시작)
- [접속 URL](#접속-url)
- [데모 시나리오](#데모-시나리오)
- [프로젝트 구조](#프로젝트-구조)

---

## 프로젝트 개요

**DLP (Data Loss Prevention) 시스템**은 생성형 AI 서비스(ChatGPT 등) 사용 시 발생할 수 있는 **개인정보 유출을 실시간으로 탐지하고 차단**하는 통합 보안 솔루션입니다.

### 핵심 가치
- ✅ **AI 기반 한국어 PII 탐지**: RoBERTa 모델 활용한 고정밀 개인정보 인식
- ✅ **실시간 차단**: MITM 프록시를 통한 ChatGPT 트래픽 모니터링
- ✅ **통합 관리 대시보드**: 실시간 통계, 로그 관리, 설정 조정
- ✅ **유연한 정책 관리**: PII 타입별 활성화/비활성화 및 민감도 조정

---

## 주요 기능

### 1️⃣ PII 탐지 (Backend)
- **2단계 탐지 시스템**
  - **Stage 1**: RoBERTa 기반 NER (Named Entity Recognition)
  - **Stage 2**: 정책 위반 탐지 (Policy Violation Detection)
- **탐지 항목**: 이름, 전화번호, 이메일, 주민등록번호, 주소, 신용카드, 계좌번호 등 15+ 항목
- **신뢰도 기반 필터링**: 설정 가능한 임계값 (0-100)
- **API 기반 제공**: REST API로 외부 연동 가능

### 2️⃣ 실시간 차단 (Proxy)
- **MITM 프록시**: ChatGPT 트래픽 실시간 감시
- **자동 차단**: 개인정보 포함 메시지 전송 차단
- **사용자 친화적 메시지**: 차단 사유 및 탐지 정보 상세 표시
- **로그 기록**: 모든 요청 및 차단 내역 로깅

### 3️⃣ 관리 대시보드 (Frontend)
- **Command Center**: 실시간 통계 및 시각화
- **로그 관리**: 검색, 필터링, 페이지네이션
- **설정 관리**: PII 타입별 활성화/비활성화, 민감도 조정
- **통계 분석**: 시계열 차트, IP별 통계, PII 타입별 분포

### 4️⃣ 로그 & 모니터링
- **Elasticsearch**: 대용량 로그 저장 및 검색
- **Kibana**: 고급 로그 시각화 및 분석
- **30일 로그 보관**: 자동 로그 로테이션

---

## 시스템 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                         사용자 (ChatGPT 사용)                    │
└────────────────┬────────────────────────────────────────────────┘
                 │ (프록시 설정: localhost:8080)
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  Proxy (mitmproxy)                                              │
│  ├─ ChatGPT 트래픽 가로채기                                     │
│  ├─ 프롬프트 추출                                               │
│  └─ Backend API 호출 (PII 검사)                                 │
└────────────────┬───────────────────────┬────────────────────────┘
                 │                       │
      ✅ 허용    │                       │  ❌ 차단
                 ▼                       ▼
        ┌───────────────┐       ┌───────────────────┐
        │  ChatGPT API  │       │  차단 메시지 반환  │
        └───────────────┘       └───────────────────┘
                                         │
                 ┌───────────────────────┘
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend (FastAPI)                                              │
│  ├─ PII 탐지 (RoBERTa NER)                                      │
│  ├─ 정책 위반 검사                                              │
│  ├─ Elasticsearch 로그 저장                                     │
│  └─ 관리 API 제공                                               │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  Admin Dashboard (Next.js)                                      │
│  ├─ 실시간 통계 시각화                                          │
│  ├─ 로그 검색 및 관리                                           │
│  └─ PII 설정 관리                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 빠른 시작

### 📋 사전 요구사항

#### 필수 소프트웨어
- **Docker** 20.10 이상
- **Docker Compose** v2.0 이상
- **Python** 3.13 (백엔드 및 프록시 로컬 실행용)
- **uv** (Python 패키지 매니저) - 설치: `pip install uv`

#### Mac 사용자
- **Docker Desktop** 설치 및 실행 필수
  ```bash
  # Docker Desktop이 실행 중인지 확인
  docker ps
  ```

#### 시스템 요구사항
- **RAM**: 최소 8GB (권장 16GB)
- **디스크**: 10GB 이상 여유 공간
- **포트**: 3000, 5432, 5601, 8000, 8080, 9200, 9300 포트 사용 가능

### 🚀 실행 방법 (4단계)

프로젝트는 4개의 독립적인 컴포넌트로 구성되며, 각각 별도로 실행됩니다:

#### 1단계: 백엔드 인프라 시작 (PostgreSQL, Elasticsearch, Kibana)

```bash
cd DLP-BE
docker-compose up -d
```

서비스가 시작되는 데 2-3분 소요됩니다. 다음 명령어로 상태를 확인하세요:

```bash
docker-compose ps
```

모든 서비스가 `healthy` 상태가 될 때까지 기다립니다.

#### 2단계: 백엔드 애플리케이션 시작

새 터미널 창을 열고:

```bash
cd DLP-BE

# 의존성 설치 (첫 실행 시만)
uv sync

# DB 마이그레이션 실행 (첫 실행 시만)
uv run alembic upgrade head

# 백엔드 서버 시작
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

백엔드가 시작되면 다음과 같은 메시지가 표시됩니다:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**첫 실행 시**: AI 모델(RoBERTa) 다운로드로 인해 10분가량 추가 소요될 수 있습니다.

#### 3단계: 프론트엔드 시작

새 터미널 창을 열고:

```bash
cd Admin-FE

# 프론트엔드 Docker 실행
docker-compose up -d
```

빌드가 완료되면 http://localhost:3000 에서 접속 가능합니다.

#### 4단계: 프록시 시작

새 터미널 창을 열고:

```bash
cd proxy

# 의존성 설치 (첫 실행 시만)
uv sync

# 프록시 시작
./start.sh
```

프록시가 시작되면 다음과 같은 메시지가 표시됩니다:
```
🚀 ChatGPT 프록시 시작 중...
📡 포트: 8080
```

### ⏱️ 예상 소요 시간
- **첫 실행**:
  - 백엔드 인프라: 2-3분 (Docker 이미지 다운로드)
  - 백엔드 앱: 2-3분 (AI 모델 다운로드)
  - 프론트엔드: 3-5분 (빌드)
  - 프록시: 1분
- **두 번째 실행부터**: 각 1분 이내

### 🛑 중지 방법

각 터미널에서:

```bash
# 백엔드 애플리케이션: Ctrl+C

# 백엔드 인프라 중지
cd DLP-BE
docker-compose down

# 프론트엔드 중지
cd Admin-FE
docker-compose down

# 프록시: Ctrl+C
```

---

## 접속 URL

| 서비스 | URL | 설명 |
|--------|-----|------|
| **관리자 대시보드** | http://localhost:3000 | 메인 웹 인터페이스 |
| **Backend API** | http://localhost:8000/docs | Swagger UI (API 문서) |
| **Kibana** | http://localhost:5601 | 로그 시각화 |
| **Elasticsearch** | http://localhost:9200 | 검색 엔진 API |
| **Proxy** | localhost:8080 | MITM 프록시 |

### 기본 계정
- 첫 접속 시 회원가입 후 사용
- 또는 Backend API에서 직접 사용자 생성

---

## 데모 시나리오

### 시나리오 1: 관리자 대시보드 둘러보기

1. **접속**: http://localhost:3000
2. **회원가입/로그인**
3. **Command Center**: 실시간 통계 확인
4. **Logs 페이지**: 실시간 로그 확인
5. **Detection Settings**: PII 탐지 설정 조정

### 시나리오 2: PII 탐지 API 테스트

```bash
# 개인정보 포함 텍스트 전송
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "제 이름은 홍길동이고 전화번호는 010-1234-5678입니다."
  }'
```

**예상 응답:**
```json
{
  "has_pii": true,
  "reason": "Personal information detected",
  "entities": [
    {
      "type": "PERSON",
      "value": "홍길동",
      "confidence": 0.95
    },
    {
      "type": "PHONE_NUM",
      "value": "010-1234-5678",
      "confidence": 0.98
    }
  ],
  "policy_violation": false,
  "policy_judgment": null
}
```

### 시나리오 3: ChatGPT 프록시 테스트

1. **프록시 인증서 설치**
   - 브라우저 프록시 설정: `localhost:8080`
   - http://mitm.it 접속하여 인증서 다운로드 및 설치

2. **ChatGPT 접속 및 테스트**
   - ChatGPT 접속
   - 개인정보 포함 메시지 입력 (예: "제 전화번호는 010-1234-5678입니다")
   - 차단 메시지 확인:
     ```
     🚨 요청이 차단되었습니다.

     차단 사유:
     • 개인정보 1개 탐지됨

     탐지된 개인정보:
     • PHONE_NUM: '01********' (신뢰도: 98.0%)
     ```

3. **대시보드에서 확인**
   - Logs 페이지에서 방금 차단된 요청 확인

---

## 프로젝트 구조

```
최종/
├── DLP-BE/                 # 백엔드 (FastAPI)
│   ├── app/
│   │   ├── main.py         # 앱 진입점
│   │   ├── api/routers/    # API 엔드포인트
│   │   ├── services/       # 비즈니스 로직
│   │   ├── ai/             # AI 모델 (RoBERTa)
│   │   ├── models/         # DB 모델
│   │   └── schemas/        # Pydantic 스키마
│   ├── docker-compose.yml  # PostgreSQL, Elasticsearch, Kibana
│   └── pyproject.toml      # 의존성 (uv)
│
├── Admin-FE/               # 프론트엔드 (Next.js)
│   ├── frontend/
│   │   ├── app/            # Next.js 15 App Router
│   │   ├── components/     # 57개 UI 컴포넌트
│   │   └── lib/            # API 클라이언트
│   └── docker-compose.yml  # 프론트엔드 Docker 설정
│
├── proxy/                  # 프록시 (mitmproxy)
│   ├── proxy.py            # 메인 프록시 로직
│   ├── backend.py          # 백엔드 API 클라이언트
│   ├── response.py         # 응답 생성
│   ├── start.sh            # 실행 스크립트
│   └── pyproject.toml      # 의존성 (uv)
│
├── .env                    # 환경 변수 (기본값 포함)
├── .gitignore              # Git 무시 파일
├── README.md               # 이 파일
└── CLAUDE.md               # 프로젝트 전체 아키텍처
```

### 주요 컴포넌트

#### Backend (Port 8000)
- **Framework**: FastAPI
- **AI Model**: RoBERTa (`psh3333/roberta-large-korean-pii5`)
- **Database**: PostgreSQL 15
- **Logging**: Elasticsearch 8.15.0
- **언어**: Python 3.13

#### Frontend (Port 3000)
- **Framework**: Next.js 15 (App Router)
- **UI Library**: Radix UI, shadcn/ui
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **언어**: TypeScript

#### Proxy (Port 8080)
- **Framework**: mitmproxy 12.1.1
- **역할**: ChatGPT 트래픽 실시간 감시 및 차단
- **언어**: Python 3.13

---

## 상세 문서

- **백엔드 아키텍처**: [DLP-BE/ARCHITECTURE.md](./DLP-BE/ARCHITECTURE.md)
- **프로젝트 전체 구조**: [CLAUDE.md](./CLAUDE.md)
- **테스트 가이드**: [DLP-BE/TESTING.md](./DLP-BE/TESTING.md)

---

## 기술 스택

### Backend
- Python 3.13, FastAPI 0.116+
- PyTorch 2.0+, Transformers 4.30+
- PostgreSQL 15, Elasticsearch 8.15
- SQLAlchemy (Async), Alembic
- Pydantic, JWT

### Frontend
- Next.js 15.2, React 19
- TypeScript 5
- Tailwind CSS 3.4, Radix UI
- React Hook Form, Zod
- Recharts, Three.js

### Proxy
- Python 3.13
- mitmproxy 12.1.1
- requests, Pillow

### Infrastructure
- Docker & Docker Compose

---

## 트러블슈팅

### 백엔드가 시작되지 않을 때

```bash
# PostgreSQL 확인
cd DLP-BE
docker-compose ps
docker-compose logs postgres

# Elasticsearch 확인
curl http://localhost:9200/_cluster/health?pretty

# 마이그레이션 확인
cd DLP-BE
uv run alembic current
uv run alembic upgrade head
```

### 프론트엔드 빌드 오류

```bash
cd Admin-FE
docker-compose down
docker-compose up -d --build
```

### 프록시가 요청을 차단하지 않을 때

```bash
# 백엔드 연결 확인
curl http://localhost:8000/api/v1/pii/health

# 프록시 로그 확인
cd proxy
tail -f logs/prompt_latest.json
```

### 포트가 이미 사용 중일 때

```bash
# 포트 사용 확인 (macOS)
lsof -i :8000  # 백엔드
lsof -i :3000  # 프론트엔드
lsof -i :8080  # 프록시
lsof -i :5432  # PostgreSQL
lsof -i :9200  # Elasticsearch

# 프로세스 종료
kill -9 <PID>
```

---

## 라이선스 & 용도

이 프로젝트는 **교육 및 연구 목적**으로 개발되었습니다.

- ✅ 교육용 데모 및 프레젠테이션
- ✅ 연구 및 개념 증명 (PoC)
- ✅ 내부 보안 교육

---

## 문의 & 지원

프로젝트 관련 문의사항이 있으시면 개발팀에 연락해 주세요.

---

## 주요 기능 요약

| 기능 | 설명 | 상태 |
|------|------|------|
| PII 탐지 | RoBERTa 기반 한국어 PII 인식 | ✅ |
| 정책 위반 검사 | 커스텀 정책 위반 탐지 | ✅ |
| 실시간 차단 | ChatGPT 트래픽 MITM 차단 | ✅ |
| 관리 대시보드 | 통계, 로그, 설정 관리 | ✅ |
| API 제공 | REST API 외부 연동 | ✅ |
| 로그 시각화 | Kibana 통합 | ✅ |
| Docker 지원 | 컨테이너 기반 배포 | ✅ |

---

**DLP Project - Protecting Your Privacy in the AI Era** 🛡️
