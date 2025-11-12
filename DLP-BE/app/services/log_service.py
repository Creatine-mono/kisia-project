"""
PII 검사 로그 서비스
"""
from datetime import datetime
import logging

from app.schemas.pii import PIIDetectionResponse
from app.schemas.log import (
    PIILogCreate,
    PIILogResponse,
    LogListResponse,
    StatisticsOverview,
    TimelineResponse,
    TimelineDataPoint,
    PIITypeStatistics,
    PIITypeStatisticsResponse,
    IPStatistics,
    IPStatisticsResponse
)
from app.repository.elasticsearch_repo import ElasticsearchRepository
from app.core.elasticsearch import get_elasticsearch_client

logger = logging.getLogger(__name__)


class PIILogService:
    """PII 검사 로그 서비스"""

    async def log_detection(
        self,
        client_ip: str,
        original_text: str,
        result: PIIDetectionResponse,
        response_time_ms: float
    ) -> None:
        """
        PII 검사 결과를 Elasticsearch에 저장

        Args:
            client_ip: 클라이언트 IP 주소
            original_text: 원문 텍스트
            result: PII 탐지 결과
            response_time_ms: 응답 시간 (밀리초)
        """
        try:
            es_client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(es_client)

            # 엔티티 타입 추출
            entity_types = list(set(entity.type for entity in result.entities))

            # 로그 데이터 생성
            log_data = PIILogCreate(
                client_ip=client_ip,
                original_text=original_text,
                text_length=len(original_text),
                has_pii=result.has_pii,
                detected_entities=[entity.model_dump() for entity in result.entities],
                entity_types=entity_types,
                entity_count=len(result.entities),
                blocked=result.has_pii or result.policy_violation,  # PII 또는 정책 위반 시 차단
                reason=result.reason,
                response_time_ms=response_time_ms,
                # 정책 위반 정보
                policy_violation=result.policy_violation,
                policy_judgment=result.policy_judgment,
                policy_confidence=result.policy_confidence
            )

            # Elasticsearch에 저장
            doc_id = await repo.index_log(log_data.model_dump())
            logger.info(f"Logged PII detection result: {doc_id} (IP: {client_ip}, has_pii: {result.has_pii})")

        except Exception as e:
            # 로깅 실패해도 메인 요청은 성공 처리
            logger.error(f"Failed to log PII detection: {str(e)}", exc_info=True)

    async def get_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        client_ip: str | None = None,
        has_pii: bool | None = None,
        entity_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort: str = "timestamp:desc"
    ) -> LogListResponse:
        """
        로그 조회 (페이징, 필터링)

        Returns:
            LogListResponse: 로그 목록 및 페이징 정보
        """
        try:
            es_client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(es_client)

            result = await repo.search_logs(
                start_date=start_date,
                end_date=end_date,
                client_ip=client_ip,
                has_pii=has_pii,
                entity_type=entity_type,
                page=page,
                page_size=page_size,
                sort=sort
            )

            logs = [
                PIILogResponse(
                    id=hit["id"],
                    timestamp=datetime.fromisoformat(hit["timestamp"].replace("Z", "+00:00")),
                    **{k: v for k, v in hit.items() if k != "id" and k != "timestamp"}
                )
                for hit in result["hits"]
            ]

            return LogListResponse(
                total=result["total"],
                page=page,
                page_size=page_size,
                logs=logs
            )

        except Exception as e:
            logger.error(f"Failed to get logs: {str(e)}", exc_info=True)
            raise

    async def get_statistics_overview(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> StatisticsOverview:
        """
        전체 통계 개요 조회

        Returns:
            StatisticsOverview: 전체 통계 데이터
        """
        try:
            es_client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(es_client)

            aggs = await repo.aggregate_statistics(start_date, end_date)

            if not aggs:
                # 데이터 없을 때 기본값
                return StatisticsOverview(
                    period={"start": start_date.isoformat(), "end": end_date.isoformat()},
                    total_requests=0,
                    detected_requests=0,
                    detection_rate=0.0,
                    blocked_requests=0,
                    blocked_rate=0.0,
                    avg_response_time_ms=0.0,
                    unique_ips=0,
                    top_detected_types=[],
                    top_ips=[]
                )

            total_requests = aggs["total_requests"]["value"]
            detected_requests = aggs["detected_requests"]["doc_count"]
            detection_rate = (detected_requests / total_requests * 100) if total_requests > 0 else 0.0

            # Top PII 타입
            top_detected_types = [
                {
                    "type": bucket["key"],
                    "count": bucket["doc_count"],
                    "percentage": round(bucket["doc_count"] / detected_requests * 100, 2) if detected_requests > 0 else 0.0
                }
                for bucket in aggs["top_pii_types"]["buckets"]
            ]

            # Top IPs
            top_ips = [
                {
                    "client_ip": bucket["key"],
                    "request_count": bucket["doc_count"],
                    "detection_count": bucket["detected_count"]["doc_count"]
                }
                for bucket in aggs["top_ips"]["buckets"]
            ]

            return StatisticsOverview(
                period={"start": start_date.isoformat(), "end": end_date.isoformat()},
                total_requests=int(total_requests),
                detected_requests=detected_requests,
                detection_rate=round(detection_rate, 2),
                blocked_requests=detected_requests,  # PII 탐지 = 차단
                blocked_rate=round(detection_rate, 2),
                avg_response_time_ms=round(aggs["avg_response_time"]["value"] or 0.0, 2),
                unique_ips=aggs["unique_ips"]["value"],
                top_detected_types=top_detected_types,
                top_ips=top_ips
            )

        except Exception as e:
            logger.error(f"Failed to get statistics overview: {str(e)}", exc_info=True)
            raise

    async def get_statistics_timeline(
        self,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> TimelineResponse:
        """
        시간대별 추세 분석

        Args:
            interval: "1h", "1d", "1w" 등
        """
        try:
            es_client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(es_client)

            buckets = await repo.aggregate_timeline(start_date, end_date, interval)

            timeline = [
                TimelineDataPoint(
                    timestamp=datetime.fromisoformat(bucket["key_as_string"].replace("Z", "+00:00")),
                    total_requests=bucket["doc_count"],
                    detected_requests=bucket["detected_count"]["doc_count"],
                    detection_rate=round(
                        bucket["detected_count"]["doc_count"] / bucket["doc_count"] * 100, 2
                    ) if bucket["doc_count"] > 0 else 0.0
                )
                for bucket in buckets
            ]

            return TimelineResponse(timeline=timeline)

        except Exception as e:
            logger.error(f"Failed to get statistics timeline: {str(e)}", exc_info=True)
            raise

    async def get_statistics_by_pii_type(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> PIITypeStatisticsResponse:
        """
        PII 타입별 통계
        """
        try:
            es_client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(es_client)

            aggs = await repo.aggregate_statistics(start_date, end_date)

            if not aggs or "top_pii_types" not in aggs:
                return PIITypeStatisticsResponse(statistics=[])

            total_detected = sum(bucket["doc_count"] for bucket in aggs["top_pii_types"]["buckets"])

            statistics = [
                PIITypeStatistics(
                    pii_type=bucket["key"],
                    count=bucket["doc_count"],
                    percentage=round(bucket["doc_count"] / total_detected * 100, 2) if total_detected > 0 else 0.0,
                    avg_confidence=0.0  # 추후 구현
                )
                for bucket in aggs["top_pii_types"]["buckets"]
            ]

            return PIITypeStatisticsResponse(statistics=statistics)

        except Exception as e:
            logger.error(f"Failed to get statistics by PII type: {str(e)}", exc_info=True)
            raise

    async def get_statistics_by_ip(
        self,
        start_date: datetime,
        end_date: datetime,
        size: int = 20
    ) -> IPStatisticsResponse:
        """
        IP별 통계
        """
        try:
            es_client = await get_elasticsearch_client()
            repo = ElasticsearchRepository(es_client)

            buckets = await repo.aggregate_by_ip(start_date, end_date, size)

            statistics = [
                IPStatistics(
                    client_ip=bucket["key"],
                    total_requests=bucket["doc_count"],
                    detected_requests=bucket["detected_count"]["doc_count"],
                    detection_rate=round(
                        bucket["detected_count"]["doc_count"] / bucket["doc_count"] * 100, 2
                    ) if bucket["doc_count"] > 0 else 0.0,
                    most_detected_type=(
                        bucket["top_pii_type"]["buckets"][0]["key"]
                        if bucket["top_pii_type"]["buckets"] else None
                    )
                )
                for bucket in buckets
            ]

            return IPStatisticsResponse(statistics=statistics)

        except Exception as e:
            logger.error(f"Failed to get statistics by IP: {str(e)}", exc_info=True)
            raise
