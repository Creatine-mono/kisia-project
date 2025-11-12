#!/bin/bash
set -e

echo "=== mitmproxy 인증서 설정 시작 ==="

# 인증서 디렉토리 생성
mkdir -p /app/certs
mkdir -p /app/.mitmproxy

# mitmproxy 환경 변수 설정
export MITMPROXY_CONFDIR="/app/.mitmproxy"

echo "mitmproxy 초기 실행으로 CA 인증서 생성..."

# mitmproxy를 백그라운드에서 짧게 실행하여 인증서 생성
timeout 5s mitmdump --listen-port 8081 --set confdir=/app/.mitmproxy || true

# 인증서 파일 확인 및 복사
if [ -f "/app/.mitmproxy/mitmproxy-ca-cert.pem" ]; then
    cp /app/.mitmproxy/mitmproxy-ca-cert.pem /app/certs/
    cp /app/.mitmproxy/mitmproxy-ca-cert.p12 /app/certs/ 2>/dev/null || true
    cp /app/.mitmproxy/mitmproxy-ca-cert.cer /app/certs/ 2>/dev/null || true
    
    echo "✅ CA 인증서가 생성되었습니다:"
    ls -la /app/certs/
    
    echo ""
    echo "=== 클라이언트 설정 안내 ==="
    echo "1. 다음 명령으로 인증서 다운로드:"
    echo "   docker cp 컨테이너명:/app/certs/mitmproxy-ca-cert.pem ."
    echo ""
    echo "2. 각 OS별 인증서 설치:"
    echo "   - Windows: 인증서 파일 더블클릭 → 신뢰할 수 있는 루트 인증 기관"
    echo "   - macOS: 키체인 접근에서 인증서 추가 → 항상 신뢰"
    echo "   - Linux: /usr/local/share/ca-certificates/ 복사 후 update-ca-certificates"
    echo ""
    echo "3. 브라우저 프록시 설정: 127.0.0.1:8080"
    echo "=========================="
    
else
    echo "❌ 인증서 생성에 실패했습니다."
    exit 1
fi

echo "=== 인증서 설정 완료 ==="