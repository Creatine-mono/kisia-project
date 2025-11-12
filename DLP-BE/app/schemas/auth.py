"""
인증 관련 스키마
"""
from pydantic import BaseModel, EmailStr, Field


# 회원가입
class UserRegister(BaseModel):
    """회원가입 요청"""
    username: str = Field(..., min_length=3, max_length=50, description="사용자명 (3-50자)")
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., min_length=8, max_length=100, description="비밀번호 (최소 8자)")
    full_name: str | None = Field(None, max_length=100, description="이름 (선택)")


# 로그인
class UserLogin(BaseModel):
    """로그인 요청"""
    username: str = Field(..., description="사용자명")
    password: str = Field(..., description="비밀번호")


# 토큰
class Token(BaseModel):
    """JWT 토큰 응답"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """토큰 데이터"""
    username: str | None = None


# 사용자 정보
class UserResponse(BaseModel):
    """사용자 정보 응답"""
    id: int
    username: str
    email: str
    full_name: str | None
    is_active: bool
    is_superuser: bool
    
    class Config:
        from_attributes = True
