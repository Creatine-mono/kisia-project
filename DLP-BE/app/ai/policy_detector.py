"""
정책 위반 탐지 모델
EXAONE 기반 맥락 분석으로 정부 정책 위반 여부 판단
"""
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
import re
import logging

# bitsandbytes는 CUDA에서만 사용 (macOS 미지원)
try:
    from transformers import BitsAndBytesConfig
    BITSANDBYTES_AVAILABLE = True
except ImportError:
    BITSANDBYTES_AVAILABLE = False

logger = logging.getLogger(__name__)


class PolicyViolationDetector:
    """EXAONE 기반 정책 위반 탐지 모델 (QLoRA with PEFT)"""

    def __init__(
        self,
        adapter_name: str = "psh3333/EXAONE-Policy-Violation-Detector-v1",
        base_model_name: str = "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct"
    ):
        """
        정책 위반 탐지 모델 초기화

        Args:
            adapter_name: PEFT 어댑터 모델 이름
            base_model_name: 베이스 모델 이름
        """
        logger.info(f"Loading Policy Violation Detector")
        logger.info(f"Base model: {base_model_name}")
        logger.info(f"Adapter: {adapter_name}")

        # 디바이스 설정 (M4 MacBook: MPS, CUDA GPU: cuda, CPU: cpu)
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            logger.info("Using MPS (Metal Performance Shaders) for M-series Mac")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
            logger.info("Using CUDA GPU")
        else:
            self.device = torch.device("cpu")
            logger.warning("Using CPU (slow performance expected)")

        # Tokenizer 로드
        self.tokenizer = AutoTokenizer.from_pretrained(
            adapter_name,
            trust_remote_code=True
        )

        # pad_token 설정 (없으면 eos_token으로 설정)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        # 베이스 모델 로드 설정
        # MPS는 4-bit quantization을 지원하지 않으므로 조건부 적용
        if self.device.type == "cuda" and BITSANDBYTES_AVAILABLE:
            # CUDA: 4-bit quantization 사용
            logger.info("Loading base model with 4-bit quantization (CUDA)")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True
            )
        else:
            # MPS/CPU: float16 사용, device_map 없이 단일 장치에 로드
            logger.info(f"Loading base model in float16 ({self.device.type})")
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            base_model = base_model.to(self.device)

        # PEFT 어댑터 적용
        logger.info("Loading PEFT adapter...")
        self.model = PeftModel.from_pretrained(base_model, adapter_name)
        self.model.eval()

        logger.info(f"Policy Violation Detector loaded on {self.device}")

        # 시스템 프롬프트 정의 (간결하게 최적화)
        self.system_prompt = """정책 위반 분류:
SAFE | VIOLATION_PRIVACY_CITIZEN | VIOLATION_CLASSIFIED | VIOLATION_HR | VIOLATION_SALARY | VIOLATION_DELIBERATION

카테고리만 출력."""

    async def detect_violation(self, text: str) -> dict[str, str | float]:
        """
        텍스트의 정책 위반 여부 판단

        Args:
            text: 분석할 텍스트

        Returns:
            dict: {
                "judgment": "SAFE" | "VIOLATION_*",
                "confidence": float (0.0~1.0)
            }
        """
        try:
            # CPU intensive한 모델 추론을 별도 스레드에서 실행
            import asyncio
            result = await asyncio.to_thread(self._detect_violation_sync, text)
            return result

        except Exception as e:
            logger.error(f"Policy violation detection failed: {str(e)}", exc_info=True)
            # 에러 시 안전하게 SAFE 처리
            return {
                "judgment": "SAFE",
                "confidence": 0.0
            }

    def _detect_violation_sync(self, text: str) -> dict[str, str | float]:
        """동기 방식으로 정책 위반 판단"""
        # Chat template 구성
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"다음 질문을 분류하세요:\n\n{text}"}
        ]

        # 토크나이징 (chat template 적용)
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        )

        # attention_mask 생성 (모든 토큰을 attend하도록 설정)
        attention_mask = torch.ones_like(input_ids)

        # 디바이스로 이동
        input_ids = input_ids.to(self.device)
        attention_mask = attention_mask.to(self.device)

        # 생성 (카테고리만 출력하므로 토큰 수 최소화)
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_new_tokens=15,  # 50 → 15로 감소 (카테고리 이름만 필요)
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id,
                # 추가 최적화
                use_cache=True,  # KV cache 사용
                num_beams=1,  # beam search 비활성화 (greedy)
            )

        # 디코딩
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.debug(f"Model output: {result}")

        # 결과에서 카테고리 추출
        judgment = self._extract_judgment(result)
        # Confidence는 생성 모델이므로 항상 높게 설정 (실제로는 logprobs가 필요)
        confidence = 0.95 if judgment != "SAFE" else 0.98

        logger.debug(f"Policy judgment: {judgment} (confidence: {confidence:.2%})")

        return {
            "judgment": judgment,
            "confidence": confidence
        }

    def _extract_judgment(self, text: str) -> str:
        """
        생성된 텍스트에서 판단 결과 추출

        Args:
            text: 모델이 생성한 텍스트

        Returns:
            str: 추출된 카테고리 (SAFE, VIOLATION_*)
        """
        # 가능한 카테고리 패턴
        categories = [
            "VIOLATION_PRIVACY_CITIZEN",
            "VIOLATION_CLASSIFIED",
            "VIOLATION_HR",
            "VIOLATION_SALARY",
            "VIOLATION_DELIBERATION",
            "SAFE"
        ]

        # 텍스트에서 카테고리 검색 (순서대로, 먼저 매칭되는 것 반환)
        text_upper = text.upper()
        for category in categories:
            if category in text_upper:
                return category

        # 매칭 실패 시 SAFE로 처리
        logger.warning(f"Could not extract judgment from: {text}")
        return "SAFE"

    def is_safe(self, judgment: str) -> bool:
        """
        판단 결과가 안전한지 확인

        Args:
            judgment: 모델의 판단 결과

        Returns:
            bool: SAFE면 True, 그 외 False
        """
        return judgment == "SAFE"