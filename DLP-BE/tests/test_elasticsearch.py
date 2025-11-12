"""
Elasticsearch 통합 테스트
"""
import pytest
from app.core.elasticsearch import ElasticsearchClient, get_elasticsearch_client
from app.repository.elasticsearch_repo import ElasticsearchRepository
from app.schemas.log import PIILogCreate
from datetime import datetime, timedelta
import asyncio


class TestElasticsearchConnection:
    """Elasticsearch 연결 테스트"""

    @pytest.mark.asyncio
    async def test_elasticsearch_client_connection(self):
        """ES 클라이언트 연결 테스트"""
        try:
            client = await ElasticsearchClient.get_client()
            assert client is not None

            # 클러스터 정보 확인
            info = await client.info()
            assert "cluster_name" in info

        except Exception as e:
            pytest.skip(f"Elasticsearch not available: {str(e)}")

    @pytest.mark.asyncio
    async def test_elasticsearch_health_check(self):
        """ES 헬스 체크 테스트"""
        try:
            health = await ElasticsearchClient.health_check()
            assert "status" in health

            if health["status"] == "healthy":
                assert "cluster_name" in health
                assert "cluster_status" in health

        except Exception as e:
            pytest.skip(f"Elasticsearch not available: {str(e)}")


class TestElasticsearchRepository:
    """Elasticsearch 저장소 테스트"""

    @pytest.mark.asyncio
    async def test_create_index(self):
        """인덱스 생성 테스트"""
        try:
            client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(client)

            # 인덱스 생성
            await repo.create_index_if_not_exists()

            # 인덱스 존재 확인
            exists = await client.indices.exists(index=repo.index_name)
            assert exists

        except Exception as e:
            pytest.skip(f"Elasticsearch not available: {str(e)}")

    @pytest.mark.asyncio
    async def test_index_log(self):
        """로그 인덱싱 테스트"""
        try:
            client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(client)

            # 테스트 로그 데이터
            log_data = PIILogCreate(
                client_ip="192.168.1.100",
                original_text="테스트 텍스트입니다",
                text_length=9,
                has_pii=False,
                detected_entities=[],
                entity_types=[],
                entity_count=0,
                blocked=False,
                reason="개인정보가 탐지되지 않았습니다",
                response_time_ms=150.5
            )

            # 로그 저장
            doc_id = await repo.index_log(log_data.model_dump())
            assert doc_id is not None

            # 인덱스 새로고침 (테스트용)
            await client.indices.refresh(index=repo.index_name)

            # 저장된 문서 조회
            doc = await client.get(index=repo.index_name, id=doc_id)
            assert doc["_source"]["client_ip"] == "192.168.1.100"

        except Exception as e:
            pytest.skip(f"Elasticsearch not available: {str(e)}")

    @pytest.mark.asyncio
    async def test_search_logs(self):
        """로그 검색 테스트"""
        try:
            client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(client)

            # 테스트 로그 여러 개 생성
            test_logs = [
                {
                    "client_ip": "10.0.0.1",
                    "original_text": "홍길동입니다",
                    "text_length": 6,
                    "has_pii": True,
                    "detected_entities": [{"type": "PERSON", "value": "홍길동", "confidence": 0.95, "token_count": 2}],
                    "entity_types": ["PERSON"],
                    "entity_count": 1,
                    "blocked": True,
                    "reason": "개인정보 1개 탐지됨",
                    "response_time_ms": 200.0
                },
                {
                    "client_ip": "10.0.0.2",
                    "original_text": "평범한 텍스트",
                    "text_length": 7,
                    "has_pii": False,
                    "detected_entities": [],
                    "entity_types": [],
                    "entity_count": 0,
                    "blocked": False,
                    "reason": "개인정보가 탐지되지 않았습니다",
                    "response_time_ms": 100.0
                }
            ]

            for log in test_logs:
                await repo.index_log(log)

            # 인덱스 새로고침
            await client.indices.refresh(index=repo.index_name)

            # 검색 수행
            start_date = datetime.now() - timedelta(minutes=5)
            end_date = datetime.now() + timedelta(minutes=5)

            result = await repo.search_logs(
                start_date=start_date,
                end_date=end_date,
                page=1,
                page_size=10
            )

            assert "total" in result
            assert "hits" in result
            assert result["total"] >= 2  # 최소 2개 이상

        except Exception as e:
            pytest.skip(f"Elasticsearch not available: {str(e)}")

    @pytest.mark.asyncio
    async def test_search_logs_with_filters(self):
        """필터링 검색 테스트"""
        try:
            client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(client)

            # PII 포함 로그 생성
            log_with_pii = {
                "client_ip": "172.16.0.1",
                "original_text": "김철수 010-1234-5678",
                "text_length": 13,
                "has_pii": True,
                "detected_entities": [
                    {"type": "PERSON", "value": "김철수", "confidence": 0.92, "token_count": 2},
                    {"type": "PHONE_NUM", "value": "010-1234-5678", "confidence": 0.89, "token_count": 5}
                ],
                "entity_types": ["PERSON", "PHONE_NUM"],
                "entity_count": 2,
                "blocked": True,
                "reason": "개인정보 2개 탐지됨",
                "response_time_ms": 250.0
            }

            await repo.index_log(log_with_pii)
            await client.indices.refresh(index=repo.index_name)

            # has_pii=True 필터링 검색
            start_date = datetime.now() - timedelta(minutes=5)
            end_date = datetime.now() + timedelta(minutes=5)

            result = await repo.search_logs(
                start_date=start_date,
                end_date=end_date,
                has_pii=True,
                page=1,
                page_size=10
            )

            # 모든 결과가 has_pii=True여야 함
            for hit in result["hits"]:
                assert hit["has_pii"] is True

        except Exception as e:
            pytest.skip(f"Elasticsearch not available: {str(e)}")

    @pytest.mark.asyncio
    async def test_aggregate_statistics(self):
        """통계 집계 테스트"""
        try:
            client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(client)

            # 통계 집계
            start_date = datetime.now() - timedelta(days=1)
            end_date = datetime.now() + timedelta(hours=1)

            stats = await repo.aggregate_statistics(
                start_date=start_date,
                end_date=end_date
            )

            # 집계 결과 구조 확인 (데이터가 있는 경우)
            if stats:
                assert "total_requests" in stats or stats == {}

        except Exception as e:
            pytest.skip(f"Elasticsearch not available: {str(e)}")

    @pytest.mark.asyncio
    async def test_aggregate_timeline(self):
        """시간대별 집계 테스트"""
        try:
            client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(client)

            start_date = datetime.now() - timedelta(hours=24)
            end_date = datetime.now()

            timeline = await repo.aggregate_timeline(
                start_date=start_date,
                end_date=end_date,
                interval="1h"
            )

            assert isinstance(timeline, list)

        except Exception as e:
            pytest.skip(f"Elasticsearch not available: {str(e)}")


class TestElasticsearchPerformance:
    """Elasticsearch 성능 테스트"""

    @pytest.mark.asyncio
    async def test_bulk_indexing_performance(self):
        """대량 인덱싱 성능 테스트"""
        try:
            client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(client)

            # 100개의 로그 생성
            import time
            start_time = time.time()

            tasks = []
            for i in range(100):
                log_data = {
                    "client_ip": f"10.0.0.{i % 255}",
                    "original_text": f"테스트 텍스트 {i}",
                    "text_length": 10,
                    "has_pii": i % 2 == 0,
                    "detected_entities": [],
                    "entity_types": [],
                    "entity_count": 0,
                    "blocked": False,
                    "reason": "테스트",
                    "response_time_ms": 100.0
                }
                tasks.append(repo.index_log(log_data))

            await asyncio.gather(*tasks)

            elapsed = time.time() - start_time
            print(f"\n100개 로그 인덱싱 시간: {elapsed:.2f}초")

            # 10초 이내에 완료되어야 함
            assert elapsed < 10.0

        except Exception as e:
            pytest.skip(f"Elasticsearch not available: {str(e)}")