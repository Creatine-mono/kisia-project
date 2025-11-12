from app.ai.model_manager import get_pii_detector, get_policy_detector
from app.schemas.pii import PIIDetectionResponse, DetectedEntity
from app.services.pii_settings_service import PIISettingsService
from app.db.session import get_db  # get_session -> get_db로 변경
import logging

logger = logging.getLogger(__name__)


class PIIDetectionService:
    """PII 탐지 비즈니스 로직을 처리하는 서비스"""

    # 모델 라벨 → DB 라벨 매핑
    LABEL_MAPPING = {
        "NAME": "PERSON",
        "STREET_ADDRESS": "ADDRESS",
        "CREDIT_CARD_INFO": "CREDIT_CARD",
        "BANKING_NUMBER": "ACCOUNT",
        "ORGANIZATION_NAME": "ORG",
        # 나머지는 동일하게 매핑
        "PHONE_NUM": "PHONE_NUM",
        "EMAIL": "EMAIL",
        "ID_NUM": "ID_NUM",
        "DATE": "DATE",
        "USERNAME": "USERNAME",
        "URL_PERSONAL": "URL_PERSONAL",
        "DATE_OF_BIRTH": "DATE_OF_BIRTH",
        "AGE": "AGE",
        "PASSWORD": "PASSWORD",
        "SECURE_CREDENTIAL": "SECURE_CREDENTIAL",
    }

    def __init__(self):
        # 싱글톤 패턴으로 모델 인스턴스 재사용
        self.detector = None

    async def analyze_text(self, text: str) -> PIIDetectionResponse:
        """
        2단계 탐지를 수행하는 텍스트 분석

        1단계: NER 기반 PII 탐지 (설정 기반 필터링 포함)
        2단계: 정책 위반 맥락 탐지 (PII 없을 때만)
        """

        # ==================== 1단계: NER 기반 PII 탐지 ====================
        logger.info("Stage 1: NER-based PII detection")

        # 싱글톤 모델 인스턴스 가져오기
        pii_detector = get_pii_detector()

        # AI 모델로 PII 탐지
        detection_result = await pii_detector.detect_pii(text)

        # PII 설정 조회 (캐시 사용)
        settings_dict = await self._get_pii_settings()

        # 설정 기반 필터링
        filtered_entities = []
        for entity in detection_result["entities"]:
            model_type = entity["type"]

            # 모델 라벨 → DB 라벨 변환
            db_type = self.LABEL_MAPPING.get(model_type, model_type)

            logger.debug(f"Model type: {model_type} → DB type: {db_type}")

            # 해당 타입의 설정 확인 (DB 타입으로 조회)
            setting = settings_dict.get(db_type)

            # 설정이 없거나 비활성화된 경우 제외
            if not setting or not setting.get("enabled", True):
                logger.debug(f"Filtered out {model_type} (disabled)")
                continue

            # confidence를 퍼센트로 변환 (0.0~1.0 → 0~100)
            confidence_percent = entity["confidence"] * 100
            threshold = setting.get("threshold", 0)

            # threshold 미만인 경우 제외
            if confidence_percent < threshold:
                logger.debug(
                    f"Filtered out {model_type} '{entity['value']}' "
                    f"(confidence {confidence_percent:.1f}% < threshold {threshold}%)"
                )
                continue

            # 필터 통과 (원래 모델 타입 유지)
            filtered_entities.append(entity)

        # 필터링된 엔티티로 응답 구성
        entities = [
            DetectedEntity(
                type=entity["type"],
                value=entity["value"],
                confidence=entity["confidence"],
                token_count=entity["token_count"]
            )
            for entity in filtered_entities
        ]

        # has_pii는 필터링 후 결과 기준
        has_pii = len(entities) > 0

        # PII가 탐지된 경우 → 정책 검사 스킵하고 즉시 반환
        if has_pii:
            logger.info(f"PII detected: {len(entities)} entities. Skipping policy check.")
            reason = self._generate_reason(has_pii, entities, None, None)
            details = self._generate_details(has_pii, entities, None, None)

            return PIIDetectionResponse(
                has_pii=has_pii,
                reason=reason,
                details=details,
                entities=entities,
                policy_violation=False,
                policy_judgment=None,
                policy_confidence=None
            )

        # ==================== 2단계: 정책 위반 탐지 ====================
        logger.info("Stage 2: Policy violation detection (no PII found)")

        policy_detector = get_policy_detector()
        policy_result = await policy_detector.detect_violation(text)

        policy_judgment = policy_result["judgment"]
        policy_confidence = policy_result["confidence"]
        policy_violation = not policy_detector.is_safe(policy_judgment)

        logger.info(f"Policy judgment: {policy_judgment} (confidence: {policy_confidence:.2%})")

        # reason과 details 생성
        reason = self._generate_reason(has_pii, entities, policy_violation, policy_judgment)
        details = self._generate_details(has_pii, entities, policy_violation, policy_result)

        return PIIDetectionResponse(
            has_pii=has_pii,
            reason=reason,
            details=details,
            entities=entities,
            policy_violation=policy_violation,
            policy_judgment=policy_judgment,
            policy_confidence=policy_confidence
        )

    def _generate_reason(
        self,
        has_pii: bool,
        entities: list[DetectedEntity],
        policy_violation: bool | None,
        policy_judgment: str | None
    ) -> str:
        """탐지 결과에 대한 이유 생성"""
        # PII 탐지된 경우
        if has_pii:
            if len(entities) == 1:
                entity_type = entities[0].type
                return f"개인정보 1개 탐지됨 ({entity_type})"

            entity_types = list(set(entity.type for entity in entities))
            type_str = ", ".join(entity_types)
            return f"개인정보 {len(entities)}개 탐지됨 ({type_str})"

        # PII 없음 → 정책 검사 결과에 따라
        if policy_violation:
            return "정책 위반 탐지됨"

        # 모두 통과
        return "차단 사유 없음"

    def _generate_details(
        self,
        has_pii: bool,
        entities: list[DetectedEntity],
        policy_violation: bool | None,
        policy_result: dict | None
    ) -> str:
        """탐지된 정보에 대한 상세 설명 생성"""
        # PII 탐지된 경우
        if has_pii:
            details_parts = []
            for entity in entities:
                confidence_pct = f"{entity.confidence:.1%}"
                details_parts.append(f"{entity.type} '{entity.value}' (신뢰도: {confidence_pct})")

            details_str = ", ".join(details_parts)
            return f"다음 개인정보가 탐지되었습니다: {details_str}"

        # PII 없음 → 정책 검사 결과에 따라
        if policy_violation and policy_result:
            judgment = policy_result.get("judgment", "UNKNOWN")
            confidence = policy_result.get("confidence", 0.0)
            confidence_pct = f"{confidence:.1%}"
            return f"정책 위반 탐지됨 ({judgment}, 신뢰도: {confidence_pct})"

        # 모두 통과
        return "개인정보 및 정책 위반이 탐지되지 않았습니다"

    async def _get_pii_settings(self) -> dict[str, dict]:
        """
        PII 설정 조회 (캐시 활용)

        Returns:
            dict[entity_type, {"enabled": bool, "threshold": int}]
        """
        try:
            # DB 세션 가져오기 (get_session -> get_db로 변경)
            async for session in get_db():
                service = PIISettingsService(session)
                settings_dict = await service.get_settings_for_filtering()
                return settings_dict
        except Exception as e:
            logger.error(f"Failed to load PII settings, using defaults: {str(e)}")
            # 실패 시 모든 타입 활성화 (기본값)
            return {}