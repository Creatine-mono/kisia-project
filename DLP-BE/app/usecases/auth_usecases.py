"""
인증 Use Cases (Application Layer)

Use Case는 여러 서비스를 조합하여 애플리케이션 수준의 비즈니스 흐름을 정의합니다.
각 Use Case는 하나의 사용자 의도(User Story)를 나타냅니다.
"""
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth.user_service import UserService
from app.services.auth.token_service import TokenService
from app.models.user import User


class RegisterUserUseCase:
    """
    회원가입 Use Case
    
    User Story: 사용자가 계정을 생성한다
    
    Flow:
    1. UserService를 통해 사용자 생성 (중복 검증 포함)
    2. 생성된 사용자 정보 반환
    """
    
    def __init__(self, db: AsyncSession):
        self.user_service = UserService(db)
    
    async def execute(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str | None = None
    ) -> User:
        """
        회원가입 실행
        
        Args:
            username: 사용자명
            email: 이메일
            password: 비밀번호 (평문)
            full_name: 이름 (선택)
        
        Returns:
            생성된 User 엔티티
        
        Raises:
            ValueError: 중복된 사용자명 또는 이메일
        """
        # UserService를 통해 사용자 생성 (도메인 규칙 검증 포함)
        user = await self.user_service.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
        
        return user


class LoginUseCase:
    """
    로그인 Use Case
    
    User Story: 사용자가 로그인하여 액세스 토큰을 받는다
    
    Flow:
    1. UserService를 통해 자격 증명 검증
    2. 사용자 활성화 상태 확인
    3. TokenService를 통해 액세스 토큰 생성
    4. 토큰 정보 반환
    """
    
    def __init__(self, db: AsyncSession):
        self.user_service = UserService(db)
        self.token_service = TokenService()
    
    async def execute(
        self,
        username: str,
        password: str
    ) -> dict[str, str]:
        """
        로그인 실행
        
        Args:
            username: 사용자명
            password: 비밀번호
        
        Returns:
            dict: {"access_token": str, "token_type": str}
        
        Raises:
            ValueError: 자격 증명 오류 또는 비활성 사용자
        """
        # 1. 자격 증명 검증
        user = await self.user_service.verify_user_credentials(username, password)
        
        if not user:
            raise ValueError("사용자명 또는 비밀번호가 올바르지 않습니다")
        
        # 2. 사용자 활성화 상태 확인
        if not await self.user_service.is_user_active(user):
            raise ValueError("비활성화된 사용자입니다")
        
        # 3. 액세스 토큰 생성
        access_token = self.token_service.create_user_access_token(username=user.username)
        
        # 4. 토큰 정보 반환
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


class GetCurrentUserUseCase:
    """
    현재 사용자 정보 조회 Use Case
    
    User Story: 로그인한 사용자가 자신의 정보를 조회한다
    
    Flow:
    1. TokenService를 통해 토큰에서 사용자명 추출
    2. UserService를 통해 사용자 정보 조회
    3. 사용자 정보 반환
    """
    
    def __init__(self, db: AsyncSession):
        self.user_service = UserService(db)
        self.token_service = TokenService()
    
    async def execute(self, token: str) -> User:
        """
        현재 사용자 정보 조회 실행
        
        Args:
            token: JWT 액세스 토큰
        
        Returns:
            User 엔티티
        
        Raises:
            ValueError: 유효하지 않은 토큰 또는 사용자 없음
        """
        # 1. 토큰에서 사용자명 추출
        username = self.token_service.extract_username_from_token(token)
        
        if username is None:
            raise ValueError("유효하지 않은 인증 정보입니다")
        
        # 2. 사용자 정보 조회
        user = await self.user_service.get_user_by_username(username)
        
        if user is None:
            raise ValueError("사용자를 찾을 수 없습니다")
        
        # 3. 사용자 정보 반환
        return user


class ValidateSuperuserUseCase:
    """
    슈퍼유저 권한 검증 Use Case
    
    User Story: 관리자만 접근할 수 있는 기능에 대한 권한 검증
    
    Flow:
    1. UserService를 통해 슈퍼유저 여부 확인
    2. 권한 없으면 예외 발생
    """
    
    def __init__(self, db: AsyncSession):
        self.user_service = UserService(db)
    
    async def execute(self, user: User) -> User:
        """
        슈퍼유저 권한 검증 실행
        
        Args:
            user: 검증할 User 엔티티
        
        Returns:
            User 엔티티 (검증 통과 시)
        
        Raises:
            ValueError: 슈퍼유저 권한 없음
        """
        if not await self.user_service.is_user_superuser(user):
            raise ValueError("슈퍼유저 권한이 필요합니다")
        
        return user
