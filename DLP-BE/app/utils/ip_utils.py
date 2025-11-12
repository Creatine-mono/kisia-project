"""
IP 주소 추출 유틸리티
"""
from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    요청에서 클라이언트 IP 주소 추출

    우선순위:
    1. X-Forwarded-For 헤더 (프록시 환경)
    2. X-Real-IP 헤더 (Nginx 등)
    3. request.client.host (직접 연결)

    Args:
        request: FastAPI Request 객체

    Returns:
        str: 클라이언트 IP 주소
    """
    # X-Forwarded-For 헤더 확인 (가장 우선)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For는 여러 IP를 포함할 수 있음 (예: "client, proxy1, proxy2")
        # 첫 번째 IP가 원본 클라이언트 IP
        return forwarded_for.split(",")[0].strip()

    # X-Real-IP 헤더 확인 (두 번째 우선순위)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # 직접 연결된 클라이언트 IP (최종 대체)
    if request.client:
        return request.client.host

    # 모든 방법 실패 시 기본값
    return "unknown"