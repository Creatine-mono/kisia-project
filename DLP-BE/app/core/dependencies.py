"""
인증 의존성 (Dependency Injection)

역할:
- FastAPI 의존성 주입
- UseCase를 통한 인증 처리
- HTTP 예외 처리
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.usecases.auth_usecases import GetCurrentUserUseCase, ValidateSuperuserUseCase
from app.models.user import User

# OAuth2 스키마
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    현재 로그인한 사용자 조회
    
    UseCase를 통해 토큰 검증 및 사용자 조회 수행
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Use Case 실행
        use_case = GetCurrentUserUseCase(db)
        user = await use_case.execute(token)
        
        return user
    
    except ValueError:
        raise credentials_exception


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    관리자 권한 확인
    
    UseCase를 통해 슈퍼유저 권한 검증 수행
    """
    try:
        # Use Case 실행
        use_case = ValidateSuperuserUseCase(db)
        superuser = await use_case.execute(current_user)
        
        return superuser
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
