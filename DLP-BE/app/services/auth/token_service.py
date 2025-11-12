"""
토큰 관리 서비스 (도메인 비즈니스 로직)

DDD Service Layer:
- JWT 토큰 생성 및 검증
- 토큰 관련 비즈니스 로직
"""
from datetime import timedelta
from app.core.security import create_access_token, decode_access_token
from app.core.config import settings


class TokenService:
    """토큰 도메인 서비스"""
    
    def create_user_access_token(self, username: str, expires_delta: timedelta | None = None) -> str:
        """
        사용자 액세스 토큰 생성
        
        Args:
            username: 사용자명
            expires_delta: 토큰 만료 시간 (기본값: 설정에서 가져옴)
        
        Returns:
            JWT 액세스 토큰
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        token_data = {"sub": username}
        access_token = create_access_token(data=token_data, expires_delta=expires_delta)
        
        return access_token
    
    def decode_token(self, token: str) -> dict | None:
        """
        토큰 디코딩 및 검증
        
        Args:
            token: JWT 토큰
        
        Returns:
            토큰 페이로드 (검증 실패 시 None)
        """
        return decode_access_token(token)
    
    def extract_username_from_token(self, token: str) -> str | None:
        """
        토큰에서 사용자명 추출
        
        Args:
            token: JWT 토큰
        
        Returns:
            사용자명 (추출 실패 시 None)
        """
        payload = self.decode_token(token)
        
        if payload is None:
            return None
        
        username: str | None = payload.get("sub")
        return username
