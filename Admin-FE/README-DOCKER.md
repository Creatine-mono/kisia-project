# Docker Compose 실행 가이드

이 프로젝트는 Docker Compose를 사용하여 실행할 수 있습니다.

## 📋 사전 요구사항

- Docker (20.10 이상)
- Docker Compose (2.0 이상)

## 🚀 빠른 시작

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하세요:

```bash
cp env.example .env
```

`.env` 파일에서 백엔드 API URL을 설정하세요:

```env
# 백엔드 API URL 설정
BACKEND_API_URL=http://host.docker.internal:8000
```

**주요 설정 값:**
- **Docker Desktop (Mac/Windows)**: `http://host.docker.internal:8000`
- **Linux**: `http://172.17.0.1:8000` (또는 호스트의 실제 IP 주소)
- **프로덕션**: `https://api.yourdomain.com`
- **다른 Docker 컨테이너와 통신**: `http://backend:8000` (같은 Docker 네트워크 내)

### 2. Docker Compose로 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 컨테이너 중지
docker-compose down
```

### 3. 접속

브라우저에서 [http://localhost:3000](http://localhost:3000) 으로 접속하세요.

## 🔧 개발 모드

### Option 1: Docker 개발 모드 (Hot Reload 지원) ⚡

코드 변경사항이 **자동으로 반영**되는 개발 환경입니다:

```bash
# 개발 모드로 실행 (Hot Reload 활성화)
docker-compose -f docker-compose.dev.yml up --build

# 백그라운드 실행
docker-compose -f docker-compose.dev.yml up -d --build

# 로그 확인
docker-compose -f docker-compose.dev.yml logs -f frontend

# 중지
docker-compose -f docker-compose.dev.yml down
```

**특징:**
- ✅ 코드 수정 시 자동 반영 (Hot Reload)
- ✅ 빠른 개발 사이클
- ✅ Docker 환경에서 개발 가능
- ⚠️ 개발 전용 (프로덕션 환경에 사용 금지)

**코드 변경이 반영되지 않을 때:**
```bash
# 컨테이너와 볼륨 완전히 삭제 후 재시작
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build
```

### Option 2: 로컬 개발 모드

Docker 없이 로컬에서 개발할 때는 다음과 같이 실행할 수 있습니다:

```bash
cd frontend
npm install
npm run dev
```

이 경우 `frontend/.env.local` 파일에 환경 변수를 설정하세요:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📝 API 설정 변경

백엔드 API 주소를 변경하려면:

1. **Docker Compose 사용 시**: `.env` 파일의 `BACKEND_API_URL` 값을 수정하고 컨테이너를 재시작하세요:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. **로컬 개발 시**: `frontend/.env.local` 파일의 `NEXT_PUBLIC_API_URL` 값을 수정하세요.

프론트엔드 코드에서는 `frontend/lib/api-config.js` 파일에서 API 설정을 관리합니다. 이 파일을 통해 모든 API 호출이 중앙에서 관리됩니다.

## 🛠️ 유용한 명령어

```bash
# 컨테이너 빌드 (캐시 없이)
docker-compose build --no-cache

# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 로그 확인
docker-compose logs frontend

# 컨테이너 내부 접속
docker-compose exec frontend sh

# 컨테이너 재시작
docker-compose restart frontend

# 볼륨 및 네트워크 포함 완전 삭제
docker-compose down -v
```

## 📦 빌드 최적화

프로덕션 빌드를 위해 Next.js는 standalone 모드로 빌드됩니다. 이는 더 작은 이미지 크기와 빠른 시작 시간을 제공합니다.

## 🔍 문제 해결

### 백엔드에 연결할 수 없는 경우

1. `.env` 파일의 `BACKEND_API_URL`이 올바른지 확인하세요.
2. 백엔드 서버가 실행 중인지 확인하세요.
3. Docker 네트워크 설정을 확인하세요.

### 포트가 이미 사용 중인 경우

`docker-compose.yml`에서 포트 매핑을 변경하세요:

```yaml
ports:
  - "3001:3000"  # 호스트의 3001 포트 사용
```

