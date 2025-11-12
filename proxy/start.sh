#!/bin/bash

# ChatGPT 프록시 실행 스크립트
# mitmproxy의 기본 로그를 최소화하고 ChatGPT 통신만 표시

echo "🚀 ChatGPT 프록시 시작 중..."
echo "📡 포트: 8080"
echo "🎯 대상: ChatGPT/OpenAI 도메인만 모니터링"
echo "🔒 기능: 한국어 개인정보(PII) 탐지 및 차단"
echo "🔧 모드: PII 탐지 프록시 (스트리밍 비활성화)"
echo "─────────────────────────────────────────────────"

# mitmproxy 실행 (안정적인 설정)
# uv를 통해 설치된 패키지 실행
uv run mitmdump \
  --listen-host 0.0.0.0 \
  --set termlog_verbosity=warn \
  --set connection_strategy=lazy \
  --set keep_host_header=true \
  --set upstream_cert=false \
  --ssl-insecure \
  -p 8080 \
  -s proxy.py \
  --quiet