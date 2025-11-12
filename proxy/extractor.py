"""
요청 데이터 추출 모듈
"""
import re
import json
import base64
from typing import Dict, Any, List, Optional
from email.parser import BytesParser
from email.policy import default as email_default
from pathlib import Path
from mitmproxy import http

from config import PATH_CONVERSATION, PATH_UPLOAD, UPLOAD_HOSTS, CONTENT_TYPE_TO_EXT
from logger import logger


class DataExtractor:
    """HTTP 요청에서 데이터를 추출하는 클래스"""

    @staticmethod
    def is_stream_request(flow: http.HTTPFlow) -> bool:
        """스트리밍 요청인지 확인 (실제 대화 요청)"""
        if flow.request.method.upper() != "POST":
            return False

        path = flow.request.path or ""
        
        # 정확한 대화 경로만 매칭 (prepare, sentinel 등 제외)
        if not re.search(r"^/backend-a(?:pi|non)/(?:f/)?conversation(?:$|/[^/]+$)", path, re.I):
            return False

        # content-type이 application/json인 경우 대화 요청으로 간주
        content_type = flow.request.headers.get("Content-Type", "").lower()
        if "application/json" in content_type:
            return True

        # Accept 헤더 확인
        accept = flow.request.headers.get("Accept", "").lower()
        if "text/event-stream" in accept:
            return True

        # SSE 경로 확인
        if "/sse/" in path:
            return True

        return False

    @staticmethod
    def is_upload_request(flow: http.HTTPFlow) -> bool:
        """업로드 요청인지 확인"""
        path = flow.request.path or ""
        host = flow.request.host or ""

        # 내부 업로드 경로
        if PATH_UPLOAD.search(path):
            return True

        # 외부 업로드 호스트
        if UPLOAD_HOSTS.search(host):
            method = flow.request.method.upper()
            return method in ("PUT", "POST")

        return False

    @staticmethod
    def extract_prompt_from_json(body: str) -> str:
        """JSON 본문에서 사용자 프롬프트 추출"""
        if not body:
            return ""

        try:
            data = json.loads(body)
            messages = data.get("messages", [])

            if not isinstance(messages, list):
                return ""

            # 최신 사용자 메시지 찾기
            for msg in reversed(messages):
                if not isinstance(msg, dict):
                    continue

                # 역할 확인
                role = DataExtractor._get_message_role(msg)
                if role != "user":
                    continue

                # 콘텐츠 추출
                content = DataExtractor._extract_message_content(msg)
                if content:
                    logger.debug(f"Extracted prompt: {content[:100]}...")
                    return content

            return ""

        except json.JSONDecodeError as e:
            logger.debug(f"JSON decode error: {e}")
            return ""
        except Exception as e:
            logger.warn(f"Error extracting prompt: {e}")
            return ""

    @staticmethod
    def _get_message_role(msg: Dict) -> str:
        """메시지에서 역할 추출"""
        # 직접 role 필드
        if "role" in msg:
            return msg["role"]

        # author 객체 내 role
        author = msg.get("author", {})
        if isinstance(author, dict):
            return author.get("role", "")

        return ""

    @staticmethod
    def _extract_message_content(msg: Dict) -> str:
        """메시지에서 콘텐츠 추출"""
        content = msg.get("content")

        # content가 리스트인 경우
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    # type이 text 또는 input_text인 경우
                    if part.get("type") in ("text", "input_text"):
                        text = part.get("text", "").strip()
                        if text:
                            return text
                elif isinstance(part, str) and part.strip():
                    return part.strip()

        # content가 딕셔너리인 경우
        elif isinstance(content, dict):
            # content_type이 text인 경우
            if content.get("content_type") == "text":
                parts = content.get("parts", [])
                if isinstance(parts, list):
                    for part in reversed(parts):
                        if isinstance(part, str) and part.strip():
                            return part.strip()

        # content가 문자열인 경우
        elif isinstance(content, str) and content.strip():
            return content.strip()

        return ""

    @staticmethod
    def extract_base64_images(body: str) -> List[Dict[str, Any]]:
        """JSON에서 base64 인코딩된 이미지 추출"""
        images = []

        # Base64 이미지 패턴
        pattern = r'data:image/(?P<type>png|jpeg|jpg|webp|gif|bmp);base64,(?P<data>[A-Za-z0-9+/=]+)'

        for match in re.finditer(pattern, body, re.I):
            try:
                image_type = match.group('type')
                image_data = base64.b64decode(match.group('data'))

                images.append({
                    "type": "base64_image",
                    "content_type": f"image/{image_type}",
                    "data": image_data,
                    "filename": f"inline.{image_type}",
                    "size": len(image_data)
                })

                logger.debug(f"Extracted base64 image: {image_type}, {len(image_data)} bytes")

            except Exception as e:
                logger.warn(f"Base64 decode error: {e}")

        return images

    @staticmethod
    def extract_cdn_urls(body: str) -> List[str]:
        """CDN URL 추출"""
        urls = []

        # OpenAI CDN URL 패턴
        patterns = [
            r'https?://([a-z0-9\.\-]*oaiusercontent\.com)(/[^"\'\s)]+)',
            r'https?://([a-z0-9\.\-]*openai\.com/[^"\'\s)]+)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, body, re.I):
                url = match.group(0)
                urls.append(url)
                logger.debug(f"Found CDN URL: {url}")

        return urls

    @staticmethod
    def parse_multipart(raw_bytes: bytes, content_type: str) -> List[Dict[str, Any]]:
        """멀티파트 폼 데이터 파싱"""
        files = []

        try:
            # Email parser를 사용한 멀티파트 파싱
            msg = BytesParser(policy=email_default).parsebytes(
                b"Content-Type: " + content_type.encode("utf-8") + b"\r\n\r\n" + raw_bytes
            )

            for part in msg.iter_parts():
                payload = part.get_payload(decode=True)
                if not payload:
                    continue

                ctype = (part.get_content_type() or "").lower()
                filename = part.get_filename()
                field_name = part.get_param("name", header="content-disposition")

                file_info = {
                    "type": "multipart",
                    "field_name": field_name,
                    "filename": filename or "unknown",
                    "content_type": ctype,
                    "data": payload,
                    "size": len(payload)
                }

                files.append(file_info)
                logger.debug(f"Extracted multipart file: {filename}, {ctype}, {len(payload)} bytes")

        except Exception as e:
            logger.warn(f"Multipart parse error: {e}")

        return files

    @staticmethod
    def extract_parent_info(flow: http.HTTPFlow) -> Dict[str, Any]:
        """요청에서 부모 메시지 정보 추출"""
        body = flow.request.get_text(strict=False) or ""

        try:
            data = json.loads(body)

            # 대화 ID
            conv_id = data.get("conversation_id")

            # 부모 메시지 ID
            parent_id = data.get("parent_message_id") or data.get("parent_id")

            # 메시지 목록에서 사용자 메시지 찾기
            messages = data.get("messages", [])
            user_msg_id = None
            user_create_time = None

            if isinstance(messages, list):
                for msg in reversed(messages):
                    if isinstance(msg, dict):
                        role = DataExtractor._get_message_role(msg)
                        if role == "user":
                            user_msg_id = msg.get("id")
                            user_create_time = msg.get("create_time")
                            break

            return {
                "conversation_id": conv_id,
                "parent_id": parent_id or user_msg_id,
                "user_create_time": user_create_time
            }

        except Exception as e:
            logger.debug(f"Error extracting parent info: {e}")
            return {}

    @staticmethod
    def guess_filename(flow: http.HTTPFlow) -> str:
        """요청에서 파일명 추측"""
        path = flow.request.path or ""
        content_type = flow.request.headers.get("content-type", "").lower()

        # URL 경로에서 파일명 추출
        if "/" in path:
            filename = path.split("/")[-1]
            if "." in filename and len(filename) < 100:
                return filename

        # Content-Type에서 확장자 추측
        for ct_pattern, ext in CONTENT_TYPE_TO_EXT.items():
            if ct_pattern in content_type:
                return f"upload{ext}"

        return "upload"

    @staticmethod
    def get_client_ip(flow: http.HTTPFlow) -> str:
        """클라이언트 IP 추출"""
        addr = flow.client_conn.address
        try:
            if isinstance(addr, tuple):
                return addr[0]
            return str(addr)
        except:
            return str(addr)