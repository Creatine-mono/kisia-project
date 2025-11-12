"""
Elasticsearch 클라이언트 초기화 및 관리
"""
from elasticsearch import AsyncElasticsearch
from app.core.config import settings


class ElasticsearchClient:
    """Elasticsearch 클라이언트 싱글톤"""

    _instance: AsyncElasticsearch | None = None

    @classmethod
    async def get_client(cls) -> AsyncElasticsearch:
        """Elasticsearch 클라이언트 인스턴스 반환 (싱글톤)"""
        if cls._instance is None:
            cls._instance = AsyncElasticsearch(
                hosts=[settings.elasticsearch_url],
                retry_on_timeout=True,
                max_retries=3,
                request_timeout=30,
            )
        return cls._instance

    @classmethod
    async def close_client(cls) -> None:
        """Elasticsearch 클라이언트 종료"""
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None

    @classmethod
    async def health_check(cls) -> dict:
        """Elasticsearch 헬스 체크"""
        try:
            client = await cls.get_client()
            health = await client.cluster.health()
            return {
                "status": "healthy",
                "cluster_name": health["cluster_name"],
                "cluster_status": health["status"],
                "number_of_nodes": health["number_of_nodes"],
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }


async def get_elasticsearch_client() -> AsyncElasticsearch:
    """FastAPI 의존성 주입용 헬퍼 함수"""
    return await ElasticsearchClient.get_client()