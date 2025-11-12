"""
로깅 관리 모듈
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from glob import glob
from mitmproxy import ctx

from config import DEBUG, LOG_DIR, LOG_BASE, LOG_MAX, LOG_ROTATE, LOG_KEEP_LATEST


class ProxyLogger:
    """프록시 로깅을 관리하는 클래스"""

    def __init__(self):
        self.log_dir = LOG_DIR
        self.log_base = LOG_BASE
        self.log_max = LOG_MAX
        self.rotate = LOG_ROTATE
        self.keep_latest = LOG_KEEP_LATEST

    def info(self, message: str):
        """정보 로그"""
        if DEBUG:
            ctx.log.info(message)

    def warn(self, message: str):
        """경고 로그"""
        ctx.log.warn(message)

    def error(self, message: str):
        """에러 로그"""
        ctx.log.error(message)

    def debug(self, message: str):
        """디버그 로그"""
        if DEBUG:
            ctx.log.info(f"[DEBUG] {message}")

    def log_request(self, prompt: str, files_count: int, client_ip: str, 
                   host: str, should_block: bool, reason: str, details=None):
        """사용자 요청 로그 저장 (일자별 통합 파일)"""
        try:
            # 로그 데이터 구성
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "epoch": datetime.utcnow().timestamp(),
                "client_ip": client_ip,
                "host": host,
                "prompt": prompt[:1000] if prompt else "",  # 로그에는 일부만
                "files_count": files_count,
                "should_block": should_block,
                "reason": reason,
                "status": "blocked" if should_block else "allowed",
                "details": details
            }

            # 일자별 로그 파일명 생성
            today = datetime.utcnow().strftime("%Y-%m-%d")
            log_path = self.log_dir / f"{self.log_base}_{today}.jsonl"

            # JSONL 형식으로 추가 (JSON Lines)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            self.debug(f"Log appended to {log_path.name}")

        except Exception as e:
            self.error(f"Failed to save log: {e}")

    def log_blocked_request(self, prompt: str, files_count: int, client_ip: str,
                           host: str, reason: str, details=None):
        """차단된 요청 로그를 별도로 저장 (일자별 통합)"""
        try:
            block_log_dir = self.log_dir / "blocked"
            block_log_dir.mkdir(parents=True, exist_ok=True)

            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "epoch": datetime.utcnow().timestamp(),
                "client_ip": client_ip,
                "host": host,
                "prompt": prompt[:500] if prompt else "",  # 차단된 내용은 더 짧게
                "files_count": files_count,
                "reason": reason,
                "details": details
            }

            # 일자별 차단 로그 파일명 생성
            today = datetime.utcnow().strftime("%Y-%m-%d")
            log_path = block_log_dir / f"blocked_{today}.jsonl"

            # JSONL 형식으로 추가
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            self.debug(f"Block log appended to {log_path.name}")

        except Exception as e:
            self.error(f"Failed to save block log: {e}")

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """오래된 일자별 로그 파일 정리"""
        try:
            import time
            cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
            
            # 일반 로그 정리
            for log_file in self.log_dir.glob(f"{self.log_base}_*.jsonl"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.debug(f"Deleted old log: {log_file.name}")
            
            # 차단 로그 정리
            block_log_dir = self.log_dir / "blocked"
            if block_log_dir.exists():
                for log_file in block_log_dir.glob("blocked_*.jsonl"):
                    if log_file.stat().st_mtime < cutoff_time:
                        log_file.unlink()
                        self.debug(f"Deleted old block log: {log_file.name}")
                        
        except Exception as e:
            self.warn(f"Failed to cleanup old logs: {e}")


# 싱글톤 인스턴스
logger = ProxyLogger()