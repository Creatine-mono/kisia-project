"""
응답 생성 모듈
"""
import json
import time
import uuid
from typing import Dict, Any, Optional
from mitmproxy import http

from logger import logger


class ResponseGenerator:
    """차단 응답을 생성하는 클래스"""

    @staticmethod
    def create_sse_block_response(
        flow: http.HTTPFlow,
        message: str,
        parent_info: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
        user_prompt: str = ""
    ) -> http.Response:
        """
        SSE(Server-Sent Events) 형식의 차단 응답 생성

        Args:
            flow: HTTP 플로우
            message: 사용자에게 표시할 메시지
            parent_info: 부모 메시지 정보
            details: 추가 상세 정보

        Returns:
            SSE 형식의 HTTP 응답
        """
        # 부모 정보 확인
        if not parent_info:
            parent_info = {}

        # 대화 및 메시지 ID 생성
        conv_id = parent_info.get("conversation_id") or str(uuid.uuid4())
        parent_id = parent_info.get("parent_id")
        user_create_time = parent_info.get("user_create_time")

        # 타임스탬프 계산
        if user_create_time and isinstance(user_create_time, (int, float)):
            create_time = float(user_create_time) + 1.2
        else:
            create_time = time.time()

        # 메시지 ID 생성
        msg_id = f"block-{uuid.uuid4().hex[:8]}"

        # ChatGPT 응답 페이로드 구성
        payload = ResponseGenerator._build_chatgpt_payload(
            msg_id=msg_id,
            message=message,
            conv_id=conv_id,
            parent_id=parent_id,
            create_time=create_time,
            details=details
        )

        # SSE 형식으로 변환
        sse_data = ResponseGenerator._format_sse_data(payload)

        # HTTP 응답 생성
        response = http.Response.make(
            200,
            sse_data,
            {
                "Content-Type": "text/event-stream; charset=utf-8",
                "Cache-Control": "no-cache, no-transform",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )

        logger.info(f"Created SSE block response: conv={conv_id}, parent={parent_id}")

        return response

    @staticmethod
    def _build_chatgpt_payload(
        msg_id: str,
        message: str,
        conv_id: str,
        parent_id: Optional[str],
        create_time: float,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """ChatGPT 형식의 메시지 페이로드 생성"""

        # 기본 메시지 구조
        payload = {
            "message": {
                "id": msg_id,
                "author": {
                    "role": "assistant",
                    "name": None,
                    "metadata": {}
                },
                "create_time": create_time,
                "update_time": create_time,
                "content": {
                    "content_type": "text",
                    "parts": [message]
                },
                "status": "finished_successfully",
                "end_turn": True,
                "weight": 1.0,
                "metadata": {
                    "finish_details": {
                        "type": "stop",
                        "stop_tokens": [100260]
                    },
                    "is_complete": True,
                    "model_slug": "gpt-4",
                    "parent_id": parent_id,
                    "timestamp_": "absolute"
                },
                "recipient": "all"
            },
            "conversation_id": conv_id,
            "error": None
        }

        # 부모 ID 설정
        if parent_id:
            payload["message"]["parent"] = parent_id

        # 추가 상세 정보가 있으면 메타데이터에 포함
        if details:
            payload["message"]["metadata"]["block_details"] = details

        return payload

    @staticmethod
    def _format_sse_data(payload: Dict[str, Any]) -> bytes:
        """페이로드를 SSE 형식으로 변환"""

        # JSON 직렬화
        json_data = json.dumps(payload, ensure_ascii=False)

        # SSE 형식으로 포맷팅
        sse_lines = [
            f"data: {json_data}",
            "",
            "data: [DONE]",
            "",
            ""
        ]

        return "\n".join(sse_lines).encode("utf-8")

    @staticmethod
    def create_sse_response(
        flow: http.HTTPFlow,
        message: str,
        parent_info: Optional[Dict[str, Any]] = None
    ) -> http.Response:
        """
        일반 SSE(Server-Sent Events) 응답 생성 (차단이 아닌 일반 응답)

        Args:
            flow: HTTP 플로우
            message: 사용자에게 표시할 메시지
            parent_info: 부모 메시지 정보

        Returns:
            SSE 형식의 HTTP 응답
        """
        # 부모 정보 확인
        if not parent_info:
            parent_info = {}

        # 대화 및 메시지 ID 생성
        conv_id = parent_info.get("conversation_id") or str(uuid.uuid4())
        parent_id = parent_info.get("parent_id")
        
        # 타임스탬프 계산
        create_time = time.time()
        message_id = str(uuid.uuid4())

        # SSE 응답 생성
        response_data = ResponseGenerator._create_chatgpt_response(
            message=message,
            conv_id=conv_id,
            message_id=message_id,
            parent_id=parent_id,
            create_time=create_time
        )

        return http.Response.make(
            200,
            response_data,
            {
                "Content-Type": "text/event-stream; charset=utf-8",
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )

    @staticmethod
    def create_error_response(
        flow: http.HTTPFlow,
        error_message: str,
        status_code: int = 500
    ) -> http.Response:
        """
        에러 응답 생성

        Args:
            flow: HTTP 플로우
            error_message: 에러 메시지
            status_code: HTTP 상태 코드

        Returns:
            에러 HTTP 응답
        """
        error_data = {
            "error": {
                "message": error_message,
                "type": "server_error",
                "code": status_code
            }
        }

        return http.Response.make(
            status_code,
            json.dumps(error_data, ensure_ascii=False).encode("utf-8"),
            {
                "Content-Type": "application/json; charset=utf-8",
                "Cache-Control": "no-cache"
            }
        )

    @staticmethod
    def create_json_response(
        data: Dict[str, Any],
        status_code: int = 200
    ) -> http.Response:
        """
        일반 JSON 응답 생성

        Args:
            data: 응답 데이터
            status_code: HTTP 상태 코드

        Returns:
            JSON HTTP 응답
        """
        return http.Response.make(
            status_code,
            json.dumps(data, ensure_ascii=False).encode("utf-8"),
            {
                "Content-Type": "application/json; charset=utf-8",
                "Cache-Control": "no-cache"
            }
        )

    @staticmethod
    def format_detection_message(details: Dict[str, Any]) -> str:
        """
        PII 탐지 및 정책 위반 결과를 사용자 친화적인 메시지로 변환

        Args:
            details: backend.check_content()가 반환한 상세 정보
                {
                    "message": "기본 메시지",
                    "entities": [...],
                    "reason": "...",
                    "policy_violation": bool,
                    "policy_judgment": str,
                    "policy_confidence": float
                }

        Returns:
            포맷된 사용자 안내 메시지
        """
        if not details:
            return "🚨 요청이 차단되었습니다."

        message_lines = ["🚨 요청이 차단되었습니다.", ""]

        # 차단 사유
        reasons = []
        entities = details.get("entities", [])
        policy_violation = details.get("policy_violation", False)

        # PII 탐지 여부
        if entities:
            reasons.append(f"개인정보 {len(entities)}개 탐지됨")

        # 정책 위반 여부
        if policy_violation:
            policy_judgment = details.get("policy_judgment", "정책 위반")
            reasons.append(f"정책 위반 탐지됨 ({policy_judgment})")

        # 사유 표시
        if reasons:
            message_lines.append("차단 사유:")
            for reason in reasons:
                message_lines.append(f"• {reason}")
            message_lines.append("")

        # PII 상세 정보
        if entities:
            message_lines.append("탐지된 개인정보:")
            for entity in entities:
                entity_type = entity.get("type", "UNKNOWN")
                entity_value = entity.get("value", "")
                confidence = entity.get("confidence", 0)

                # 개인정보 마스킹 (처음 2자만 표시)
                if len(entity_value) > 4:
                    masked_value = entity_value[:2] + "*" * (len(entity_value) - 2)
                else:
                    masked_value = entity_value[0] + "*" * (len(entity_value) - 1) if entity_value else "****"

                confidence_percent = round(confidence * 100, 1) if confidence else 0
                message_lines.append(f"• {entity_type}: '{masked_value}' (신뢰도: {confidence_percent}%)")
            message_lines.append("")

        # 정책 위반 상세 정보
        if policy_violation:
            policy_judgment = details.get("policy_judgment")
            policy_confidence = details.get("policy_confidence")

            message_lines.append("정책 위반 정보:")
            if policy_judgment:
                message_lines.append(f"• 위반 유형: {policy_judgment}")
            if policy_confidence is not None:
                confidence_percent = round(policy_confidence * 100, 1)
                message_lines.append(f"• 신뢰도: {confidence_percent}%")
            message_lines.append("")

        # 안내 메시지
        message_lines.append("본 요청은 개인정보 보호 정책에 따라 차단되었습니다.")
        message_lines.append("문의사항이 있으시면 관리자에게 문의해 주세요.")

        return "\n".join(message_lines)

    @staticmethod
    def format_comprehensive_analysis_message(analysis_result: Dict[str, Any]) -> str:
        """
        종합 분석 API 응답을 사용자 친화적인 메시지로 변환

        Args:
            analysis_result: /api/v1/analyze/comprehensive API 응답 데이터

        Returns:
            포맷된 사용자 안내 메시지
        """
        if not analysis_result.get("blocked", False):
            return "✅ 요청이 승인되었습니다."

        # 차단 메시지 시작
        message_lines = ["🚨 요청이 차단되었습니다."]
        message_lines.append("")
        
        # 차단 사유 수집
        reasons = []
        block_reasons = analysis_result.get("block_reasons", [])
        
        # 개인정보 탐지 정보
        pii_analysis = analysis_result.get("pii_analysis", {})
        if "pii_detected" in block_reasons and pii_analysis.get("has_pii"):
            pii_count = pii_analysis.get("total_entities", 0)
            reasons.append(f"개인정보 {pii_count}개 탐지됨")
        
        # 유사 문서 탐지 정보
        similarity_analysis = analysis_result.get("similarity_analysis", {})
        if "similarity_detected" in block_reasons and similarity_analysis.get("is_similar"):
            matched_count = similarity_analysis.get("matched_count", 0)
            max_similarity = similarity_analysis.get("max_similarity", 0)
            similarity_percent = round(max_similarity * 100, 1)
            reasons.append(f"유사 문서 {matched_count}건 일치 (최대 유사도 {similarity_percent}%)")
        
        # 사유 섹션
        if reasons:
            message_lines.append("사유:")
            for reason in reasons:
                message_lines.append(f"- {reason}")
            message_lines.append("")

        # 탐지된 개인정보 상세
        if pii_analysis.get("has_pii") and pii_analysis.get("entities"):
            message_lines.append("탐지된 개인정보:")
            for entity in pii_analysis["entities"]:
                entity_type = entity.get("type", "UNKNOWN")
                entity_value = entity.get("value", "")
                confidence = entity.get("confidence", 0)
                confidence_percent = round(confidence * 100, 1)
                message_lines.append(f"- {entity_type}: '{entity_value}' (신뢰도: {confidence_percent}%)")
            message_lines.append("")

        # 유사 문서 상세
        if similarity_analysis.get("is_similar") and similarity_analysis.get("matched_documents"):
            message_lines.append("유사 문서:")
            for doc in similarity_analysis["matched_documents"]:
                doc_title = doc.get("document_title", "제목 없음")
                max_sim = doc.get("max_similarity", 0)
                sim_percent = round(max_sim * 100, 1)
                message_lines.append(f"- 제목: \"{doc_title}\"")
                message_lines.append(f"- 유사도: {sim_percent}%")

        return "\n".join(message_lines)