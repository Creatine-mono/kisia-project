#!/usr/bin/env python3
"""
프록시 실행 스크립트
mitmproxy의 기본 로그를 끄고 ChatGPT 통신만 표시
"""
import os
import sys
from mitmproxy.tools.main import mitmdump

def main():
    """프록시 실행"""
    
    # mitmproxy 로그 레벨을 error로 설정 (기본 정보 로그 끄기)
    os.environ["MITMPROXY_LOG_LEVEL"] = "error"
    
    # 프록시 실행 인자 (안정성 우선)
    args = [
        # 로그 레벨을 error로 설정 (warn, error만 출력)
        "--set", "termlog_verbosity=error",
        
        # 연결 안정성 개선
        "--set", "connection_strategy=lazy",
        "--set", "keep_host_header=true",
        
        # 프록시 스크립트 지정
        "-s", "proxy.py",
        
        # 포트 설정 (기본 8080)
        "-p", "8080",
        
        # SSL 인증서 무시 (개발용)
        "--ssl-insecure",
        
        # 호스트 해석 건너뛰기
        "--set", "confdir=~/.mitmproxy",
    ]
    
    # 디버그 모드인 경우 더 자세한 로그
    if os.getenv("PROXY_DEBUG", "0") == "1":
        args[1] = "termlog_verbosity=info"
    
    print("🚀 ChatGPT 프록시 시작 중...")
    print(f"📡 포트: 8080")
    print(f"🎯 대상: ChatGPT/OpenAI 도메인")
    print(f"🔒 기능: 한국어 개인정보(PII) 탐지 및 차단")
    print(f"🔧 모드: PII 탐지 프록시 (스트리밍 비활성화)")
    print("─" * 50)
    
    try:
        # mitmdump 실행
        sys.argv = ["mitmdump"] + args
        mitmdump()
    except KeyboardInterrupt:
        print("\n🛑 프록시 종료됨")
    except Exception as e:
        print(f"❌ 프록시 실행 오류: {e}")

if __name__ == "__main__":
    main()