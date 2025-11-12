"""
User Repository
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import get_password_hash


class UserRepository:
    """사용자 데이터 접근 레이어"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self, 
        username: str, 
        email: str, 
        password: str, 
        full_name: str | None = None
    ) -> User:
        """사용자 생성"""
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=False
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_by_username(self, username: str) -> User | None:
        """username으로 사용자 조회"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User | None:
        """email로 사용자 조회"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> User | None:
        """ID로 사용자 조회"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
