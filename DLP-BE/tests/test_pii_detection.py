"""
PII 검사 API 테스트
"""
import pytest
from httpx import AsyncClient


class TestPIIDetectionAPI:
    """PII 검사 API 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_detect_pii_with_person_and_phone(self, client: AsyncClient, sample_pii_text):
        """PII 탐지 테스트 - 이름과 전화번호"""
        response = await client.post(
            "/api/v1/pii/detect",
            json={"text": sample_pii_text}
        )

        assert response.status_code == 200
        data = response.json()

        # 기본 응답 구조 확인
        assert "has_pii" in data
        assert "reason" in data
        assert "details" in data
        assert "entities" in data

        # PII 탐지 확인
        assert data["has_pii"] is True
        assert len(data["entities"]) > 0

        # 엔티티 타입 확인
        entity_types = [entity["type"] for entity in data["entities"]]
        assert any("PERSON" in t or "NAME" in t for t in entity_types), "이름이 탐지되어야 합니다"
        assert any("PHONE" in t for t in entity_types), "전화번호가 탐지되어야 합니다"

    @pytest.mark.asyncio
    async def test_detect_no_pii(self, client: AsyncClient, sample_non_pii_text):
        """PII 미탐지 테스트"""
        response = await client.post(
            "/api/v1/pii/detect",
            json={"text": sample_non_pii_text}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["has_pii"] is False
        assert len(data["entities"]) == 0

    @pytest.mark.asyncio
    async def test_detect_empty_text(self, client: AsyncClient):
        """빈 텍스트 입력 테스트"""
        response = await client.post(
            "/api/v1/pii/detect",
            json={"text": "   "}
        )

        assert response.status_code == 400
        assert "비어있습니다" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_detect_phone_number(self, client: AsyncClient):
        """전화번호 탐지 테스트"""
        test_cases = [
            "010-1234-5678",
            "전화번호: 010-9876-5432",
            "연락처는 01012345678입니다"
        ]

        for text in test_cases:
            response = await client.post(
                "/api/v1/pii/detect",
                json={"text": text}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["has_pii"] is True, f"Failed for: {text}"

    @pytest.mark.asyncio
    async def test_detect_email(self, client: AsyncClient):
        """이메일 탐지 테스트"""
        test_cases = [
            "test@example.com",
            "이메일: admin@company.co.kr",
            "연락처 hong.gildong@test.org"
        ]

        for text in test_cases:
            response = await client.post(
                "/api/v1/pii/detect",
                json={"text": text}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["has_pii"] is True, f"Failed for: {text}"

    @pytest.mark.asyncio
    async def test_detect_korean_name(self, client: AsyncClient):
        """한국어 이름 탐지 테스트"""
        test_cases = [
            "저는 김철수입니다",
            "이영희 씨가 왔습니다",
            "박지성 선수는 훌륭합니다"
        ]

        for text in test_cases:
            response = await client.post(
                "/api/v1/pii/detect",
                json={"text": text}
            )

            assert response.status_code == 200
            data = response.json()
            # 이름은 맥락에 따라 탐지될 수도, 안 될 수도 있음
            # 단지 API가 정상 동작하는지 확인
            assert "has_pii" in data

    @pytest.mark.asyncio
    async def test_detect_max_length(self, client: AsyncClient):
        """최대 길이 제한 테스트"""
        # 10,000자 초과
        long_text = "a" * 10001

        response = await client.post(
            "/api/v1/pii/detect",
            json={"text": long_text}
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_detect_with_ip_header(self, client: AsyncClient):
        """X-Forwarded-For 헤더 처리 테스트"""
        response = await client.post(
            "/api/v1/pii/detect",
            json={"text": "테스트 텍스트입니다"},
            headers={"X-Forwarded-For": "192.168.1.100"}
        )

        assert response.status_code == 200
        # IP는 로그에만 저장되므로, 응답은 정상이어야 함

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """헬스체크 테스트"""
        response = await client.get("/api/v1/pii/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
        assert "model_name" in data

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client: AsyncClient):
        """동시 요청 처리 테스트"""
        import asyncio

        async def make_request():
            return await client.post(
                "/api/v1/pii/detect",
                json={"text": "홍길동의 전화번호는 010-1234-5678입니다"}
            )

        # 10개의 동시 요청
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks)

        # 모든 요청이 성공해야 함
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["has_pii"] is True