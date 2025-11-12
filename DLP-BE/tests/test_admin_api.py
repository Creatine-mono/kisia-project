"""
관리자 대시보드 API 테스트
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
import asyncio


class TestAdminAuthenticationAPI:
    """인증 관련 테스트"""

    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient):
        """사용자 등록 테스트"""
        username = f"test_user_{datetime.now().timestamp()}"
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "password": "testpass123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == username

    @pytest.mark.asyncio
    async def test_login_user(self, client: AsyncClient):
        """로그인 테스트"""
        # 먼저 사용자 등록
        username = f"login_test_{datetime.now().timestamp()}"
        password = "testpass123"

        await client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": password}
        )

        # 로그인
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """잘못된 비밀번호 로그인 테스트"""
        username = f"wrong_pass_test_{datetime.now().timestamp()}"

        await client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "correct123"}
        )

        response = await client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "wrong123"}
        )

        assert response.status_code == 401


class TestAdminLogsAPI:
    """로그 조회 API 테스트"""

    @pytest.mark.asyncio
    async def test_get_logs_without_auth(self, client: AsyncClient):
        """인증 없이 로그 조회 시도"""
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        end_date = datetime.now().isoformat()

        response = await client.get(
            f"/api/v1/admin/logs?start_date={start_date}&end_date={end_date}"
        )

        assert response.status_code == 401  # Unauthorized

    @pytest.mark.asyncio
    async def test_get_logs_with_auth(self, client: AsyncClient, admin_token: str):
        """인증 후 로그 조회"""
        # 먼저 PII 검사 요청을 몇 개 생성 (로그 데이터 생성)
        await client.post("/api/v1/pii/detect", json={"text": "홍길동 010-1234-5678"})
        await client.post("/api/v1/pii/detect", json={"text": "평범한 텍스트"})

        # 로그 생성을 위해 잠시 대기
        await asyncio.sleep(2)

        # 로그 조회
        start_date = (datetime.now() - timedelta(days=1)).isoformat()
        end_date = datetime.now().isoformat()

        response = await client.get(
            f"/api/v1/admin/logs?start_date={start_date}&end_date={end_date}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "logs" in data
        assert isinstance(data["logs"], list)

    @pytest.mark.asyncio
    async def test_get_logs_with_filters(self, client: AsyncClient, admin_token: str):
        """필터링 옵션으로 로그 조회"""
        # 특정 IP로 요청 생성
        await client.post(
            "/api/v1/pii/detect",
            json={"text": "김철수 010-9999-8888"},
            headers={"X-Forwarded-For": "10.0.0.100"}
        )

        await asyncio.sleep(2)

        start_date = (datetime.now() - timedelta(days=1)).isoformat()
        end_date = datetime.now().isoformat()

        # has_pii 필터 적용
        response = await client.get(
            f"/api/v1/admin/logs?start_date={start_date}&end_date={end_date}&has_pii=true",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # 결과의 모든 로그가 has_pii=true여야 함
        for log in data["logs"]:
            assert log["has_pii"] is True

    @pytest.mark.asyncio
    async def test_get_logs_pagination(self, client: AsyncClient, admin_token: str):
        """페이징 테스트"""
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        end_date = datetime.now().isoformat()

        # 페이지 1
        response1 = await client.get(
            f"/api/v1/admin/logs?start_date={start_date}&end_date={end_date}&page=1&page_size=5",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["page"] == 1
        assert data1["page_size"] == 5


class TestAdminStatisticsAPI:
    """통계 API 테스트"""

    @pytest.mark.asyncio
    async def test_statistics_overview_without_auth(self, client: AsyncClient):
        """인증 없이 통계 조회 시도"""
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        end_date = datetime.now().isoformat()

        response = await client.get(
            f"/api/v1/admin/statistics/overview?start_date={start_date}&end_date={end_date}"
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_statistics_overview_with_auth(self, client: AsyncClient, admin_token: str):
        """전체 통계 조회"""
        # 테스트 데이터 생성
        await client.post("/api/v1/pii/detect", json={"text": "홍길동 010-1234-5678"})
        await client.post("/api/v1/pii/detect", json={"text": "평범한 텍스트"})

        await asyncio.sleep(2)

        start_date = (datetime.now() - timedelta(days=1)).isoformat()
        end_date = datetime.now().isoformat()

        response = await client.get(
            f"/api/v1/admin/statistics/overview?start_date={start_date}&end_date={end_date}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # 응답 구조 확인
        assert "period" in data
        assert "total_requests" in data
        assert "detected_requests" in data
        assert "detection_rate" in data
        assert "blocked_requests" in data
        assert "blocked_rate" in data
        assert "avg_response_time_ms" in data
        assert "unique_ips" in data
        assert "top_detected_types" in data
        assert "top_ips" in data

    @pytest.mark.asyncio
    async def test_statistics_timeline(self, client: AsyncClient, admin_token: str):
        """시간대별 통계 조회"""
        start_date = (datetime.now() - timedelta(days=1)).isoformat()
        end_date = datetime.now().isoformat()

        response = await client.get(
            f"/api/v1/admin/statistics/timeline?start_date={start_date}&end_date={end_date}&interval=1h",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "timeline" in data
        assert isinstance(data["timeline"], list)

    @pytest.mark.asyncio
    async def test_statistics_by_pii_type(self, client: AsyncClient, admin_token: str):
        """PII 타입별 통계 조회"""
        # 다양한 PII 타입 생성
        await client.post("/api/v1/pii/detect", json={"text": "홍길동"})
        await client.post("/api/v1/pii/detect", json={"text": "010-1234-5678"})
        await client.post("/api/v1/pii/detect", json={"text": "test@email.com"})

        await asyncio.sleep(2)

        start_date = (datetime.now() - timedelta(days=1)).isoformat()
        end_date = datetime.now().isoformat()

        response = await client.get(
            f"/api/v1/admin/statistics/by-pii-type?start_date={start_date}&end_date={end_date}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "statistics" in data
        assert isinstance(data["statistics"], list)

    @pytest.mark.asyncio
    async def test_statistics_by_ip(self, client: AsyncClient, admin_token: str):
        """IP별 통계 조회"""
        # 서로 다른 IP에서 요청 생성
        await client.post(
            "/api/v1/pii/detect",
            json={"text": "홍길동"},
            headers={"X-Forwarded-For": "192.168.1.1"}
        )
        await client.post(
            "/api/v1/pii/detect",
            json={"text": "김철수"},
            headers={"X-Forwarded-For": "192.168.1.2"}
        )

        await asyncio.sleep(2)

        start_date = (datetime.now() - timedelta(days=1)).isoformat()
        end_date = datetime.now().isoformat()

        response = await client.get(
            f"/api/v1/admin/statistics/by-ip?start_date={start_date}&end_date={end_date}&size=10",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "statistics" in data
        assert isinstance(data["statistics"], list)

        # IP별 통계 구조 확인
        if len(data["statistics"]) > 0:
            stat = data["statistics"][0]
            assert "client_ip" in stat
            assert "total_requests" in stat
            assert "detected_requests" in stat
            assert "detection_rate" in stat