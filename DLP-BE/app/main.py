# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.pii import router as pii_router
from app.api.routers.auth import router as auth_router
from app.api.routers.admin import router as admin_router
from app.api.routers.pii_settings import router as pii_settings_router
from app.ai.model_manager import preload_models, cleanup_models
from app.core.elasticsearch import ElasticsearchClient
from app.repository.elasticsearch_repo import ElasticsearchRepository
from app.services.pii_settings_service import PIISettingsService
from app.db.session import get_db  # get_session -> get_db로 변경
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-TLS-DLP Backend",
    description="AI 기반 개인정보 탐지 API (인증 필수)",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 추가 (개발환경용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*","http://localhost:3000",
          "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 추가
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])  # 인증 API (인증 불필요)
app.include_router(pii_router, prefix="/api/v1/pii", tags=["PII Detection"])  # PII API (인증 불필요, 프록시용)
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin Dashboard"])  # 관리자 API (인증 필수)
app.include_router(pii_settings_router, prefix="/api/v1/admin/pii-settings", tags=["PII Settings"])  # PII 설정 API (인증 필수)

# 애플리케이션 시작/종료 이벤트 핸들러
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("Starting AI-TLS-DLP Backend...")

    # AI 모델 사전 로딩
    preload_models()
    logger.info("AI models loaded successfully")

    # Elasticsearch 클라이언트 초기화 및 인덱스 생성
    try:
        es_client = await ElasticsearchClient.get_client()
        repo = ElasticsearchRepository(es_client)
        await repo.create_index_if_not_exists()
        logger.info("Elasticsearch initialized successfully")

        # ES 헬스 체크
        health = await ElasticsearchClient.health_check()
        logger.info(f"Elasticsearch health: {health}")
    except Exception as e:
        logger.warning(f"Elasticsearch initialization failed: {str(e)}")
        logger.warning("Application will continue without logging functionality")

    # PII 설정 캐시 초기화 (get_session -> get_db로 변경)
    try:
        async for session in get_db():
            await PIISettingsService.initialize_cache(session)
            logger.info("PII settings cache initialized successfully")
            break
    except Exception as e:
        logger.warning(f"PII settings cache initialization failed: {str(e)}")
        logger.warning("Application will use default PII detection settings")

    logger.info("AI-TLS-DLP Backend startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("Shutting down AI-TLS-DLP Backend...")

    # AI 모델 메모리 정리
    cleanup_models()
    logger.info("AI models cleaned up")

    # Elasticsearch 클라이언트 종료
    try:
        await ElasticsearchClient.close_client()
        logger.info("Elasticsearch client closed")
    except Exception as e:
        logger.warning(f"Elasticsearch cleanup warning: {str(e)}")

    logger.info("AI-TLS-DLP Backend shutdown completed")

@app.get("/", summary="API 상태 확인")
async def root():
    """루트 엔드포인트 - API 상태 확인"""
    return {
        "message": "AI-TLS-DLP Backend API is running",
        "description": "PII Detection & Logging System with Admin Dashboard",
        "status": "ok",
        "version": "1.2.0",
        "features": [
            "Korean PII Detection (RoBERTa + Regex)",
            "IP-based Request Logging (Elasticsearch)",
            "Admin Dashboard & Statistics",
            "JWT Authentication (Admin only)",
            "PII Detection Settings (Enable/Disable & Threshold)"
        ],
        "endpoints": {
            "docs": "/docs",
            "auth": {
                "register": "/api/v1/auth/register",
                "login": "/api/v1/auth/login",
                "me": "/api/v1/auth/me"
            },
            "pii_detection": {
                "detect": "/api/v1/pii/detect (프록시용, 인증 불필요)",
                "health": "/api/v1/pii/health"
            },
            "admin_dashboard": {
                "logs": "/api/v1/admin/logs (인증 필수)",
                "statistics_overview": "/api/v1/admin/statistics/overview",
                "statistics_timeline": "/api/v1/admin/statistics/timeline",
                "statistics_by_pii_type": "/api/v1/admin/statistics/by-pii-type",
                "statistics_by_ip": "/api/v1/admin/statistics/by-ip"
            },
            "pii_settings": {
                "get_all": "/api/v1/admin/pii-settings (인증 필수)",
                "get_specific": "/api/v1/admin/pii-settings/{entity_type} (인증 필수)",
                "update": "/api/v1/admin/pii-settings/{entity_type} (PATCH, 인증 필수)"
            }
        },
        "notes": [
            "PII Detection API는 인증 불필요 (프록시 서버용)",
            "Admin API는 JWT 인증 필수",
            "로그는 Elasticsearch에 저장 (30일 보관)"
        ]
    }