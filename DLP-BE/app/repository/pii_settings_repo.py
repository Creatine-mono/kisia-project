"""
PII Settings Repository
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.pii_settings import PIISettings


class PIISettingsRepository:
    """PII 설정 데이터 접근 레이어"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[PIISettings]:
        """모든 PII 설정 조회"""
        result = await self.session.execute(
            select(PIISettings).order_by(PIISettings.entity_type)
        )
        return list(result.scalars().all())

    async def get_by_entity_type(self, entity_type: str) -> PIISettings | None:
        """특정 엔티티 타입의 설정 조회"""
        result = await self.session.execute(
            select(PIISettings).where(PIISettings.entity_type == entity_type)
        )
        return result.scalar_one_or_none()

    async def update_setting(
        self,
        entity_type: str,
        enabled: bool | None = None,
        threshold: int | None = None
    ) -> PIISettings | None:
        """PII 설정 업데이트"""
        # 기존 설정 확인
        setting = await self.get_by_entity_type(entity_type)
        if not setting:
            return None

        # 업데이트할 필드 준비
        update_data = {}
        if enabled is not None:
            update_data["enabled"] = enabled
        if threshold is not None:
            update_data["threshold"] = threshold

        if not update_data:
            return setting

        # 업데이트 실행
        await self.session.execute(
            update(PIISettings)
            .where(PIISettings.entity_type == entity_type)
            .values(**update_data)
        )
        await self.session.commit()

        # 업데이트된 설정 조회 및 반환
        await self.session.refresh(setting)
        return setting

    async def get_enabled_types(self) -> list[str]:
        """활성화된 PII 타입 목록 조회"""
        result = await self.session.execute(
            select(PIISettings.entity_type).where(PIISettings.enabled == True)
        )
        return list(result.scalars().all())

    async def get_settings_dict(self) -> dict[str, PIISettings]:
        """
        PII 설정을 딕셔너리로 조회 (빠른 검색용)

        Returns:
            dict[entity_type, PIISettings]
        """
        settings = await self.get_all()
        return {setting.entity_type: setting for setting in settings}
