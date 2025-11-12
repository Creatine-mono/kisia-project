# DS MASKING AI - Next.js 프론트엔드 프로젝트 분석

## 프로젝트 개요

DS MASKING AI는 개인정보 탐지 및 보호를 위한 실시간 모니터링 대시보드입니다. NER(Named Entity Recognition) 및 컨텍스트 기반 탐지 기술을 활용하여 민감한 개인정보를 자동으로 식별하고 차단하는 관리자용 프론트엔드 애플리케이션입니다.

**버전**: 0.1.0  
**프레임워크**: Next.js 15.2.4 (App Router)  
**프로젝트 상태**: 오픈소스 프로젝트 (KISIA)

---

## 1. 프로젝트 구조

### 디렉토리 구조

```
frontend/
├── app/                          # Next.js App Router 기반 페이지
│   ├── dashboard/                # 대시보드 메인 섹션
│   │   ├── command-center/       # 개인정보 탐지 현황 대시보드
│   │   ├── agent-network/        # 프로젝트 관리 (미개발)
│   │   ├── operations/           # 운영 관리 (미개발)
│   │   ├── intelligence/         # 인텔리전스 분석 (미개발)
│   │   ├── systems/              # 시스템 설정 (미개발)
│   │   ├── logs/                 # 전체 로그 페이지
│   │   ├── detection-settings/   # 탐지 기능 설정
│   │   └── page.jsx              # 대시보드 메인 레이아웃
│   ├── login/                    # 로그인 페이지
│   ├── layout.jsx                # 루트 레이아웃 (전역 설정)
│   ├── page.jsx                  # 랜딩 페이지
│   └── globals.css               # 전역 스타일
├── components/                   # 컴포넌트 라이브러리
│   ├── ui/                       # 재사용 가능한 UI 컴포넌트 (68개+)
│   ├── gl/                       # WebGL/3D 컴포넌트
│   ├── hero.jsx                  # 히어로 섹션
│   ├── header.jsx                # 헤더 컴포넌트
│   ├── login-form.jsx            # 로그인 폼
│   ├── theme-toggle.jsx          # 테마 전환 버튼
│   └── spline-scene.jsx          # 3D 씬 컴포넌트
├── contexts/                     # React Context 관리
│   └── AuthContext.jsx           # 인증 컨텍스트
├── lib/                          # 유틸리티 및 API 클라이언트
│   ├── api-config.js             # API 설정 중앙화
│   ├── api-client.dashboard.js   # 대시보드 API
│   ├── api-client.logs.js        # 로그 API
│   ├── api-client.settings.js    # 설정 API
│   └── utils.js                  # 유틸리티 함수
├── hooks/                        # 커스텀 React Hooks
│   ├── use-mobile.jsx            # 모바일 감지 훅
│   └── use-toast.js              # 토스트 알림 훅
├── public/                       # 정적 리소스
│   ├── placeholder-*.svg/png     # 플레이스홀더 이미지
│   └── Sentient-*.woff           # 커스텀 폰트
├── styles/                       # 스타일 파일
├── Dockerfile                    # Docker 컨테이너 설정
├── docker-compose.yml            # Docker Compose 오케스트레이션
├── next.config.mjs               # Next.js 설정
├── tailwind.config.js            # Tailwind CSS 설정
└── package.json                  # 프로젝트 의존성
```

### 파일 통계

- **대시보드 페이지**: 10개 파일 (8개 섹션)
- **컴포넌트**: 75개 파일 (UI 컴포넌트 68개 포함)
- **UI 컴포넌트 총 라인 수**: 약 5,479줄
- **API 클라이언트**: 4개 파일
- **컨텍스트**: 1개 (AuthContext)

---

## 2. 기술 스택

### 핵심 프레임워크

| 기술 | 버전 | 용도 |
|------|------|------|
| **Next.js** | 15.2.4 | React 프레임워크, App Router 기반 |
| **React** | 19 | UI 라이브러리 |
| **TypeScript** | 5 | 타입 안정성 (설정되어 있으나 빌드 에러 무시) |
| **Node.js** | 18+ | 런타임 환경 |

### 스타일링

- **Tailwind CSS** 3.4.17: 유틸리티 퍼스트 CSS 프레임워크
- **tailwindcss-animate**: 애니메이션 플러그인
- **PostCSS**: CSS 후처리
- **next-themes**: 다크/라이트 테마 전환
- **class-variance-authority**: 조건부 스타일링
- **tailwind-merge**: Tailwind 클래스 병합
- **clsx**: 클래스네임 유틸리티

### UI 컴포넌트 라이브러리

#### Radix UI (완전한 접근성 보장)
프로젝트는 Radix UI의 거의 모든 프리미티브를 사용:
- Accordion, Alert Dialog, Avatar, Checkbox, Dialog
- Dropdown Menu, Hover Card, Popover, Progress, Radio Group
- Scroll Area, Select, Separator, Slider, Switch, Tabs
- Toast, Toggle, Tooltip 등 20개+ 컴포넌트

#### 추가 UI 라이브러리
- **lucide-react** ^0.454.0: 아이콘 시스템 (500개+ 아이콘)
- **cmdk** 1.0.4: Command palette (Command+K 인터페이스)
- **sonner** ^1.7.1: 토스트 알림
- **vaul** ^0.9.6: 드로어(drawer) 컴포넌트
- **embla-carousel-react** 8.5.1: 캐러셀
- **react-resizable-panels** ^2.1.7: 리사이즈 가능한 패널

### 3D 그래픽 및 시각화

- **Three.js** ^0.180.0: 3D 그래픽 라이브러리
- **@react-three/fiber** ^9.3.0: React용 Three.js 래퍼
- **@react-three/drei** ^10.7.6: Three.js 유틸리티 컬렉션
- **@splinetool/react-spline** ^4.1.0: 인터랙티브 3D 디자인
- **@paper-design/shaders-react**: 셰이더 컴포넌트
- **maath** ^0.10.8: 수학 유틸리티
- **leva** ^0.10.0: GUI 컨트롤
- **r3f-perf** ^7.2.3: 성능 모니터링

### 데이터 시각화

- **recharts** 2.15.0: 차트 라이브러리 (대시보드용)

### 폼 및 검증

- **react-hook-form** ^7.54.1: 고성능 폼 관리
- **@hookform/resolvers** ^3.9.1: 검증 통합
- **zod** ^3.24.1: TypeScript 우선 스키마 검증

### 유틸리티

- **date-fns** 4.1.0: 날짜/시간 처리
- **geist** ^1.3.1: Vercel의 Geist 폰트
- **input-otp** 1.4.1: OTP 입력 컴포넌트

### 분석 및 모니터링

- **@vercel/analytics** 1.3.1: Vercel 분석

### 개발 도구

- **autoprefixer** ^10.4.20: CSS 벤더 프리픽스 자동화
- **@types/node**, **@types/react**, **@types/react-dom**: TypeScript 타입 정의

---

## 3. 주요 기능

### 3.1 대시보드 페이지

#### 1) Command Center (개인정보 탐지 현황)
**파일**: `/app/dashboard/command-center/page.jsx`

**주요 기능**:
- 실시간 개인정보 탐지 현황 모니터링
- 전화번호, 주민등록번호, 이메일 등 탐지 통계
- 분기별 유출 횟수 차트 (Timeline)
- IP별 통계 (상위 20개)
- AI 서비스별 탐지 현황 (OpenAI, Anthropic, Google Gemini 등)
- 최근 5분간 탐지 건수 실시간 표시
- 최근 로그 10건 표시

**API 호출**:
- `fetchOverview()`: 전체 개요
- `fetchByIp()`: IP별 통계
- `fetchTimeline()`: 시간대별 추이
- `fetchByPiiType()`: 개인정보 유형별 통계
- `fetchLogs()`: 최근 로그

#### 2) Logs Page (전체 로그 페이지)
**파일**: `/app/dashboard/logs/page.jsx`

**주요 기능**:
- 모든 탐지 이벤트의 상세 로그 조회
- 검색 기능 (클라이언트 IP 기반)
- 페이지네이션 (기본 20건)
- 시간별, 프로젝트별 정렬
- 로그 레벨별 색상 구분 (critical, warning, info)
- 상세 로그 팝업 모달

**API 호출**:
- `fetchLogs()`: 필터링, 페이지네이션, 정렬 지원

#### 3) Detection Settings (탐지 기능 설정)
**파일**: `/app/dashboard/detection-settings/page.jsx`

**주요 기능**:
- 개인정보 유형별 탐지 활성화/비활성화
- 민감도 설정 (high, medium, low)
- 탐지 방법 표시 (BERT, Regex)
- 프로젝트별 설정 (UI만 구현, 실제 필터링은 미구현)
- 서버에서 설정 로드 및 업데이트

**지원하는 엔티티**:
- 이름, 전화번호, 이메일, 주민등록번호
- 주소, 신용카드번호, 계좌번호, 여권번호

**API 호출**:
- `fetchAllSettings()`: 모든 설정 조회
- `updateSetting()`: 개별 설정 업데이트 (PATCH)

#### 4) 미개발 페이지
다음 페이지들은 UI만 구현되어 있고 백엔드 연동은 미완성:
- **Agent Network** (프로젝트 관리)
- **Operations** (운영 관리)
- **Intelligence** (인텔리전스 분석)
- **Systems** (시스템 설정)

### 3.2 인증 시스템

#### AuthContext (React Context)
**파일**: `/contexts/AuthContext.jsx`

**기능**:
- JWT 토큰 기반 인증
- `localStorage`에 `access_token` 저장
- 로그인 상태 관리 (`isLoggedIn`, `accessToken`)
- 로그인/로그아웃 함수 제공

**메서드**:
- `loginWithToken(token)`: 토큰 저장 및 로그인 처리
- `logout()`: 토큰 삭제 및 로그아웃
- `useAuth()`: 인증 컨텍스트 훅

#### 로그인 폼
**파일**: `/components/login-form.jsx`, `/app/login/page.jsx`

**기능**:
- OAuth2 형식 로그인 (`application/x-www-form-urlencoded`)
- 3D Spline 씬을 배경으로 사용
- 에러 처리 및 사용자 피드백
- 로그인 성공 시 대시보드 리다이렉션 (주석 처리됨)

**API 엔드포인트**: `POST /api/v1/auth/login`

### 3.3 API 통신 구조

#### 중앙화된 API 설정
**파일**: `/lib/api-config.js`

**핵심 기능**:
1. **환경별 API URL 관리**
   - 환경 변수 `NEXT_PUBLIC_API_URL` 우선 사용
   - 기본값: `http://localhost:8000`
   - 클라이언트/서버 사이드 모두 지원

2. **엔드포인트 중앙 관리**
   ```javascript
   endpoints: {
     auth: { login, me },
     logs: { list },
     dashboard: { overview, timeline, byPiiType, byIp },
     settings: { list, detail, update }
   }
   ```

3. **자동 Authorization 헤더 주입**
   - `localStorage`에서 `access_token` 자동 추출
   - Bearer 토큰 형식으로 헤더에 추가

4. **에러 처리**
   - 401 에러 시 자동으로 토큰 삭제
   - 응답 상태 코드 검증

5. **헬퍼 함수**
   - `apiRequest()`: fetch 래퍼
   - `apiJson()`: JSON 응답 파싱
   - `getApiEndpoint()`: 전체 URL 생성

#### API 클라이언트 모듈

**1) Dashboard API** (`/lib/api-client.dashboard.js`)
- `fetchOverview()`: 전체 개요 통계
- `fetchTimeline()`: 시간대별 추이 (interval 지원)
- `fetchByPiiType()`: 개인정보 유형별 통계
- `fetchByIp()`: IP별 통계 (size 제한 가능)

**2) Logs API** (`/lib/api-client.logs.js`)
- `fetchLogs()`: 로그 조회
  - 필터: `start_date`, `end_date`, `client_ip`, `has_pii`, `entity_type`
  - 페이지네이션: `page`, `page_size`
  - 정렬: `sort` (예: `timestamp:desc`)

**3) Settings API** (`/lib/api-client.settings.js`)
- `fetchAllSettings()`: 모든 설정 조회
- `fetchSetting(entityType)`: 특정 엔티티 설정 조회
- `updateSetting(entityType, {enabled, threshold})`: 설정 업데이트 (PATCH)

#### 백엔드 API 구조 (OpenAPI 기반)
```
/api/v1/
├── auth/
│   ├── login (POST)
│   └── me (GET)
├── admin/
│   ├── logs (GET)
│   ├── statistics/
│   │   ├── overview (GET)
│   │   ├── timeline (GET)
│   │   ├── by-pii-type (GET)
│   │   └── by-ip (GET)
│   └── pii-settings/
│       ├── (GET) - 전체 설정
│       └── /{entity} (GET, PATCH) - 개별 설정
```

---

## 4. 컴포넌트 구조

### 4.1 UI 컴포넌트 시스템 (Shadcn/ui 기반)

프로젝트는 **Shadcn/ui** 디자인 시스템을 사용하며, 68개 이상의 재사용 가능한 컴포넌트를 보유:

**파일**: `/components/ui/*.jsx` (총 5,479줄)

#### 주요 컴포넌트 카테고리

1. **레이아웃 & 구조**
   - `card.jsx`: 콘텐츠 카드
   - `separator.jsx`: 구분선
   - `resizable.jsx`: 리사이즈 가능한 패널
   - `scroll-area.jsx`: 스크롤 영역
   - `sidebar.jsx`: 사이드바

2. **폼 요소**
   - `input.jsx`, `textarea.jsx`: 텍스트 입력
   - `button.jsx`, `button-group.jsx`: 버튼
   - `checkbox.jsx`, `radio-group.jsx`: 선택 요소
   - `select.jsx`, `slider.jsx`, `switch.jsx`: 입력 컨트롤
   - `calendar.jsx`, `input-otp.jsx`: 특수 입력
   - `form.jsx`, `label.jsx`, `field.jsx`: 폼 관리

3. **네비게이션**
   - `navigation-menu.jsx`: 메인 네비게이션
   - `menubar.jsx`: 메뉴바
   - `breadcrumb.jsx`: 브레드크럼
   - `pagination.jsx`: 페이지네이션
   - `tabs.jsx`: 탭 인터페이스

4. **오버레이**
   - `dialog.jsx`: 모달 다이얼로그
   - `alert-dialog.jsx`: 알림 다이얼로그
   - `sheet.jsx`: 사이드 시트
   - `drawer.jsx`: 드로어
   - `popover.jsx`: 팝오버
   - `tooltip.jsx`: 툴팁
   - `hover-card.jsx`: 호버 카드
   - `dropdown-menu.jsx`: 드롭다운 메뉴
   - `context-menu.jsx`: 컨텍스트 메뉴

5. **피드백**
   - `toast.jsx`, `toaster.jsx`, `sonner.jsx`: 토스트 알림
   - `alert.jsx`: 알림 메시지
   - `progress.jsx`: 진행 표시줄
   - `spinner.jsx`: 로딩 스피너
   - `skeleton.jsx`: 스켈레톤 로딩

6. **데이터 표시**
   - `table.jsx`: 테이블
   - `chart.jsx`: 차트 (Recharts 기반)
   - `avatar.jsx`: 아바타
   - `badge.jsx`: 배지
   - `kbd.jsx`: 키보드 단축키 표시
   - `empty.jsx`: 빈 상태

7. **복합 컴포넌트**
   - `command.jsx`: Command palette (Cmd+K)
   - `accordion.jsx`: 아코디언
   - `collapsible.jsx`: 접을 수 있는 컨테이너
   - `carousel.jsx`: 캐러셀
   - `toggle.jsx`, `toggle-group.jsx`: 토글

#### 컴포넌트 설정
**파일**: `/components.json`
- Shadcn/ui 스키마 기반
- RSC (React Server Components) 지원
- TypeScript 지원
- Tailwind CSS 변수 사용
- Path alias 설정: `@/components`, `@/lib`, `@/hooks`

### 4.2 커스텀 컴포넌트

#### 레이아웃 컴포넌트
- **header.jsx**: 헤더 네비게이션
- **mobile-menu.jsx**: 모바일 메뉴
- **logo.jsx**: 로고 컴포넌트

#### 랜딩 페이지 컴포넌트
- **hero.jsx**: 히어로 섹션
- **hero-section.jsx**: 확장된 히어로 섹션

#### 3D/그래픽 컴포넌트
- **spline-scene.jsx**: Spline 3D 씬 로더
- **pulsing-border-shader.jsx**: 맥동하는 테두리 셰이더
- **gl/index.jsx**: WebGL 컴포넌트
- **gl/particles.jsx**: 파티클 효과
- **gl/shaders/**: 셰이더 파일들

#### 인증 컴포넌트
- **login-form.jsx**: 로그인 폼
- **signup-form.jsx**: 회원가입 폼

#### 테마 컴포넌트
- **theme-provider.jsx**: 테마 프로바이더
- **theme-toggle.jsx**: 다크/라이트 모드 토글

#### 기타
- **pill.jsx**: 알약 모양 라벨

### 4.3 대시보드 레이아웃

**파일**: `/app/dashboard/page.jsx`

**구조**:
```
<TacticalDashboard>
  ├── <Sidebar> (접을 수 있음)
  │   ├── 로고 & 버전
  │   ├── 네비게이션 메뉴 (6개 섹션)
  │   └── 시스템 상태 표시
  ├── <MobileOverlay> (모바일 전용)
  └── <MainContent>
      ├── <TopToolbar>
      │   ├── 브레드크럼
      │   ├── 마지막 업데이트 시간
      │   ├── 알림 버튼
      │   ├── 새로고침 버튼
      │   ├── <ThemeToggle>
      │   └── 로그아웃 버튼
      └── <DashboardContent>
          └── 각 섹션별 페이지 컴포넌트
```

**네비게이션 섹션**:
1. 대시보드 (overview)
2. 전체 로그 페이지 (logs)
3. 탐지 기능 설정 (detection)
4. 프로젝트 관리 (agents)
5. 시스템 설정 (systems)

**반응형 디자인**:
- 데스크톱: 사이드바 펼쳐짐
- 모바일: 사이드바 오버레이 방식

---

## 5. 컨텍스트 및 상태 관리

### 5.1 React Context

#### AuthContext
**파일**: `/contexts/AuthContext.jsx`

**상태**:
- `accessToken`: JWT 액세스 토큰
- `isLoggedIn`: 로그인 여부 (Boolean)

**메서드**:
- `loginWithToken(token)`: 로그인 처리
- `logout()`: 로그아웃 처리

**특징**:
- SSR 안전 (localStorage 접근 시 window 체크)
- 페이지 새로고침 시 토큰 복원
- 전역적으로 인증 상태 공유

### 5.2 테마 관리

**ThemeProvider** (`next-themes` 사용)
**파일**: `/app/layout.jsx`, `/components/theme-provider.jsx`

**설정**:
- 기본 테마: `dark`
- 시스템 테마 비활성화 (`enableSystem: false`)
- 클래스 기반 테마 전환 (`attribute: "class"`)

**테마 스타일**:
- **다크 모드**: 검은 배경 + 노란색/호박색 악센트
- **라이트 모드**: 베이지 톤 배경 + 호박색 텍스트

### 5.3 지역 상태 관리

프로젝트는 **전역 상태 관리 라이브러리 없음** (Redux, Zustand 등 미사용)

**상태 관리 방식**:
1. **React useState**: 컴포넌트 지역 상태
2. **React Context**: 인증 및 테마
3. **URL 상태**: Next.js 라우팅 (페이지 전환)
4. **서버 상태**: React 컴포넌트에서 직접 API 호출 (useEffect)

**예시** (command-center/page.jsx):
```javascript
const [overview, setOverview] = useState(null)
const [ipStats, setIpStats] = useState([])
const [timeline, setTimeline] = useState([])

useEffect(() => {
  const load = async () => {
    const [ov, byIp, tl] = await Promise.all([
      fetchOverview(),
      fetchByIp(),
      fetchTimeline(),
    ])
    setOverview(ov)
    setIpStats(byIp)
    setTimeline(tl)
  }
  load()
}, [])
```

**장단점**:
- 장점: 간단하고 직관적, 외부 의존성 없음
- 단점: 페이지 간 상태 공유 불가, 캐싱 없음

---

## 6. Docker 설정

### 6.1 Dockerfile (Multi-stage Build)

**파일**: `/frontend/Dockerfile`

**빌드 전략**: 3단계 빌드 (최적화)

#### Stage 1: 의존성 설치 (deps)
- 베이스 이미지: `node:18-alpine`
- `libc6-compat` 설치 (호환성)
- `npm ci --legacy-peer-deps`

#### Stage 2: 빌드 (builder)
- 의존성 복사 (deps에서)
- 소스 코드 복사
- `npm run build` 실행
- 텔레메트리 비활성화

#### Stage 3: 프로덕션 실행 (runner)
- 최소한의 파일만 복사
- 비특권 사용자 생성 (`nextjs:nodejs`)
- Standalone 빌드 결과물 실행
- 포트 3000 노출

**환경 변수**:
- `NODE_ENV=production`
- `NEXT_TELEMETRY_DISABLED=1`
- `PORT=3000`
- `HOSTNAME=0.0.0.0`

**실행 명령**: `node server.js` (standalone 모드)

### 6.2 Docker Compose

**파일**: `/docker-compose.yml`

**서비스 정의**:
```yaml
services:
  frontend:
    container_name: admin-fe-frontend
    ports: 3000:3000
    environment:
      - NEXT_PUBLIC_API_URL=${BACKEND_API_URL}
    networks: admin-network
```

**특징**:
- `restart: unless-stopped`: 자동 재시작
- 환경 변수를 통한 API URL 설정
- 커스텀 네트워크 (`admin-network`)

### 6.3 .dockerignore

**제외 파일**:
- `node_modules`, `.next`, `.git`
- 로그 파일 (`*.log`)
- 환경 변수 파일 (`.env*.local`)
- README, `.DS_Store`

---

## 7. 환경 설정

### 7.1 환경 변수

#### 프론트엔드 환경 변수
**파일**: `.env.local` (gitignore됨)

**주요 변수**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
```

**특징**:
- `NEXT_PUBLIC_` 접두사: 클라이언트 사이드에 노출됨
- 브라우저 번들에 포함됨

#### Docker 환경 변수
**파일**: `/env.example` → `.env`

**설정**:
```env
BACKEND_API_URL=http://host.docker.internal:8000
```

**환경별 예시**:
- **Docker Desktop (macOS/Windows)**: `http://host.docker.internal:8000`
- **Linux**: `http://172.17.0.1:8000`
- **프로덕션**: `https://api.yourdomain.com`
- **같은 Docker 네트워크**: `http://backend:8000`

### 7.2 Next.js 설정

**파일**: `/next.config.mjs`

**주요 설정**:
```javascript
{
  eslint: { ignoreDuringBuilds: true },    // 빌드 시 ESLint 무시
  typescript: { ignoreBuildErrors: true }, // TypeScript 에러 무시
  images: { unoptimized: true },          // 이미지 최적화 비활성화
  output: 'standalone'                     // Standalone 빌드 (Docker용)
}
```

**의미**:
- **standalone**: 모든 의존성 포함, 독립 실행 가능
- **ignoreDuringBuilds**: 개발 속도 우선 (프로덕션 권장 X)

### 7.3 Tailwind CSS 설정

**파일**: `/tailwind.config.js`

**주요 설정**:
- **darkMode**: `"class"` (클래스 기반)
- **content**: 모든 JSX 파일 스캔
- **테마 확장**: CSS 변수 기반 색상 시스템
  - `--primary`, `--secondary`, `--accent` 등
  - `hsl()` 색상 값 사용
- **애니메이션**: `accordion-down`, `accordion-up`
- **플러그인**: `tailwindcss-animate`

### 7.4 TypeScript 설정

**파일**: `/tsconfig.json`

**주요 설정**:
```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "jsx": "preserve",
    "paths": {
      "@/*": ["./*"]  // Path alias
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"]
}
```

**특징**:
- JSX 보존 (Next.js가 처리)
- Path alias `@/` 지원
- Next.js 타입 자동 생성

### 7.5 폰트 설정

**파일**: `/app/layout.jsx`

**폰트**:
- **Geist Sans** (본문): Vercel의 Geist 폰트
- **Geist Mono** (코드): 모노스페이스 폰트
- **Sentient** (커스텀): `/public/Sentient-*.woff`

**적용**:
```javascript
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'

// CSS 변수로 주입
--font-sans: ${GeistSans.variable}
--font-mono: ${GeistMono.variable}
```

---

## 8. 주요 특징 및 설계 패턴

### 8.1 디자인 패턴

#### 1) 중앙화된 API 관리
- 모든 API 엔드포인트를 `api-config.js`에 집중
- 환경별 URL 관리 용이
- Authorization 헤더 자동 주입
- 에러 처리 일관성

#### 2) 컴포넌트 합성 (Composition)
- Radix UI 프리미티브 기반
- Shadcn/ui 스타일 래핑
- 높은 재사용성 및 접근성

#### 3) 파일 기반 라우팅
- Next.js App Router 사용
- `/app` 디렉토리 구조가 URL 경로
- 서버/클라이언트 컴포넌트 분리

#### 4) CSS-in-JS 대신 Tailwind
- 유틸리티 퍼스트 접근
- 빌드 타임 CSS 생성
- 번들 크기 최소화

### 8.2 보안 고려사항

#### 현재 구현
1. **JWT 토큰 기반 인증**
   - Bearer 토큰 방식
   - localStorage 저장

2. **API 요청 검증**
   - 401 에러 시 자동 로그아웃
   - 응답 상태 코드 검증

#### 개선 필요 사항
1. **토큰 저장 위치**
   - localStorage는 XSS 공격에 취약
   - HttpOnly 쿠키 사용 권장

2. **CSRF 보호**
   - 현재 구현 없음
   - CSRF 토큰 추가 권장

3. **토큰 갱신**
   - Refresh token 미구현
   - Access token 만료 시 재로그인 필요

4. **환경 변수 노출**
   - `NEXT_PUBLIC_` 변수는 클라이언트 노출
   - 민감한 정보 포함 금지

### 8.3 성능 최적화

#### 현재 적용된 최적화
1. **Standalone 빌드**
   - Docker 이미지 크기 감소
   - 의존성 포함한 단일 실행 파일

2. **이미지 최적화 비활성화**
   - `unoptimized: true`
   - 외부 이미지 호스팅 전제

3. **클라이언트 사이드 렌더링 (CSR)**
   - 대부분의 페이지에 `"use client"` 지시어
   - 동적 데이터 많음 (실시간 대시보드)

#### 개선 가능 사항
1. **서버 컴포넌트 활용**
   - 정적 부분은 서버에서 렌더링
   - 초기 로딩 속도 개선

2. **데이터 캐싱**
   - React Query, SWR 도입 고려
   - API 응답 캐싱 및 자동 재검증

3. **코드 스플리팅**
   - 동적 import 활용
   - 페이지별 번들 분리

4. **이미지 최적화 재활성화**
   - Next.js 이미지 최적화 사용
   - WebP 변환, 리사이징

### 8.4 접근성 (A11y)

#### 구현된 기능
1. **Radix UI 사용**
   - WCAG 2.1 준수
   - 키보드 네비게이션 지원
   - ARIA 속성 자동 적용

2. **시맨틱 HTML**
   - `<nav>`, `<header>`, `<main>` 등 사용
   - 적절한 헤딩 계층

3. **다크 모드 지원**
   - 시각적 편의성 향상
   - 색상 대비 고려

#### 개선 가능 사항
1. **포커스 관리**
   - 모달 열 때 포커스 트랩
   - Skip to content 링크

2. **스크린 리더 테스트**
   - NVDA, JAWS 호환성 검증
   - 대시보드 차트 대체 텍스트

3. **색상 대비**
   - WCAG AA/AAA 기준 검증
   - 색맹 사용자 고려

---

## 9. 개발 워크플로우

### 9.1 NPM 스크립트

**파일**: `/package.json`

```json
{
  "scripts": {
    "dev": "next dev",           // 개발 서버 (localhost:3000)
    "build": "next build",       // 프로덕션 빌드
    "start": "next start",       // 프로덕션 서버
    "lint": "next lint"          // ESLint 실행
  }
}
```

### 9.2 로컬 개발

#### 설치 및 실행
```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 브라우저: http://localhost:3000
```

#### 환경 변수 설정
```bash
# .env.local 파일 생성
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 9.3 Docker 개발

#### 빌드 및 실행
```bash
# Docker Compose로 실행
docker-compose up -d

# 또는 직접 빌드
docker build -t admin-fe-frontend ./frontend
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 admin-fe-frontend
```

#### 환경 변수 설정
```bash
# .env 파일 생성 (docker-compose.yml 디렉토리)
BACKEND_API_URL=http://host.docker.internal:8000
```

### 9.4 빌드 최적화

#### Standalone 빌드 확인
```bash
npm run build

# 생성 파일:
# .next/standalone/          # 독립 실행 가능한 서버
# .next/static/              # 정적 자산
# public/                    # 공개 파일
```

#### 빌드 에러 무시 설정
- ESLint 에러: 빌드 시 무시 (`ignoreDuringBuilds: true`)
- TypeScript 에러: 빌드 시 무시 (`ignoreBuildErrors: true`)

**주의**: 프로덕션에서는 에러를 수정하는 것이 권장됨

---

## 10. 프로젝트 현황 및 TODO

### 10.1 완성된 기능

- [x] 기본 레이아웃 및 네비게이션
- [x] 로그인/로그아웃 인증 시스템
- [x] 다크/라이트 테마 전환
- [x] 대시보드 (Command Center)
  - [x] 전체 개요 통계
  - [x] IP별 통계
  - [x] 시간대별 추이 차트
  - [x] 개인정보 유형별 통계
  - [x] 최근 로그 표시
- [x] 전체 로그 페이지
  - [x] 로그 조회 및 검색
  - [x] 페이지네이션
  - [x] 상세 로그 모달
- [x] 탐지 기능 설정
  - [x] 엔티티별 활성화/비활성화
  - [x] 서버 연동 (조회/업데이트)
- [x] Docker 컨테이너화
- [x] 반응형 디자인 (모바일 지원)

### 10.2 미완성 기능

- [ ] 프로젝트 관리 (Agent Network) - UI만 존재
- [ ] 운영 관리 (Operations) - UI만 존재
- [ ] 인텔리전스 분석 (Intelligence) - UI만 존재
- [ ] 시스템 설정 (Systems) - UI만 존재
- [ ] 로그 필터링 고도화 (엔티티 타입, has_pii 등)
- [ ] 실시간 알림 시스템 (WebSocket)
- [ ] 회원가입 기능 (signup-form.jsx 미사용)

### 10.3 개선 가능 영역

#### 기능
- [ ] 데이터 캐싱 (React Query, SWR)
- [ ] 무한 스크롤 (로그 페이지)
- [ ] 실시간 데이터 업데이트 (폴링 또는 WebSocket)
- [ ] 다국어 지원 (i18n)
- [ ] CSV/Excel 내보내기
- [ ] 차트 인터랙션 강화 (확대, 드릴다운)

#### 성능
- [ ] 서버 컴포넌트 활용 (RSC)
- [ ] 이미지 최적화 재활성화
- [ ] 번들 크기 분석 및 최적화
- [ ] Lazy loading (3D 컴포넌트 등)

#### 보안
- [ ] HttpOnly 쿠키로 토큰 저장
- [ ] CSRF 보호
- [ ] Refresh token 구현
- [ ] Rate limiting (API 요청 제한)

#### 개발 경험
- [ ] TypeScript 엄격 모드 활성화
- [ ] ESLint 에러 수정
- [ ] 테스트 코드 작성 (Jest, React Testing Library)
- [ ] Storybook 도입 (컴포넌트 문서화)

#### 문서화
- [ ] API 문서 생성 (Swagger/OpenAPI)
- [ ] 컴포넌트 사용 가이드
- [ ] 배포 가이드

---

## 11. 파일 경로 참조

### 주요 파일 절대 경로

#### 설정 파일
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/package.json`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/next.config.mjs`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/tailwind.config.js`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/tsconfig.json`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/Dockerfile`
- `/Users/sun/개발/KISIA/project/Admin-FE/docker-compose.yml`

#### 핵심 페이지
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/app/layout.jsx`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/app/page.jsx`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/app/login/page.jsx`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/app/dashboard/page.jsx`

#### 대시보드 페이지
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/app/dashboard/command-center/page.jsx`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/app/dashboard/logs/page.jsx`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/app/dashboard/detection-settings/page.jsx`

#### API 클라이언트
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/lib/api-config.js`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/lib/api-client.dashboard.js`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/lib/api-client.logs.js`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/lib/api-client.settings.js`

#### 컨텍스트
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/contexts/AuthContext.jsx`

#### 주요 컴포넌트
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/components/login-form.jsx`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/components/theme-toggle.jsx`
- `/Users/sun/개발/KISIA/project/Admin-FE/frontend/components/theme-provider.jsx`

---

## 12. 요약

### 프로젝트 특징
1. **최신 기술 스택**: Next.js 15, React 19, TypeScript 5
2. **풍부한 UI 컴포넌트**: 68개 이상의 재사용 가능한 컴포넌트
3. **3D/그래픽 강화**: Three.js, Spline 등 고급 시각화
4. **완전한 접근성**: Radix UI 기반 WCAG 준수
5. **Docker 지원**: 컨테이너화된 배포
6. **모듈화된 API**: 중앙화된 API 관리 시스템
7. **반응형 디자인**: 모바일부터 데스크톱까지

### 기술 하이라이트
- **프레임워크**: Next.js 15 App Router, React 19
- **스타일링**: Tailwind CSS, Shadcn/ui
- **3D**: Three.js, React Three Fiber, Spline
- **차트**: Recharts
- **폼**: React Hook Form, Zod
- **인증**: JWT Bearer Token
- **테마**: next-themes (다크/라이트)
- **배포**: Docker, Standalone 빌드

### 아키텍처
- **CSR 중심**: 클라이언트 사이드 렌더링 (실시간 데이터)
- **RESTful API**: FastAPI 백엔드 연동
- **컴포넌트 합성**: 높은 재사용성
- **파일 기반 라우팅**: 직관적인 구조

### 핵심 기능
1. **실시간 대시보드**: 개인정보 탐지 현황 모니터링
2. **로그 관리**: 검색, 필터링, 페이지네이션
3. **설정 관리**: 탐지 기능 on/off, 민감도 조절
4. **인증 시스템**: JWT 토큰 기반 보안

### 개발 상태
- **완성도**: 70% (핵심 기능 구현 완료)
- **미완성**: 프로젝트/운영/인텔리전스/시스템 관리 페이지
- **개선 필요**: 보안, 성능, 테스트, 문서화

---

**작성일**: 2025-11-04  
**분석자**: Claude Code  
**프로젝트**: DS MASKING AI - Admin Frontend
