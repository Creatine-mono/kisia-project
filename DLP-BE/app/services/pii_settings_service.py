"""
PII Settings Service - 비즈니스 로직 및 캐싱
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.pii_settings_repo import PIISettingsRepository
from app.schemas.pii_settings import (
    PIISettingResponse,
    PIISettingUpdate,
    PIISettingsListResponse
)
from app.models.pii_settings import PIISettings
import logging

logger = logging.getLogger(__name__)


class PIISettingsService:
    """PII 설정 서비스 - 캐싱 및 비즈니스 로직 처리"""

    # 인메모리 캐시 (클래스 변수)
    _cache: dict[str, PIISettings] | None = None

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PIISettingsRepository(session)

    async def get_all_settings(self, use_cache: bool = True) -> PIISettingsListResponse:
        """
        모든 PII 설정 조회

        Args:
            use_cache: 캐시 사용 여부 (기본: True)
        """
        if use_cache and PIISettingsService._cache is not None:
            settings_list = list(PIISettingsService._cache.values())
        else:
            settings_list = await self.repo.get_all()
            # 캐시 갱신
            PIISettingsService._cache = {s.entity_type: s for s in settings_list}

        settings_response = [
            PIISettingResponse.model_validate(setting)
            for setting in settings_list
        ]

        return PIISettingsListResponse(
            settings=settings_response,
            total=len(settings_response)
        )

    async def get_setting(self, entity_type: str) -> PIISettingResponse | None:
        """특정 엔티티 타입의 설정 조회"""
        # 캐시 확인
        if PIISettingsService._cache is not None:
            setting = PIISettingsService._cache.get(entity_type)
            if setting:
                return PIISettingResponse.model_validate(setting)

        # 캐시 미스 시 DB 조회
        setting = await self.repo.get_by_entity_type(entity_type)
        if setting:
            return PIISettingResponse.model_validate(setting)

        return None

    async def update_setting(
        self,
        entity_type: str,
        update_data: PIISettingUpdate
    ) -> PIISettingResponse | None:
        """PII 설정 업데이트"""
        updated_setting = await self.repo.update_setting(
            entity_type=entity_type,
            enabled=update_data.enabled,
            threshold=update_data.threshold
        )

        if updated_setting:
            # 캐시 갱신
            if PIISettingsService._cache is not None:
                PIISettingsService._cache[entity_type] = updated_setting
            else:
                # 캐시가 없으면 전체 재로딩
                await self._reload_cache()

            logger.info(f"Updated PII setting: {entity_type} - enabled={update_data.enabled}, threshold={update_data.threshold}")
            return PIISettingResponse.model_validate(updated_setting)

        return None

    async def get_settings_for_filtering(self) -> dict[str, dict]:
        """
        PII 필터링용 설정 딕셔너리 조회

        Returns:
            dict[entity_type, {"enabled": bool, "threshold": int}]
        """
        # 캐시 확인
        if PIISettingsService._cache is None:
            await self._reload_cache()

        if PIISettingsService._cache is None:
            logger.warning("PII settings cache is empty")
            return {}

        # 필터링에 필요한 정보만 추출
        return {
            entity_type: {
                "enabled": setting.enabled,
                "threshold": setting.threshold
            }
            for entity_type, setting in PIISettingsService._cache.items()
        }

    async def _reload_cache(self):
        """캐시 전체 재로딩"""
        settings = await self.repo.get_all()
        PIISettingsService._cache = {s.entity_type: s for s in settings}
        logger.info(f"Reloaded PII settings cache: {len(settings)} settings")

    @classmethod
    def clear_cache(cls):
        """캐시 초기화 (테스트용)"""
        cls._cache = None
        logger.info("Cleared PII settings cache")

    @classmethod
    async def initialize_cache(cls, session: AsyncSession):
        """
        애플리케이션 시작 시 캐시 초기화

        Args:
            session: DB 세션
        """
        service = cls(session)
        await service._reload_cache()
        logger.info("Initialized PII settings cache")