"""
관리자 대시보드 API (JWT 인증 필수)
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.log_service import PIILogService
from app.schemas.log import (
    LogListResponse,
    StatisticsOverview,
    TimelineResponse,
    PIITypeStatisticsResponse,
    IPStatisticsResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
log_service = PIILogService()


@router.get("/logs",
            response_model=LogListResponse,
            summary="PII 검사 로그 조회",
            description="관리자 전용: PII 검사 로그를 조회합니다. 필터링 및 페이징 지원. 기본 조회 기간: 최근 24시간")
async def get_logs(
    start_date: datetime | None = Query(None, description="시작 날짜 (ISO 8601, 기본: 24시간 전)"),
    end_date: datetime | None = Query(None, description="종료 날짜 (ISO 8601, 기본: 현재)"),
    client_ip: str | None = Query(None, description="클라이언트 IP 주소 필터"),
    has_pii: bool | None = Query(None, description="PII 탐지 여부 필터 (true/false)"),
    entity_type: str | None = Query(None, description="PII 타입 필터 (PERSON, PHONE_NUM 등)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기 (1-100)"),
    sort: str = Query("timestamp:desc", description="정렬 (field:asc 또는 field:desc)"),
    current_user: User = Depends(get_current_user)
):
    """
    PII 검사 로그 조회 (관리자 전용)

    - 날짜 범위 기본값: 최근 24시간
    - IP, PII 여부, 엔티티 타입으로 필터링 가능
    - 페이징 지원
    """
    try:
        # 기본값 설정: 24시간 전부터 현재까지
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(hours=24)
        if end_date is None:
            end_date = datetime.utcnow()

        logger.info(
            f"Admin {current_user.username} requested logs: "
            f"start={start_date}, end={end_date}, ip={client_ip}, has_pii={has_pii}"
        )

        result = await log_service.get_logs(
            start_date=start_date,
            end_date=end_date,
            client_ip=client_ip,
            has_pii=has_pii,
            entity_type=entity_type,
            page=page,
            page_size=page_size,
            sort=sort
        )

        return result

    except Exception as e:
        logger.error(f"Failed to get logs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그 조회 중 오류가 발생했습니다."
        )


@router.get("/statistics/overview",
            response_model=StatisticsOverview,
            summary="전체 통계 개요",
            description="관리자 전용: 지정된 기간의 전체 PII 검사 통계를 조회합니다. 기본 조회 기간: 최근 24시간")
async def get_statistics_overview(
    start_date: datetime | None = Query(None, description="시작 날짜 (ISO 8601, 기본: 24시간 전)"),
    end_date: datetime | None = Query(None, description="종료 날짜 (ISO 8601, 기본: 현재)"),
    current_user: User = Depends(get_current_user)
):
    """
    전체 통계 개요 (관리자 전용)

    반환 정보:
    - 총 요청 수
    - PII 탐지 요청 수 및 비율
    - 평균 응답 시간
    - 고유 IP 수
    - Top PII 타입
    - Top IP 주소
    - 기본 조회 기간: 최근 24시간
    """
    try:
        # 기본값 설정: 24시간 전부터 현재까지
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(hours=24)
        if end_date is None:
            end_date = datetime.utcnow()

        logger.info(
            f"Admin {current_user.username} requested statistics overview: "
            f"start={start_date}, end={end_date}"
        )

        result = await log_service.get_statistics_overview(
            start_date=start_date,
            end_date=end_date
        )

        return result

    except Exception as e:
        logger.error(f"Failed to get statistics overview: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="통계 조회 중 오류가 발생했습니다."
        )


@router.get("/statistics/timeline",
            response_model=TimelineResponse,
            summary="시간대별 추세 분석",
            description="관리자 전용: 시간대별 PII 검사 추세를 조회합니다. 기본 조회 기간: 최근 24시간")
async def get_statistics_timeline(
    start_date: datetime | None = Query(None, description="시작 날짜 (ISO 8601, 기본: 24시간 전)"),
    end_date: datetime | None = Query(None, description="종료 날짜 (ISO 8601, 기본: 현재)"),
    interval: str = Query("1h", description="집계 간격 (1h, 1d, 1w, 1M 등)"),
    current_user: User = Depends(get_current_user)
):
    """
    시간대별 추세 분석 (관리자 전용)

    - interval: Elasticsearch calendar_interval 형식
      - "1h": 1시간 단위
      - "1d": 1일 단위
      - "1w": 1주일 단위
      - "1M": 1개월 단위
    - 기본 조회 기간: 최근 24시간
    """
    try:
        # 기본값 설정: 24시간 전부터 현재까지
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(hours=24)
        if end_date is None:
            end_date = datetime.utcnow()

        logger.info(
            f"Admin {current_user.username} requested timeline: "
            f"start={start_date}, end={end_date}, interval={interval}"
        )

        result = await log_service.get_statistics_timeline(
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        return result

    except Exception as e:
        logger.error(f"Failed to get statistics timeline: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="시간대별 통계 조회 중 오류가 발생했습니다."
        )


@router.get("/statistics/by-pii-type",
            response_model=PIITypeStatisticsResponse,
            summary="PII 타입별 통계",
            description="관리자 전용: PII 타입별 탐지 통계를 조회합니다. 기본 조회 기간: 최근 24시간")
async def get_statistics_by_pii_type(
    start_date: datetime | None = Query(None, description="시작 날짜 (ISO 8601, 기본: 24시간 전)"),
    end_date: datetime | None = Query(None, description="종료 날짜 (ISO 8601, 기본: 현재)"),
    current_user: User = Depends(get_current_user)
):
    """
    PII 타입별 통계 (관리자 전용)

    반환 정보:
    - 각 PII 타입별 탐지 횟수
    - 전체 대비 비율
    - 평균 신뢰도
    - 기본 조회 기간: 최근 24시간
    """
    try:
        # 기본값 설정: 24시간 전부터 현재까지
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(hours=24)
        if end_date is None:
            end_date = datetime.utcnow()

        logger.info(
            f"Admin {current_user.username} requested PII type statistics: "
            f"start={start_date}, end={end_date}"
        )

        result = await log_service.get_statistics_by_pii_type(
            start_date=start_date,
            end_date=end_date
        )

        return result

    except Exception as e:
        logger.error(f"Failed to get PII type statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PII 타입별 통계 조회 중 오류가 발생했습니다."
        )


@router.get("/statistics/by-ip",
            response_model=IPStatisticsResponse,
            summary="IP별 통계",
            description="관리자 전용: IP 주소별 요청 및 탐지 통계를 조회합니다. 기본 조회 기간: 최근 24시간")
async def get_statistics_by_ip(
    start_date: datetime | None = Query(None, description="시작 날짜 (ISO 8601, 기본: 24시간 전)"),
    end_date: datetime | None = Query(None, description="종료 날짜 (ISO 8601, 기본: 현재)"),
    size: int = Query(20, ge=1, le=100, description="조회할 IP 개수 (1-100)"),
    current_user: User = Depends(get_current_user)
):
    """
    IP별 통계 (관리자 전용)

    반환 정보:
    - IP 주소별 총 요청 수
    - PII 탐지 요청 수 및 비율
    - 가장 많이 탐지된 PII 타입
    - 기본 조회 기간: 최근 24시간
    """
    try:
        # 기본값 설정: 24시간 전부터 현재까지
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(hours=24)
        if end_date is None:
            end_date = datetime.utcnow()

        logger.info(
            f"Admin {current_user.username} requested IP statistics: "
            f"start={start_date}, end={end_date}, size={size}"
        )

        result = await log_service.get_statistics_by_ip(
            start_date=start_date,
            end_date=end_date,
            size=size
        )

        return result

    except Exception as e:
        logger.error(f"Failed to get IP statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="IP별 통계 조회 중 오류가 발생했습니다."
        )