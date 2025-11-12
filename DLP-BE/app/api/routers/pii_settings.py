"""
PII Settings 관리자 API (JWT 인증 필수)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.services.pii_settings_service import PIISettingsService
from app.schemas.pii_settings import (
    PIISettingsListResponse,
    PIISettingResponse,
    PIISettingUpdate
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("",
            response_model=PIISettingsListResponse,
            summary="PII 탐지 설정 전체 조회",
            description="관리자 전용: 모든 PII 탐지 설정을 조회합니다.")
async def get_all_pii_settings(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PIISettingsListResponse:
    """
    PII 탐지 설정 전체 조회 (관리자 전용)

    반환 정보:
    - 모든 PII 엔티티 타입의 활성화 여부 및 민감도 설정
    """
    try:
        logger.info(f"Admin {current_user.username} requested all PII settings")

        service = PIISettingsService(session)
        result = await service.get_all_settings()

        return result

    except Exception as e:
        logger.error(f"Failed to get PII settings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PII 설정 조회 중 오류가 발생했습니다."
        )


@router.get("/{entity_type}",
            response_model=PIISettingResponse,
            summary="특정 PII 타입 설정 조회",
            description="관리자 전용: 특정 PII 타입의 설정을 조회합니다.")
async def get_pii_setting(
    entity_type: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PIISettingResponse:
    """
    특정 PII 타입 설정 조회 (관리자 전용)

    - **entity_type**: PII 엔티티 타입 (PERSON, PHONE_NUM 등)
    """
    try:
        logger.info(f"Admin {current_user.username} requested PII setting: {entity_type}")

        service = PIISettingsService(session)
        result = await service.get_setting(entity_type)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PII 타입 '{entity_type}'의 설정을 찾을 수 없습니다."
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get PII setting for {entity_type}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PII 설정 조회 중 오류가 발생했습니다."
        )


@router.patch("/{entity_type}",
              response_model=PIISettingResponse,
              summary="PII 타입 설정 업데이트",
              description="관리자 전용: 특정 PII 타입의 활성화 여부 및 민감도를 업데이트합니다.")
async def update_pii_setting(
    entity_type: str,
    update_data: PIISettingUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PIISettingResponse:
    """
    PII 타입 설정 업데이트 (관리자 전용)

    - **entity_type**: PII 엔티티 타입 (PERSON, PHONE_NUM 등)
    - **enabled**: 탐지 활성화 여부 (선택)
    - **threshold**: 탐지 민감도 0-100 (선택)

    예시:
    - PERSON 타입 비활성화: `{"enabled": false}`
    - PHONE_NUM threshold 80%로 변경: `{"threshold": 80}`
    - 둘 다 변경: `{"enabled": true, "threshold": 75}`
    """
    try:
        logger.info(
            f"Admin {current_user.username} updating PII setting: {entity_type} - "
            f"enabled={update_data.enabled}, threshold={update_data.threshold}"
        )

        service = PIISettingsService(session)
        result = await service.update_setting(entity_type, update_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PII 타입 '{entity_type}'의 설정을 찾을 수 없습니다."
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update PII setting for {entity_type}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PII 설정 업데이트 중 오류가 발생했습니다."
        )