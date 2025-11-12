#!/usr/bin/env python3
"""
mitmproxy SSL 인증서 초기화 스크립트
기업용 HTTPS 트래픽 검사를 위한 CA 인증서 생성
"""

import os
import sys
import subprocess
from pathlib import Path


def ensure_cert_dir():
    """인증서 디렉토리 생성"""
    cert_dir = Path("/app/certs")
    cert_dir.mkdir(parents=True, exist_ok=True)
    return cert_dir


def generate_mitmproxy_certs():
    """mitmproxy CA 인증서 생성"""
    cert_dir = ensure_cert_dir()
    
    # mitmproxy 설정 디렉토리
    mitmproxy_dir = Path("/app/.mitmproxy")
    mitmproxy_dir.mkdir(parents=True, exist_ok=True)
    
    print("mitmproxy CA 인증서 생성 중...")
    
    # mitmproxy를 한 번 실행하여 CA 인증서 생성
    try:
        # mitmproxy 실행하여 인증서 생성 (즉시 종료)
        result = subprocess.run([
            "mitmdump", "--version"
        ], capture_output=True, text=True, timeout=10)
        
        # 실제 인증서 생성을 위해 짧은 실행
        process = subprocess.Popen([
            "mitmdump", 
            "--listen-port", "8081",
            "--set", f"confdir={mitmproxy_dir}"
        ])
        
        # 2초 후 종료 (인증서 생성을 위한 시간)
        import time
        time.sleep(2)
        process.terminate()
        process.wait()
        
    except Exception as e:
        print(f"인증서 생성 중 오류: {e}")
    
    # 생성된 인증서 복사
    ca_cert_src = mitmproxy_dir / "mitmproxy-ca-cert.pem"
    ca_cert_dst = cert_dir / "mitmproxy-ca-cert.pem"
    
    if ca_cert_src.exists():
        import shutil
        shutil.copy2(ca_cert_src, ca_cert_dst)
        print(f"CA 인증서가 생성되었습니다: {ca_cert_dst}")
        
        # 인증서 정보 출력
        print("\n=== 클라이언트 설치 안내 ===")
        print(f"1. 다음 파일을 클라이언트에 다운로드: {ca_cert_dst}")
        print("2. 브라우저/OS 신뢰할 수 있는 루트 인증 기관에 추가")
        print("3. 프록시 설정: 127.0.0.1:8080")
        print("===============================\n")
        
        return True
    else:
        print("인증서 생성에 실패했습니다.")
        return False


def main():
    """메인 함수"""
    print("=== mitmproxy 인증서 초기화 시작 ===")
    
    if generate_mitmproxy_certs():
        print("인증서 초기화 완료!")
        return 0
    else:
        print("인증서 초기화 실패!")
        return 1


if __name__ == "__main__":
    sys.exit(main())