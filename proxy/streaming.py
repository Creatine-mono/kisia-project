"""
스트리밍 응답 처리 모듈
ChatGPT의 실시간 스트리밍 응답을 버퍼링 없이 전달
"""
import time
from typing import Optional
from mitmproxy import http

from logger import logger


class StreamingHandler:
    """스트리밍 응답을 처리하는 클래스"""

    @staticmethod
    def is_streaming_response(flow: http.HTTPFlow) -> bool:
        """스트리밍 응답인지 확인"""
        if not flow.response:
            return False
            
        content_type = flow.response.headers.get("content-type", "").lower()
        
        # Server-Sent Events 확인
        if "text/event-stream" in content_type:
            return True
            
        # Transfer-Encoding: chunked 확인
        transfer_encoding = flow.response.headers.get("transfer-encoding", "").lower()
        if "chunked" in transfer_encoding:
            return True
            
        return False

    @staticmethod
    def setup_streaming_headers(flow: http.HTTPFlow):
        """스트리밍에 필요한 헤더 설정"""
        if not flow.response:
            return
            
        # 스트리밍 최적화 헤더
        flow.response.headers["Cache-Control"] = "no-cache, no-transform"
        flow.response.headers["X-Accel-Buffering"] = "no"
        flow.response.headers["Connection"] = "keep-alive"
        
        # CORS 헤더 (필요한 경우)
        if "origin" in flow.request.headers:
            flow.response.headers["Access-Control-Allow-Origin"] = "*"
            flow.response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            flow.response.headers["Access-Control-Allow-Headers"] = "*"

    @staticmethod
    def enable_response_streaming(flow: http.HTTPFlow):
        """응답 스트리밍 활성화 (보수적 접근)"""
        if not flow.response:
            return
            
        try:
            # 스트리밍 헤더만 설정 (stream = True는 제거)
            StreamingHandler.setup_streaming_headers(flow)
            
            logger.debug(f"Enabled streaming headers for {flow.request.host}{flow.request.path}")
            
        except Exception as e:
            logger.warn(f"Failed to enable streaming: {e}")

    @staticmethod
    def should_stream_request(flow: http.HTTPFlow) -> bool:
        """요청이 스트리밍 처리가 필요한지 확인 (엄격한 조건)"""
        
        # Accept 헤더에서 명시적으로 text/event-stream 요청하는 경우만
        accept = flow.request.headers.get("Accept", "").lower()
        if "text/event-stream" in accept:
            return True
            
        return False

    @staticmethod
    def optimize_for_streaming():
        """스트리밍 최적화를 위한 전역 설정"""
        # 이 메서드는 프록시 시작 시 호출
        logger.info("Streaming optimization enabled")


class ResponseBuffer:
    """스트리밍 응답을 위한 버퍼 관리"""
    
    def __init__(self):
        self.buffers = {}  # flow_id -> buffer
    
    def should_buffer(self, flow: http.HTTPFlow) -> bool:
        """응답을 버퍼링해야 하는지 확인"""
        # 차단된 요청은 버퍼링 필요 (즉시 응답)
        if hasattr(flow, 'metadata') and flow.metadata.get('should_block'):
            return True
            
        # 일반 스트리밍 응답은 버퍼링 안함
        return False
    
    def add_to_buffer(self, flow_id: str, data: bytes):
        """버퍼에 데이터 추가"""
        if flow_id not in self.buffers:
            self.buffers[flow_id] = b""
        self.buffers[flow_id] += data
    
    def get_buffer(self, flow_id: str) -> bytes:
        """버퍼 데이터 반환"""
        return self.buffers.get(flow_id, b"")
    
    def clear_buffer(self, flow_id: str):
        """버퍼 정리"""
        self.buffers.pop(flow_id, None)


# 전역 버퍼 인스턴스
response_buffer = ResponseBuffer()