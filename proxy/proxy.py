"""
메인 프록시 애드온
"""
from typing import Dict, Any, List
from datetime import datetime
from mitmproxy import http

from config import TARGET_HOSTS, BLOCK_MESSAGE, DEBUG
from logger import logger
from backend import backend_client
from extractor import DataExtractor
from response import ResponseGenerator
from streaming import StreamingHandler


class SemanticProxy:
    """민감정보 차단 프록시 애드온"""

    def __init__(self):
        self.extractor = DataExtractor()
        self.backend = backend_client
        self.response_gen = ResponseGenerator()

        # 초기화 시 백엔드 헬스 체크
        if self.backend.health_check():
            print("🟢 프록시 시작됨 - PII 탐지 백엔드 연결 정상")
        else:
            print("🟡 프록시 시작됨 - PII 탐지 백엔드 연결 실패 (기본 차단 모드)")
        
        # 오래된 로그 정리 (30일 초과)
        logger.cleanup_old_logs(30)
        
        # 스트리밍 기능 비활성화 (안정성 우선)
        # StreamingHandler.optimize_for_streaming()

    def request(self, flow: http.HTTPFlow):
        """
        HTTP 요청 처리

        Args:
            flow: mitmproxy HTTP 플로우
        """
        # 대상 호스트 확인
        host = (flow.request.host or "").lower()
        if not TARGET_HOSTS.search(host):
            return

        # 요청 타입 확인
        if self.extractor.is_upload_request(flow):
            # 업로드 요청 처리 (차단하지 않음)
            self._handle_upload(flow)
            return

        if not self.extractor.is_stream_request(flow):
            # 스트림 요청이 아니면 통과
            return

        # 스트림 요청 처리
        self._handle_stream_request(flow)

    def _handle_stream_request(self, flow: http.HTTPFlow):
        """스트림 요청 처리 (대화 요청)"""

        # 요청 디코딩
        try:
            flow.request.decode()
        except Exception as e:
            logger.debug(f"Failed to decode request: {e}")

        # 데이터 추출
        extracted_data = self._extract_request_data(flow)

        # 추출된 데이터가 없으면 통과 (백그라운드 통신)
        if not extracted_data["prompt"] and not extracted_data["files"]:
            return

        # 실제 사용자 입력이 있는 경우만 출력
        print(f"\n💬 [대화 요청] {flow.request.host}")
        
        # 사용자 입력값 출력
        if extracted_data["prompt"]:
            print(f"📝 [사용자 입력] {extracted_data['prompt'][:200]}{'...' if len(extracted_data['prompt']) > 200 else ''}")
        
        if extracted_data["files"]:
            for file_info in extracted_data["files"]:
                print(f"📎 [파일] {file_info.get('filename', 'unknown')} ({file_info.get('content_type', 'unknown')})")
                if file_info.get('text'):
                    print(f"  내용: {file_info['text'][:100]}{'...' if len(file_info.get('text', '')) > 100 else ''}")

        # 백엔드에 종합 분석 요청 (PII + 유사 문서)
        print(f"🔍 [검사 시작] 텍스트 길이: {len(extracted_data['prompt'])}, 파일: {len(extracted_data['files'])}개")
        should_block, reason, details = self.backend.comprehensive_analysis(
            prompt=extracted_data["prompt"],
            files_data=extracted_data["files"],
            metadata=extracted_data["metadata"],
            client_ip=extracted_data["metadata"]["client_ip"]
        )
        print(f"🔍 [검사 완료] 차단: {should_block}, 사유: {reason}")

        # 로그 저장 (logger에서 모든 로그 처리)
        logger.log_request(
            prompt=extracted_data["prompt"],
            files_count=len(extracted_data["files"]),
            client_ip=extracted_data["metadata"]["client_ip"],
            host=flow.request.host,
            should_block=should_block,
            reason=reason,
            details=details
        )

        # 차단 여부 결정
        if should_block:
            print(f"🚫 [차단됨] {reason}")
            if details and "message" in details:
                print(f"   메시지: {details['message']}")

            # 차단 로그 별도 저장
            logger.log_blocked_request(
                prompt=extracted_data["prompt"],
                files_count=len(extracted_data["files"]),
                client_ip=extracted_data["metadata"]["client_ip"],
                host=flow.request.host,
                reason=reason,
                details=details
            )

            # 차단 응답 생성
            block_message = BLOCK_MESSAGE
            if details and "message" in details:
                block_message = details["message"]

            flow.response = self.response_gen.create_sse_block_response(
                flow=flow,
                message=block_message,
                parent_info=extracted_data.get("parent_info"),
                details=details,
                user_prompt=extracted_data["prompt"]
            )
        else:
            print(f"✅ [통과] {reason}")
            # 통과한 경우 정상적인 브라우저 헤더 추가하여 Cloudflare 우회
            self._add_browser_headers(flow)
            # flow.response가 None이면 원본 요청이 GPT API로 전달됨

    def _handle_upload(self, flow: http.HTTPFlow):
        """업로드 요청 처리"""

        # 요청 디코딩
        try:
            flow.request.decode()
        except Exception:
            pass

        content_type = flow.request.headers.get("content-type", "").lower()

        # 멀티파트 업로드
        if "multipart/form-data" in content_type:
            files = self.extractor.parse_multipart(
                flow.request.raw_content or b"",
                content_type
            )

            # 각 파일을 백엔드로 전송
            for file_info in files:
                self.backend.process_file(
                    file_bytes=file_info["data"],
                    filename=file_info["filename"],
                    content_type=file_info["content_type"]
                )
                print(f"[파일 처리] {file_info['filename']} ({len(file_info['data'])} bytes)")

            print(f"[완료] {len(files)}개 파일 처리됨")

        # 바이너리 업로드
        else:
            raw_data = flow.request.raw_content or b""
            if raw_data:
                filename = self.extractor.guess_filename(flow)

                # 백엔드로 파일 전송
                self.backend.process_file(
                    file_bytes=raw_data,
                    filename=filename,
                    content_type=content_type
                )

                print(f"[바이너리 처리] {filename} ({len(raw_data)} bytes)")

    def _extract_request_data(self, flow: http.HTTPFlow) -> Dict[str, Any]:
        """요청에서 모든 데이터 추출 (파일은 백엔드로 전송)"""

        content_type = flow.request.headers.get("content-type", "").lower()
        body = flow.request.get_text(strict=False) or ""

        # 결과 초기화
        result = {
            "prompt": "",
            "files": [],
            "metadata": {
                "client_ip": self.extractor.get_client_ip(flow),
                "path": flow.request.path,
                "host": flow.request.host,
                "timestamp": datetime.utcnow().isoformat(),
                "headers": dict(flow.request.headers)
            },
            "parent_info": None
        }

        # JSON 요청 처리
        if "application/json" in content_type:
            # 프롬프트 추출
            result["prompt"] = self.extractor.extract_prompt_from_json(body)

            # Base64로 인코딩된 파일들 추출
            embedded_files = self.extractor.extract_base64_images(body)
            for file_data in embedded_files:
                # 파일 원본 바이트를 백엔드로 전송
                # 백엔드에서 PDF 파싱, OCR, 텍스트 추출 등 모든 처리 수행
                processed = self.backend.process_file(
                    file_bytes=file_data["data"],
                    filename=file_data["filename"],
                    content_type=file_data["content_type"]
                )
                result["files"].append(processed)

            # CDN URL 추출 (백엔드에서 다운로드 및 처리 가능)
            cdn_urls = self.extractor.extract_cdn_urls(body)
            if cdn_urls:
                result["metadata"]["cdn_urls"] = cdn_urls

            # 부모 정보 추출
            result["parent_info"] = self.extractor.extract_parent_info(flow)

        # 멀티파트 요청 처리
        elif "multipart/form-data" in content_type:
            files = self.extractor.parse_multipart(
                flow.request.raw_content or b"",
                content_type
            )

            for file_info in files:
                # 파일 원본 바이트를 백엔드로 전송
                # PDF, 이미지, 문서 등 모든 파일 타입의 처리는 백엔드에서 수행
                processed = self.backend.process_file(
                    file_bytes=file_info["data"],
                    filename=file_info["filename"],
                    content_type=file_info["content_type"]
                )
                result["files"].append(processed)

        # 일반 텍스트/폼 요청
        elif "text/" in content_type or "application/x-www-form-urlencoded" in content_type:
            result["prompt"] = body.strip()

        return result

    def _add_browser_headers(self, flow: http.HTTPFlow):
        """정상적인 브라우저 헤더를 추가하여 Cloudflare 우회"""
        
        # User-Agent가 없거나 의심스러운 경우 정상적인 브라우저 User-Agent 설정
        current_ua = flow.request.headers.get("User-Agent", "")
        if not current_ua or "python" in current_ua.lower() or "requests" in current_ua.lower():
            flow.request.headers["User-Agent"] = (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        
        # Accept 헤더가 없으면 브라우저 기본값 설정
        if not flow.request.headers.get("Accept"):
            flow.request.headers["Accept"] = (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7"
            )
        
        # Accept-Language 헤더 추가
        if not flow.request.headers.get("Accept-Language"):
            flow.request.headers["Accept-Language"] = "ko-KR,ko;q=0.9,en;q=0.8"
        
        # Accept-Encoding 헤더 추가
        if not flow.request.headers.get("Accept-Encoding"):
            flow.request.headers["Accept-Encoding"] = "gzip, deflate, br"
        
        # Sec-CH-UA 헤더 추가 (Chrome의 Client Hints)
        if not flow.request.headers.get("Sec-CH-UA"):
            flow.request.headers["Sec-CH-UA"] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
            flow.request.headers["Sec-CH-UA-Mobile"] = "?0"
            flow.request.headers["Sec-CH-UA-Platform"] = '"macOS"'
        
        # Upgrade-Insecure-Requests 헤더 (HTTPS 요청임을 명시)
        if not flow.request.headers.get("Upgrade-Insecure-Requests"):
            flow.request.headers["Upgrade-Insecure-Requests"] = "1"
        
        # 원본 도메인에서 오는 것처럼 Referer 설정
        if not flow.request.headers.get("Referer") and flow.request.host:
            flow.request.headers["Referer"] = f"https://{flow.request.host}/"
        
        logger.debug(f"Added browser headers for {flow.request.host}")

    def responseheaders(self, flow: http.HTTPFlow):
        """
        응답 헤더 처리 (스트리밍 비활성화)
        
        Args:
            flow: mitmproxy HTTP 플로우
        """
        # 스트리밍 관련 처리 완전 비활성화 (안정성 우선)
        pass

    def response(self, flow: http.HTTPFlow):
        """
        HTTP 응답 처리

        Args:
            flow: mitmproxy HTTP 플로우
        """
        # 응답 처리 비활성화 (안정성 우선)
        pass

    def error(self, flow: http.HTTPFlow):
        """
        에러 처리

        Args:
            flow: mitmproxy HTTP 플로우
        """
        # ChatGPT 도메인 에러만 출력
        host = (flow.request.host or "").lower()
        if TARGET_HOSTS.search(host):
            print(f"❌ [에러] {host}: {flow.error}")


# mitmproxy 애드온 등록
addons = [SemanticProxy()]