# 클린 아키텍처 & DDD 구조

## 📐 아키텍처 개요

본 프로젝트는 **클린 아키텍처(Clean Architecture)**와 **도메인 주도 설계(Domain-Driven Design, DDD)** 원칙을 적용하여 구현되었습니다.

### 핵심 원칙

1. **의존성 역전 원칙 (Dependency Inversion)**: 외부 레이어가 내부 레이어에 의존
2. **관심사의 분리 (Separation of Concerns)**: 각 레이어는 명확한 책임을 가짐
3. **테스트 가능성 (Testability)**: 비즈니스 로직을 독립적으로 테스트 가능
4. **프레임워크 독립성**: 비즈니스 로직이 FastAPI에 종속되지 않음

## 🏗️ 레이어 구조

```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                      │
│              (API Routes - HTTP 처리)                    │
│  app/api/routers/                                        │
└─────────────────────────────────────────────────────────┘
                          ↓ depends on
┌─────────────────────────────────────────────────────────┐
│                 Application Layer                        │
│            (Use Cases - 비즈니스 흐름)                    │
│  app/usecases/                                           │
└─────────────────────────────────────────────────────────┘
                          ↓ depends on
┌─────────────────────────────────────────────────────────┐
│                   Domain Layer                           │
│         (Services - 도메인 비즈니스 로직)                 │
│  app/services/                                           │
└─────────────────────────────────────────────────────────┘
                          ↓ depends on
┌─────────────────────────────────────────────────────────┐
│               Infrastructure Layer                       │
│     (Repository, DB, External Services)                  │
│  app/repository/, app/db/, app/core/                     │
└─────────────────────────────────────────────────────────┘
```

## 📂 디렉토리 구조 및 책임

### 1. Presentation Layer (표현 계층)

**위치**: `app/api/routers/`

**책임**:
- HTTP 요청/응답 처리
- 입력 검증 (Pydantic 스키마)
- UseCase 호출
- HTTP 상태 코드 및 예외 매핑

**규칙**:
- ❌ 비즈니스 로직 포함 금지
- ❌ 데이터베이스 직접 접근 금지
- ✅ UseCase만 호출
- ✅ HTTP 관련 처리만 수행

**예시**: `app/api/routers/auth.py`

```python
@router.post("/register")
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        # Use Case 호출만 수행
        use_case = RegisterUserUseCase(db)
        user = await use_case.execute(...)
        return user
    except ValueError as e:
        # HTTP 예외로 변환
        raise HTTPException(status_code=400, detail=str(e))
```

### 2. Application Layer (애플리케이션 계층)

**위치**: `app/usecases/`

**책임**:
- 애플리케이션의 비즈니스 흐름 정의
- 여러 Service를 조합하여 사용
- 트랜잭션 경계 정의
- 각 Use Case는 하나의 사용자 의도(User Story)를 나타냄

**규칙**:
- ✅ 여러 Service를 조합하여 흐름 구성
- ✅ 각 Use Case는 단일 책임 원칙 준수
- ❌ HTTP 관련 처리 금지
- ❌ 직접적인 데이터베이스 접근 금지

**예시**: `app/usecases/auth_usecases.py`

```python
class LoginUseCase:
    """
    로그인 Use Case
    
    User Story: 사용자가 로그인하여 액세스 토큰을 받는다
    
    Flow:
    1. UserService를 통해 자격 증명 검증
    2. 사용자 활성화 상태 확인
    3. TokenService를 통해 액세스 토큰 생성
    """
    def __init__(self, db: AsyncSession):
        self.user_service = UserService(db)
        self.token_service = TokenService()
    
    async def execute(self, username: str, password: str) -> dict:
        # 1. 자격 증명 검증
        user = await self.user_service.verify_user_credentials(username, password)
        if not user:
            raise ValueError("자격 증명 오류")
        
        # 2. 활성화 상태 확인
        if not await self.user_service.is_user_active(user):
            raise ValueError("비활성화된 사용자")
        
        # 3. 토큰 생성
        token = self.token_service.create_user_access_token(username)
        
        return {"access_token": token, "token_type": "bearer"}
```

### 3. Domain Layer (도메인 계층)

**위치**: `app/services/`

**책임**:
- 단일 도메인 엔티티에 대한 비즈니스 로직
- 도메인 규칙 검증
- Repository와 상호작용

**규칙**:
- ✅ 도메인 규칙 검증
- ✅ 단일 책임 원칙 (하나의 도메인 엔티티만 관리)
- ❌ HTTP 관련 처리 금지
- ❌ 다른 도메인 서비스와의 복잡한 조합 금지 (UseCase에서 수행)

**예시**: `app/services/auth/user_service.py`

```python
class UserService:
    """사용자 도메인 서비스"""
    
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)
    
    async def create_user(self, username: str, email: str, password: str) -> User:
        """
        사용자 생성
        
        비즈니스 규칙:
        - 사용자명 중복 불가
        - 이메일 중복 불가
        """
        # 도메인 규칙 검증
        if await self.repository.get_by_username(username):
            raise ValueError("사용자명 중복")
        
        if await self.repository.get_by_email(email):
            raise ValueError("이메일 중복")
        
        # 엔티티 생성
        return await self.repository.create(username, email, password)
```

### 4. Infrastructure Layer (인프라 계층)

**위치**: `app/repository/`, `app/db/`, `app/core/`

**책임**:
- 데이터베이스 접근
- 외부 서비스 연동
- 기술적 구현 세부사항

**구성요소**:
- **Repository**: 데이터 접근 계층 (`app/repository/`)
- **Database**: DB 연결 및 세션 관리 (`app/db/`)
- **Security**: 암호화, JWT 등 보안 관련 (`app/core/security.py`)
- **Config**: 설정 관리 (`app/core/config.py`)

## 📊 인증(Auth) 기능의 계층별 흐름

### 회원가입 예시

```
1. [Presentation] POST /api/v1/auth/register
   ↓
2. [Application] RegisterUserUseCase.execute()
   ↓
3. [Domain] UserService.create_user()
   ├─ UserService.check_duplicate_username()
   ├─ UserService.check_duplicate_email()
   └─ UserRepository.create()
   ↓
4. [Infrastructure] UserRepository.create()
   └─ PostgreSQL INSERT
```

### 로그인 예시

```
1. [Presentation] POST /api/v1/auth/login
   ↓
2. [Application] LoginUseCase.execute()
   ├─ UserService.verify_user_credentials()
   │  └─ UserRepository.get_by_username()
   ├─ UserService.is_user_active()
   └─ TokenService.create_user_access_token()
   ↓
3. [Domain] UserService + TokenService
   ↓
4. [Infrastructure] Repository + Security (JWT)
```

## 🎯 각 레이어의 테스트 전략

### 1. Presentation Layer (Router) 테스트
- **타입**: Integration Test
- **도구**: TestClient (FastAPI)
- **검증**: HTTP 요청/응답, 상태 코드

```python
def test_register_user():
    response = client.post("/api/v1/auth/register", json={...})
    assert response.status_code == 201
```

### 2. Application Layer (UseCase) 테스트
- **타입**: Unit Test
- **도구**: pytest + Mock
- **검증**: 비즈니스 흐름, Service 호출 순서

```python
async def test_login_use_case():
    # Mock Services
    user_service = Mock(UserService)
    token_service = Mock(TokenService)
    
    use_case = LoginUseCase(user_service, token_service)
    result = await use_case.execute("user", "pass")
    
    assert result["access_token"]
    user_service.verify_user_credentials.assert_called_once()
```

### 3. Domain Layer (Service) 테스트
- **타입**: Unit Test
- **도구**: pytest + Mock Repository
- **검증**: 도메인 규칙, 비즈니스 로직

```python
async def test_create_user_duplicate_check():
    # Mock Repository
    repo = Mock(UserRepository)
    repo.get_by_username.return_value = existing_user
    
    service = UserService(repo)
    
    with pytest.raises(ValueError, match="사용자명 중복"):
        await service.create_user("duplicate", "email", "pass")
```

### 4. Infrastructure Layer (Repository) 테스트
- **타입**: Integration Test
- **도구**: pytest + Test Database
- **검증**: 데이터베이스 CRUD

```python
async def test_user_repository_create(test_db):
    repo = UserRepository(test_db)
    user = await repo.create("user", "email", "pass")
    
    assert user.id is not None
    assert user.username == "user"
```

## 🔄 의존성 방향

```
Router (HTTP)
   ↓ depends on
UseCase (Application Logic)
   ↓ depends on
Service (Domain Logic)
   ↓ depends on
Repository (Data Access)
   ↓ depends on
Database (Infrastructure)
```

**핵심**: 의존성은 항상 **외부에서 내부로** 흐릅니다.
- Router는 UseCase를 알지만, UseCase는 Router를 모릅니다.
- Service는 Repository를 알지만, Repository는 Service를 모릅니다.

## 📝 새로운 기능 추가 시 가이드

### 예시: PII 탐지 기록 저장 기능 추가

#### 1. Infrastructure Layer 먼저 구현

```python
# app/models/pii_detection.py
class PIIDetection(Base):
    __tablename__ = "pii_detections"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str]
    has_pii: Mapped[bool]
    detected_at: Mapped[datetime]

# app/repository/pii_detection_repo.py
class PIIDetectionRepository:
    async def create(self, user_id: int, text: str, has_pii: bool):
        # DB 저장 로직
```

#### 2. Domain Layer 구현

```python
# app/services/pii_service.py
class PIIDetectionService:
    def __init__(self, db: AsyncSession):
        self.repository = PIIDetectionRepository(db)
        self.detector = get_pii_detector()
    
    async def detect_and_analyze(self, text: str) -> PIIDetectionResult:
        # 도메인 규칙: 텍스트 길이 검증
        if len(text) > 10000:
            raise ValueError("텍스트가 너무 깁니다")
        
        # PII 탐지
        result = await self.detector.detect_pii(text)
        return result
    
    async def save_detection(self, user_id: int, text: str, has_pii: bool):
        return await self.repository.create(user_id, text, has_pii)
```

#### 3. Application Layer 구현

```python
# app/usecases/pii_usecases.py
class DetectAndSavePIIUseCase:
    """
    PII 탐지 및 저장 Use Case
    
    Flow:
    1. PIIDetectionService로 텍스트 분석
    2. PIIDetectionService로 결과 저장
    3. 결과 반환
    """
    def __init__(self, db: AsyncSession):
        self.pii_service = PIIDetectionService(db)
    
    async def execute(self, user_id: int, text: str):
        # 1. 탐지
        result = await self.pii_service.detect_and_analyze(text)
        
        # 2. 저장
        await self.pii_service.save_detection(user_id, text, result.has_pii)
        
        # 3. 반환
        return result
```

#### 4. Presentation Layer 구현

```python
# app/api/routers/pii.py
@router.post("/detect")
async def detect_pii(
    request: PIIDetectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        use_case = DetectAndSavePIIUseCase(db)
        result = await use_case.execute(current_user.id, request.text)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## ✅ 아키텍처 체크리스트

새로운 코드를 작성할 때 다음을 확인하세요:

### Router (Presentation)
- [ ] HTTP 요청/응답 처리만 수행하는가?
- [ ] UseCase를 호출하는가?
- [ ] 비즈니스 로직이 없는가?
- [ ] Repository를 직접 호출하지 않는가?

### UseCase (Application)
- [ ] 하나의 사용자 의도를 나타내는가?
- [ ] 여러 Service를 조합하여 흐름을 만드는가?
- [ ] HTTP 관련 코드가 없는가?
- [ ] 도메인 규칙은 Service에 위임하는가?

### Service (Domain)
- [ ] 단일 도메인 엔티티에 집중하는가?
- [ ] 도메인 규칙을 검증하는가?
- [ ] Repository를 통해 데이터에 접근하는가?
- [ ] HTTP나 프레임워크에 의존하지 않는가?

### Repository (Infrastructure)
- [ ] 데이터 접근만 담당하는가?
- [ ] 비즈니스 로직이 없는가?
- [ ] SQL/ORM 쿼리만 포함하는가?

## 🎓 참고 자료

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design by Eric Evans](https://www.domainlanguage.com/ddd/)
- [Hexagonal Architecture (Ports and Adapters)](https://alistair.cockburn.us/hexagonal-architecture/)

---

**작성일**: 2025-10-11  
**버전**: v1.1.0
