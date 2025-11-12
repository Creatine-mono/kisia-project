"""
Pytest 공통 설정 및 Fixtures
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 fixture"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    """FastAPI 테스트 클라이언트"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def admin_token(client: AsyncClient):
    """관리자 JWT 토큰 생성"""
    # 테스트 관리자 계정 생성
    register_data = {
        "username": "test_admin",
        "password": "test_password123"
    }

    # 회원가입 시도 (이미 있으면 무시)
    await client.post("/api/v1/auth/register", json=register_data)

    # 로그인
    login_response = await client.post("/api/v1/auth/login", json=register_data)
    assert login_response.status_code == 200

    token_data = login_response.json()
    return token_data["access_token"]


@pytest.fixture
def sample_pii_text():
    """테스트용 PII 포함 텍스트"""
    return "저는 홍길동이고, 전화번호는 010-1234-5678입니다. 이메일은 hong@example.com입니다."


@pytest.fixture
def sample_non_pii_text():
    """테스트용 PII 미포함 텍스트"""
    return "오늘 날씨가 정말 좋습니다. 산책하기 좋은 날씨네요."