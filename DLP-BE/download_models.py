"""
정책 위반 탐지 모델 사전 다운로드 스크립트

서버 시작 전에 미리 모델을 다운로드하여 캐시에 저장합니다.
한 번 실행하면 ~/.cache/huggingface/hub/ 에 저장되어
서버 재시작 시 빠르게 로드됩니다.
"""
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

print("=" * 60)
print("모델 사전 다운로드 시작")
print("=" * 60)

# 1. 베이스 모델 다운로드
print("\n[1/3] 베이스 모델 다운로드 중...")
print("모델: LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct")
print("크기: ~15GB (시간이 오래 걸릴 수 있습니다)")
print("-" * 60)

base_model_name = "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct"
# MPS/macOS에서 device_map="auto"는 PEFT 로딩 시 오류 발생
# 다운로드만 하므로 device_map 없이 로드
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.float16,
    trust_remote_code=True,
    low_cpu_mem_usage=True
)
print("✓ 베이스 모델 다운로드 완료!")

# 2. 어댑터 다운로드
print("\n[2/3] PEFT 어댑터 다운로드 중...")
print("모델: psh3333/EXAONE-Policy-Violation-Detector-v1")
print("크기: ~수백MB")
print("-" * 60)

adapter_name = "psh3333/EXAONE-Policy-Violation-Detector-v1"
model = PeftModel.from_pretrained(base_model, adapter_name)
print("✓ 어댑터 다운로드 완료!")

# 3. Tokenizer 다운로드
print("\n[3/3] Tokenizer 다운로드 중...")
print("-" * 60)

tokenizer = AutoTokenizer.from_pretrained(
    adapter_name,
    trust_remote_code=True
)
print("✓ Tokenizer 다운로드 완료!")

# 완료
print("\n" + "=" * 60)
print("✓ 모든 모델 다운로드 완료!")
print("=" * 60)
print(f"\n저장 위치: ~/.cache/huggingface/hub/")
print(f"- models--LGAI-EXAONE--EXAONE-3.5-7.8B-Instruct/")
print(f"- models--psh3333--EXAONE-Policy-Violation-Detector-v1/")
print("\n다음부터는 서버 시작 시 이 캐시를 사용합니다.")
print("네트워크 없이도 작동 가능합니다.\n")