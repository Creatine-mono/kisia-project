"""
로그 스키마 정의 (IP 기반)
"""
from datetime import datetime
from pydantic import BaseModel, Field


class PIILogCreate(BaseModel):
    """PII 검사 로그 생성 스키마 (IP 기반)"""
    client_ip: str
    original_text: str
    text_length: int
    has_pii: bool
    detected_entities: list[dict]
    entity_types: list[str]
    entity_count: int
    blocked: bool
    reason: str
    response_time_ms: float
    # 정책 위반 관련 필드
    policy_violation: bool
    policy_judgment: str | None = None
    policy_confidence: float | None = None
    model_version: str = "psh3333/roberta-large-korean-pii5"
    api_version: str = "1.0.0"


class PIILogResponse(BaseModel):
    """PII 검사 로그 응답 스키마"""
    id: str
    timestamp: datetime
    client_ip: str
    original_text: str
    text_length: int
    has_pii: bool
    detected_entities: list[dict]
    entity_types: list[str]
    entity_count: int
    blocked: bool
    reason: str
    response_time_ms: float
    # 정책 위반 관련 필드 (기존 로그와의 호환성을 위해 기본값 제공)
    policy_violation: bool = False
    policy_judgment: str | None = None
    policy_confidence: float | None = None
    model_version: str
    api_version: str


class LogQueryParams(BaseModel):
    """로그 조회 쿼리 파라미터"""
    start_date: datetime
    end_date: datetime
    client_ip: str | None = None
    has_pii: bool | None = None
    entity_type: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort: str = "timestamp:desc"


class LogListResponse(BaseModel):
    """로그 목록 응답"""
    total: int
    page: int
    page_size: int
    logs: list[PIILogResponse]


class StatisticsOverview(BaseModel):
    """전체 통계 개요 (IP 기반)"""
    period: dict
    total_requests: int
    detected_requests: int
    detection_rate: float
    blocked_requests: int
    blocked_rate: float
    avg_response_time_ms: float
    unique_ips: int
    top_detected_types: list[dict]
    top_ips: list[dict]


class TimelineDataPoint(BaseModel):
    """시간대별 통계 데이터 포인트"""
    timestamp: datetime
    total_requests: int
    detected_requests: int
    detection_rate: float


class TimelineResponse(BaseModel):
    """시간대별 추세 응답"""
    timeline: list[TimelineDataPoint]


class PIITypeStatistics(BaseModel):
    """PII 타입별 통계"""
    pii_type: str
    count: int
    percentage: float
    avg_confidence: float


class PIITypeStatisticsResponse(BaseModel):
    """PII 타입별 통계 응답"""
    statistics: list[PIITypeStatistics]


class IPStatistics(BaseModel):
    """IP별 통계"""
    client_ip: str
    total_requests: int
    detected_requests: int
    detection_rate: float
    most_detected_type: str | None = None


class IPStatisticsResponse(BaseModel):
    """IP별 통계 응답"""
    statistics: list[IPStatistics]