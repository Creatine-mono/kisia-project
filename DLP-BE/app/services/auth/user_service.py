"""
사용자 관리 서비스 (도메인 비즈니스 로직)

DDD Service Layer:
- 단일 도메인 엔티티(User)에 대한 비즈니스 로직
- Repository와 상호작용하여 데이터 접근
- 도메인 규칙 검증
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.user_repo import UserRepository
from app.models.user import User


class UserService:
    """사용자 도메인 서비스"""
    
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str | None = None
    ) -> User:
        """
        새로운 사용자 생성
        
        비즈니스 규칙:
        - 사용자명 중복 불가
        - 이메일 중복 불가
        """
        # 비즈니스 규칙 검증: 중복 체크
        if await self.repository.get_by_username(username):
            raise ValueError(f"사용자명 '{username}'이 이미 존재합니다")
        
        if await self.repository.get_by_email(email):
            raise ValueError(f"이메일 '{email}'이 이미 존재합니다")
        
        # 사용자 생성
        user = await self.repository.create(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
        
        return user
    
    async def get_user_by_username(self, username: str) -> User | None:
        """사용자명으로 사용자 조회"""
        return await self.repository.get_by_username(username)
    
    async def get_user_by_email(self, email: str) -> User | None:
        """이메일로 사용자 조회"""
        return await self.repository.get_by_email(email)
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        """ID로 사용자 조회"""
        return await self.repository.get_by_id(user_id)
    
    async def verify_user_credentials(self, username: str, password: str) -> User | None:
        """
        사용자 자격 증명 검증
        
        비즈니스 규칙:
        - 사용자 존재 여부 확인
        - 비밀번호 일치 여부 확인
        - 활성화 상태 확인
        """
        from app.core.security import verify_password
        
        user = await self.get_user_by_username(username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def is_user_active(self, user: User) -> bool:
        """사용자 활성화 상태 확인"""
        return user.is_active
    
    async def is_user_superuser(self, user: User) -> bool:
        """사용자 슈퍼유저 여부 확인"""
        return user.is_superuser
