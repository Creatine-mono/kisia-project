"""
인증 API (Presentation Layer)

역할:
- HTTP 요청/응답 처리
- 입력 검증 (Pydantic)
- UseCase 호출
- HTTP 상태 코드 및 예외 처리

비즈니스 로직은 포함하지 않음 (UseCase에 위임)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import UserRegister, Token, UserResponse
from app.models.user import User
from app.usecases.auth_usecases import (
    RegisterUserUseCase,
    LoginUseCase,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    회원가입
    
    - **username**: 사용자명 (3-50자, 고유값)
    - **email**: 이메일 주소 (고유값)
    - **password**: 비밀번호 (최소 8자)
    - **full_name**: 이름 (선택)
    """
    try:
        # Use Case 실행
        use_case = RegisterUserUseCase(db)
        user = await use_case.execute(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        return user
    
    except ValueError as e:
        # 도메인 규칙 위반 (중복 등)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    로그인
    
    - **username**: 사용자명
    - **password**: 비밀번호
    
    성공 시 JWT 액세스 토큰 반환
    """
    try:
        # Use Case 실행
        use_case = LoginUseCase(db)
        token_data = await use_case.execute(
            username=form_data.username,
            password=form_data.password
        )
        
        return token_data
    
    except ValueError as e:
        # 자격 증명 오류 또는 비활성 사용자
        error_message = str(e)
        
        if "비활성화" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_message,
                headers={"WWW-Authenticate": "Bearer"},
            )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    현재 로그인한 사용자 정보 조회
    
    JWT 토큰 필요
    
    Note: 이 엔드포인트는 get_current_user dependency에서 이미 UseCase를 통해
    사용자를 조회하므로, 추가적인 Use Case 호출이 필요 없음
    """
    return current_user
