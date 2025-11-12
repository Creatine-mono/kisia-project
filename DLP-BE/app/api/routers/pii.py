from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from app.schemas.pii import PIIDetectionRequest, PIIDetectionResponse
from app.services.pii_service import PIIDetectionService
from app.services.log_service import PIILogService
from app.ai.model_manager import get_pii_detector
from app.utils.ip_utils import get_client_ip
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter()

# 서비스 인스턴스 생성 (이제 모델은 싱글톤으로 관리됨)
pii_service = PIIDetectionService()
log_service = PIILogService()

@router.post("/detect",
             response_model=PIIDetectionResponse,
             summary="PII 탐지 (프록시용, 인증 불필요)",
             description="입력된 텍스트에서 개인정보를 탐지하고 결과를 반환합니다. 프록시 서버에서 호출합니다.",
             status_code=status.HTTP_200_OK)
async def detect_pii(
    pii_request: PIIDetectionRequest,
    request: Request
) -> PIIDetectionResponse:
    """
    텍스트에서 개인정보 탐지 API (프록시용, 인증 불필요)

    - **text**: 분석할 텍스트 (1-10,000자)

    반환값:
    - **has_pii**: 개인정보 탐지 여부 (boolean)
    - **reason**: 탐지 결과 이유
    - **details**: 구체적인 탐지 내용
    - **entities**: 탐지된 개인정보 엔티티 목록
    """
    start_time = time.time()
    client_ip = get_client_ip(request)

    try:
        # 입력 검증
        if not pii_request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="입력 텍스트가 비어있습니다."
            )

        # PII 탐지 수행
        text = pii_request.text.strip()
        logger.info(f"PII detection started from IP: {client_ip}, text length: {len(text)}")

        result = await pii_service.analyze_text(text)

        # 응답 시간 계산
        response_time_ms = (time.time() - start_time) * 1000

        logger.info(
            f"PII detection completed. IP: {client_ip}, has_pii: {result.has_pii}, "
            f"entities: {len(result.entities)}, response_time: {response_time_ms:.2f}ms"
        )

        # 로그 저장 (비동기, 빠름)
        try:
            await log_service.log_detection(
                client_ip=client_ip,
                original_text=text,
                result=result,
                response_time_ms=response_time_ms
            )
        except Exception as log_error:
            # 로깅 실패해도 메인 요청은 성공 처리
            logger.warning(f"Failed to log detection result: {str(log_error)}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PII detection failed from IP {client_ip}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PII 탐지 중 오류가 발생했습니다."
        )

@router.get("/health",
            summary="PII 탐지 서비스 상태 확인",
            description="PII 탐지 모델이 정상적으로 로드되었는지 확인합니다. 인증 불필요.")
async def health_check():
    """PII 탐지 서비스 헬스체크 (인증 불필요)"""
    try:
        # 모델 인스턴스 상태 확인 (실제 추론 없이 빠른 체크)
        detector = get_pii_detector()
        model_loaded = detector.model is not None and detector.tokenizer is not None

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "message": "PII detection service is running",
                "model_loaded": model_loaded,
                "model_name": detector.model_name
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "message": "PII detection service is not available",
                "model_loaded": False,
                "error": str(e)
            }
        )