# DS MASKING AI - Frontend

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-15.2.4-black)
![React](https://img.shields.io/badge/React-19-blue)
![License](https://img.shields.io/badge/license-Private-red)

Advanced NER and context-based detection system to protect personal information with real-time monitoring and AI-powered analysis.

## 🎯 프로젝트 개요

DS MASKING AI는 개인정보 탐지 및 보호를 위한 실시간 모니터링 대시보드입니다. NER(Named Entity Recognition) 및 컨텍스트 기반 탐지 기술을 활용하여 민감한 개인정보를 자동으로 식별하고 차단합니다.

### 주요 기능

- 📊 **실시간 대시보드**: 개인정보 탐지 현황 실시간 모니터링
- 🔍 **AI 기반 탐지**: OpenAI, Anthropic, Google Gemini 등 AI 서비스별 통계
- 🌓 **다크/라이트 테마**: 사용자 맞춤형 테마 지원 (베이지 톤 라이트 모드)
- 📈 **상세 분석**: IP별 통계, 분기별 유출 횟수, 라벨별 차단 현황
- 🚨 **실시간 알림**: 위협 감지 시 즉각적인 알림 시스템
- 🔐 **인증 시스템**: 보안 강화된 로그인/로그아웃 기능

## 🛠️ 기술 스택

### Core
- **Framework**: Next.js 15.2.4 (App Router)
- **React**: 19
- **TypeScript**: 5
- **Styling**: Tailwind CSS 3.4.17

### UI Components
- **Radix UI**: 완전한 접근성을 갖춘 UI 컴포넌트 라이브러리
- **Lucide React**: 아이콘 시스템
- **Recharts**: 데이터 시각화
- **next-themes**: 다크/라이트 테마 지원

### 3D & Graphics
- **Three.js**: 3D 그래픽 렌더링
- **React Three Fiber**: React용 Three.js
- **Spline**: 인터랙티브 3D 디자인

### Forms & Validation
- **React Hook Form**: 폼 관리
- **Zod**: 스키마 검증
- **@hookform/resolvers**: 폼 검증 통합

## 📁 프로젝트 구조

```
frontend/
├── app/
│   ├── dashboard/              # 대시보드 메인
│   │   ├── command-center/     # 개인정보 탐지 현황
│   │   ├── agent-network/      # 프로젝트 관리
│   │   ├── operations/         # 운영 관리
│   │   ├── intelligence/       # 인텔리전스 분석
│   │   ├── systems/            # 시스템 설정
│   │   ├── logs/              # 전체 로그 페이지
│   │   └── detection-settings/ # 탐지 기능 설정
│   ├── login/                 # 로그인 페이지
│   ├── layout.jsx             # 루트 레이아웃
│   ├── page.jsx              # 랜딩 페이지
│   └── globals.css           # 글로벌 스타일
├── components/
│   ├── ui/                   # 재사용 가능한 UI 컴포넌트
│   ├── gl/                   # WebGL/3D 컴포넌트
│   ├── hero.jsx              # 히어로 섹션
│   ├── header.jsx            # 헤더 컴포넌트
│   └── theme-toggle.jsx      # 테마 전환 버튼
├── contexts/
│   └── AuthContext.jsx       # 인증 컨텍스트
└── package.json
```

## 🚀 시작하기

### 필수 요구사항

- Node.js 18.17 이상
- npm 또는 yarn

### 설치

```bash
# 의존성 설치
npm install
# 또는
yarn install
```

### 개발 서버 실행

```bash
npm run dev
# 또는
yarn dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000) 을 열어 결과를 확인하세요.

### 빌드

```bash
npm run build
npm run start
# 또는
yarn build
yarn start
```

## 🎨 테마 시스템

프로젝트는 다크 모드와 라이트 모드를 지원합니다:

- **다크 모드**: 기본 검은 배경에 노란색/호박색 악센트
- **라이트 모드**: 따뜻한 베이지 톤 배경에 진한 호박색 텍스트

테마 전환은 대시보드 상단 우측의 태양/달 아이콘으로 가능합니다.

## 📊 대시보드 페이지 설명

### 1. 대시보드 (Command Center)
- 개인정보 탐지 현황 실시간 모니터링
- 전화번호, 주민등록번호, 이메일 등 탐지 통계
- 분기별 유출 횟수 차트
- IP별 통계 및 AI 서비스별 탐지 현황

### 2. 전체 로그 페이지
- 모든 탐지 이벤트의 상세 로그
- 필터링 및 검색 기능
- 시간별, 프로젝트별 정렬

### 3. 탐지 기능 설정
- 개인정보 유형별 탐지 활성화/비활성화
- 민감도 설정
- 알림 설정

### 4. 프로젝트 관리
- 프로젝트별 탐지 현황
- 프로젝트 설정 및 관리

### 5. 시스템 설정
- 시스템 상태 모니터링
- 리소스 사용량
- 시스템 구성 관리

## 🔒 보안 기능

- 인증 기반 접근 제어
- 세션 관리
- 안전한 로그아웃

## 📝 환경 변수

프로젝트 루트에 `.env.local` 파일을 생성하세요:

```env
# API 엔드포인트
NEXT_PUBLIC_API_URL=your_api_url

# 기타 환경 변수
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
```

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 오픈소스 프로젝트입니다.

## 👥 개발팀

DS AI Team - KISIA Project

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

**DS MASKING AI** - Protecting Your Privacy with Intelligence 🛡️
