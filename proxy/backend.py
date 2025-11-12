"""
백엔드 API 통신 모듈
"""
import time
import requests
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from config import (
    BACKEND_URL,
    BACKEND_TIMEOUT,
    BACKEND_RETRY,
    BACKEND_API_KEY,
    APIEndpoints,
    BLOCK_ON_BACKEND_ERROR
)
from logger import logger


class BackendClient:
    """백엔드 API와 통신하는 클라이언트"""

    def __init__(self):
        self.base_url = BACKEND_URL
        self.timeout = BACKEND_TIMEOUT
        self.retry_count = BACKEND_RETRY
        self.api_key = BACKEND_API_KEY

        # 기본 헤더 설정 (간소화)
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers["X-API-Key"] = self.api_key

    def comprehensive_analysis(
        self,
        prompt: str,
        files_data: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        client_ip: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        종합 분석 요청 - PII 탐지 + 유사 문서 검사

        Note: 이 엔드포인트는 백엔드에 아직 구현되지 않았습니다.
              향후 PII + 유사도 검사 통합 기능이 백엔드에 추가될 예정입니다.

        Args:
            prompt: 사용자 프롬프트
            files_data: 파일 데이터 리스트
            metadata: 추가 메타데이터
            client_ip: 클라이언트 IP 주소 (백엔드 로그 기록용)

        Returns:
            (should_block, reason, additional_info)
        """
        # 모든 텍스트 콘텐츠 결합
        all_text = prompt
        for file_data in files_data:
            if file_data.get("text"):
                all_text += " " + file_data["text"]
        
        # 텍스트가 비어있으면 통과
        if not all_text.strip():
            logger.debug("No text content to check, allowing")
            return (False, "no_content", None)
        
        endpoint = f"{self.base_url}{APIEndpoints.COMPREHENSIVE_ANALYSIS}"
        payload = {"text": all_text.strip()}

        for attempt in range(self.retry_count):
            try:
                logger.debug(f"Comprehensive analysis (attempt {attempt + 1}/{self.retry_count})")

                start_time = time.time()

                # 헤더 구성 (클라이언트 IP 포함)
                headers = self.headers.copy()
                if client_ip:
                    headers["X-Forwarded-For"] = client_ip

                # requests 세션을 사용해서 더 안정적으로 요청
                with requests.Session() as session:
                    session.headers.update(headers)
                    response = session.post(
                        endpoint,
                        json=payload,
                        timeout=(5, self.timeout)  # (연결 타임아웃, 읽기 타임아웃)
                    )

                elapsed = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()
                    blocked = result.get("blocked", False)
                    block_reasons = result.get("block_reasons", [])
                    
                    # PII 분석 결과
                    pii_analysis = result.get("pii_analysis", {})
                    pii_entities = pii_analysis.get("entities", [])
                    
                    # 유사 문서 분석 결과
                    similarity_analysis = result.get("similarity_analysis", {})
                    max_similarity = similarity_analysis.get("max_similarity", 0)
                    matched_docs = similarity_analysis.get("matched_documents", [])
                    
                    # 결과 로깅
                    if pii_entities:
                        entities_str = ", ".join([f"{e.get('type')}" for e in pii_entities[:3]])
                        if len(pii_entities) > 3:
                            entities_str += f" 등 {len(pii_entities)}개"
                        print(f"🚨 [PII 탐지] {entities_str}")
                    
                    if similarity_analysis.get("is_similar"):
                        sim_percent = round(max_similarity * 100, 1)
                        print(f"📄 [유사 문서] 최대 유사도 {sim_percent}%")
                    
                    logger.debug(f"Comprehensive analysis result: blocked={blocked}, reasons={block_reasons}")

                    if blocked:
                        # 포맷된 메시지 생성
                        from response import ResponseGenerator
                        formatted_message = ResponseGenerator.format_comprehensive_analysis_message(result)
                        
                        return (
                            True,
                            "_".join(block_reasons),
                            {
                                "message": formatted_message,
                                "analysis_result": result,
                                "pii_entities": pii_entities,
                                "similarity_docs": matched_docs
                            }
                        )
                    else:
                        return (False, "analysis_passed", None)

                elif response.status_code == 400:
                    logger.warn(f"Backend validation error: {response.text[:200]}")
                    return (False, "validation_error", None)
                    
                elif response.status_code == 429:
                    # Rate limit
                    logger.warn(f"Rate limited by backend, waiting...")
                    time.sleep(2 ** attempt)

                else:
                    logger.warn(f"Backend returned HTTP {response.status_code}: {response.text[:200]}")

            except requests.exceptions.Timeout as e:
                print(f"⏰ [타임아웃] 백엔드 응답 시간 초과")
                logger.warn(f"Backend timeout (attempt {attempt + 1}/{self.retry_count}): {e}")

            except requests.exceptions.ConnectionError:
                print(f"❌ [연결 실패] 백엔드 서버 연결 실패")
                logger.error(f"Cannot connect to backend at {self.base_url}")

            except Exception as e:
                print(f"❌ [API 오류] {str(e)[:100]}")
                logger.error(f"Backend error: {e}")

            # 재시도 대기
            if attempt < self.retry_count - 1:
                time.sleep(0.5 * (attempt + 1))

        # 백엔드 실패 시 처리
        if BLOCK_ON_BACKEND_ERROR:
            logger.warn("Backend unavailable, blocking by default")
            return (True, "backend_unavailable", {"message": "서비스를 일시적으로 사용할 수 없습니다."})
        else:
            logger.warn("Backend unavailable, allowing by default")
            return (False, "backend_unavailable", None)

    def check_content(
        self,
        prompt: str,
        files_data: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        client_ip: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        콘텐츠 검사 요청 - PII 탐지 + 정책 위반 검사

        Args:
            prompt: 사용자 프롬프트
            files_data: 파일 데이터 리스트
            metadata: 추가 메타데이터
            client_ip: 클라이언트 IP 주소 (백엔드 로그 기록용)

        Returns:
            (should_block, reason, additional_info)
        """
        # 모든 텍스트 콘텐츠 결합
        all_text = prompt
        for file_data in files_data:
            if file_data.get("text"):
                all_text += " " + file_data["text"]
        
        # 텍스트가 비어있으면 통과
        if not all_text.strip():
            logger.debug("No text content to check, allowing")
            return (False, "no_content", None)
        
        endpoint = f"{self.base_url}{APIEndpoints.CHECK_CONTENT}"
        payload = {"text": all_text.strip()}

        for attempt in range(self.retry_count):
            try:
                logger.debug(f"Checking PII (attempt {attempt + 1}/{self.retry_count})")

                start_time = time.time()

                # 헤더 구성 (클라이언트 IP 포함)
                headers = self.headers.copy()
                if client_ip:
                    headers["X-Forwarded-For"] = client_ip

                # requests 세션을 사용해서 더 안정적으로 요청
                with requests.Session() as session:
                    session.headers.update(headers)
                    response = session.post(
                        endpoint,
                        json=payload,
                        timeout=(5, self.timeout)  # (연결 타임아웃, 읽기 타임아웃)
                    )

                elapsed = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()
                    has_pii = result.get("has_pii", False)
                    reason = result.get("reason", "")
                    details = result.get("details", "")
                    entities = result.get("entities", [])

                    # 정책 위반 필드 처리 (하위 호환성: 없으면 기본값)
                    policy_violation = result.get("policy_violation", False)
                    policy_judgment = result.get("policy_judgment")
                    policy_confidence = result.get("policy_confidence")

                    # PII 탐지 결과 로그
                    if entities:
                        entities_str = ", ".join([f"{e.get('type')}" for e in entities[:3]])
                        if len(entities) > 3:
                            entities_str += f" 등 {len(entities)}개"
                        print(f"🚨 [PII 탐지] {entities_str}")

                    # 정책 위반 결과 로그
                    if policy_violation:
                        confidence_str = f" (신뢰도: {policy_confidence:.1%})" if policy_confidence else ""
                        print(f"⚠️  [정책 위반] {policy_judgment}{confidence_str}")

                    logger.debug(f"Detection result: has_pii={has_pii}, policy_violation={policy_violation}, entities={len(entities)}")

                    # PII 또는 정책 위반 중 하나라도 있으면 차단
                    should_block = has_pii or policy_violation

                    if should_block:
                        # 차단 타입 결정
                        if has_pii and policy_violation:
                            block_type = "pii_and_policy_violation"
                            message = f"개인정보 및 정책 위반이 탐지되어 전송이 차단되었습니다.\n\n{details}"
                        elif has_pii:
                            block_type = f"pii_detected_{len(entities)}_entities"
                            message = f"개인정보가 탐지되어 전송이 차단되었습니다.\n\n{details}"
                        else:  # policy_violation only
                            block_type = f"policy_violation_{policy_judgment or 'detected'}"
                            message = f"정책 위반이 탐지되어 전송이 차단되었습니다.\n\n{details}"

                        return (
                            True,
                            block_type,
                            {
                                "message": message,
                                "entities": entities,
                                "reason": reason,
                                "policy_violation": policy_violation,
                                "policy_judgment": policy_judgment,
                                "policy_confidence": policy_confidence
                            }
                        )
                    else:
                        return (False, "no_detection", None)

                elif response.status_code == 400:
                    logger.warn(f"Backend validation error: {response.text[:200]}")
                    return (False, "validation_error", None)
                    
                elif response.status_code == 429:
                    # Rate limit
                    logger.warn(f"Rate limited by backend, waiting...")
                    time.sleep(2 ** attempt)

                else:
                    logger.warn(f"Backend returned HTTP {response.status_code}: {response.text[:200]}")

            except requests.exceptions.Timeout as e:
                print(f"⏰ [타임아웃] 백엔드 응답 시간 초과")
                logger.warn(f"Backend timeout (attempt {attempt + 1}/{self.retry_count}): {e}")

            except requests.exceptions.ConnectionError:
                print(f"❌ [연결 실패] 백엔드 서버 연결 실패")
                logger.error(f"Cannot connect to backend at {self.base_url}")

            except Exception as e:
                print(f"❌ [API 오류] {str(e)[:100]}")
                logger.error(f"Backend error: {e}")

            # 재시도 대기
            if attempt < self.retry_count - 1:
                time.sleep(0.5 * (attempt + 1))

        # 백엔드 실패 시 처리
        if BLOCK_ON_BACKEND_ERROR:
            logger.warn("Backend unavailable, blocking by default")
            return (True, "backend_unavailable", {"message": "서비스를 일시적으로 사용할 수 없습니다."})
        else:
            logger.warn("Backend unavailable, allowing by default")
            return (False, "backend_unavailable", None)
        

    def process_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str
    ) -> Dict[str, Any]:
        """
        파일 처리 요청 - 파일 원본을 백엔드로 전송
        백엔드에서 PDF 파싱, OCR, 텍스트 추출 등 모든 처리 수행

        Args:
            file_bytes: 파일 원본 바이트 데이터
            filename: 파일명
            content_type: 콘텐츠 타입

        Returns:
            백엔드에서 처리된 결과 (추출된 텍스트 포함)
        """
        # ========== 임시 테스트 로직 (백엔드 개발 전) ==========
        # 파일 처리 없이 기본 정보만 반환
        logger.debug(f"TEST: Mock processing file {filename} ({len(file_bytes)} bytes)")
        
        # 텍스트 파일인 경우 내용 확인
        extracted_text = ""
        if content_type.startswith("text/") or filename.endswith((".txt", ".md", ".json")):
            try:
                extracted_text = file_bytes.decode("utf-8", errors="ignore")[:1000]  # 처음 1000자만
                logger.debug(f"TEST: Extracted {len(extracted_text)} chars from text file")
            except:
                pass
        
        return {
            "filename": filename,
            "content_type": content_type,
            "text": extracted_text,
            "size": len(file_bytes),
            "processed_by": "test_mock"
        }
        
        # ========== 실제 백엔드 통신 코드 (주석 처리) ==========
        # 백엔드 개발 완료 후 위의 테스트 로직을 제거하고 아래 코드 활성화
        """
        endpoint = f"{self.base_url}{APIEndpoints.PROCESS_FILE}"

        # 파일 크기 체크 (선택적)
        max_size = 50 * 1024 * 1024  # 50MB
        if len(file_bytes) > max_size:
            logger.warn(f"File {filename} too large ({len(file_bytes)} bytes), skipping")
            return {
                "filename": filename,
                "content_type": content_type,
                "text": "",
                "error": "file_too_large",
                "size": len(file_bytes)
            }

        for attempt in range(self.retry_count):
            try:
                logger.debug(f"Sending file {filename} to backend (attempt {attempt + 1}/{self.retry_count})")

                # 파일 원본을 multipart/form-data로 전송
                files = {
                    'file': (filename, file_bytes, content_type)
                }

                # 추가 메타데이터가 필요한 경우
                data = {
                    'process_options': 'ocr,extract_text,parse_pdf'
                }

                response = requests.post(
                    endpoint,
                    files=files,
                    data=data,
                    headers={"X-API-Key": self.api_key} if self.api_key else {},
                    timeout=self.timeout * 2  # 파일 처리는 더 오래 걸릴 수 있음
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"File processed by backend: {filename}, extracted {len(result.get('text', ''))} chars")
                    return result

                else:
                    logger.warn(f"Backend file processing failed with HTTP {response.status_code}")

            except requests.exceptions.Timeout:
                logger.warn(f"Backend timeout processing file {filename}")

            except Exception as e:
                logger.error(f"Backend file processing error: {e}")

            # 재시도 대기
            if attempt < self.retry_count - 1:
                time.sleep(0.5 * (attempt + 1))

        # 실패 시 빈 결과 반환
        return {
            "filename": filename,
            "content_type": content_type,
            "text": "",
            "error": "processing_failed"
        }
        """

    def health_check(self) -> bool:
        """백엔드 PII 서비스 헬스 체크"""
        try:
            endpoint = f"{self.base_url}{APIEndpoints.HEALTH}"
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=3
            )
            
            if response.status_code == 200:
                result = response.json()
                model_loaded = result.get("model_loaded", False)
                status = result.get("status", "unknown")
                
                logger.debug(f"PII service health: {status}, model_loaded: {model_loaded}")
                return status == "healthy" and model_loaded
            else:
                logger.debug(f"Health check failed with status {response.status_code}")
                return False

        except Exception as e:
            logger.debug(f"Health check failed: {e}")
            return False


# 싱글톤 인스턴스
backend_client = BackendClient()