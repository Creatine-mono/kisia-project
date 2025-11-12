# Docker 설정 완료 안내

프로젝트가 Docker Compose로 실행 가능하도록 설정되었습니다.

## 📁 생성된 파일

### 1. Docker 관련 파일
- `frontend/Dockerfile` - Next.js 애플리케이션을 위한 Docker 이미지 빌드 파일
- `frontend/.dockerignore` - Docker 빌드 시 제외할 파일 목록
- `docker-compose.yml` - Docker Compose 설정 파일 (프로젝트 루트)

### 2. 설정 파일
- `frontend/lib/api-config.js` - **중앙화된 API 설정 파일** ⭐
- `env.example` - 환경 변수 예시 파일
- `README-DOCKER.md` - Docker 사용 가이드

### 3. 예시 파일
- `frontend/lib/api-client.example.js` - API 사용 예시

## 🔧 주요 변경사항

### 1. Next.js 설정 업데이트
`frontend/next.config.mjs`에 `output: 'standalone'` 추가되어 Docker 최적화 빌드가 가능합니다.

### 2. API 설정 중앙화
`frontend/lib/api-config.js` 파일에서 모든 백엔드 API URL을 관리합니다:

```javascript
import { apiConfig, apiJson, getApiEndpoint } from '@/lib/api-config';

// 사용 예시
const logs = await apiJson(apiConfig.endpoints.logs.list);
```

### 3. 환경 변수 설정
백엔드 API URL은 환경 변수로 설정됩니다:
- Docker: `.env` 파일의 `BACKEND_API_URL`
- 로컬 개발: `frontend/.env.local` 파일의 `NEXT_PUBLIC_API_URL`

## 🚀 사용 방법

### Docker Compose로 실행
```bash
# 1. 환경 변수 설정
cp env.example .env
# .env 파일에서 BACKEND_API_URL 수정

# 2. 실행
docker-compose up -d

# 3. 접속
# http://localhost:3000
```

### 백엔드 URL 변경
`.env` 파일에서 `BACKEND_API_URL` 값을 변경하고 컨테이너를 재시작하세요:

```bash
docker-compose down
docker-compose up -d
```

## 📝 API 사용 가이드

### 기본 사용법
```javascript
import { apiConfig, apiJson, apiRequest } from '@/lib/api-config';

// GET 요청
const data = await apiJson(apiConfig.endpoints.logs.list);

// POST 요청
const result = await apiRequest(apiConfig.endpoints.auth.login, {
  method: 'POST',
  body: JSON.stringify({ email, password }),
});
```

자세한 예시는 `frontend/lib/api-client.example.js` 파일을 참고하세요.

## 🔗 백엔드 연결 설정

다양한 환경에서 백엔드에 연결하는 방법:

| 환경 | BACKEND_API_URL 설정값 |
|------|----------------------|
| Docker Desktop (Mac/Windows) | `http://host.docker.internal:8000` |
| Linux | `http://172.17.0.1:8000` |
| 같은 Docker 네트워크 | `http://backend:8000` |
| 프로덕션 | `https://api.yourdomain.com` |

## 📚 추가 문서

- `README-DOCKER.md` - 상세한 Docker 사용 가이드
- `frontend/lib/api-client.example.js` - API 사용 예시 코드

