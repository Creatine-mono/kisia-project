import os
import sys
import json
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import wandb
from huggingface_hub import login, HfApi, create_repo

MODEL_NAME = "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct"
HF_REPO_NAME = "psh3333/EXAONE-Policy-Violation-Detector-v1"
WANDB_PROJECT = "policy-violation-detector"
WANDB_RUN_NAME = "exaone-policy-v1-50k"  

# 데이터 파일 경로
TRAIN_FILE = "./train_policy_final.jsonl"
VALID_FILE = "./valid_policy_final.jsonl"


# 하이퍼 파라미터
OUTPUT_DIR = "/workspace/outputs"
NUM_EPOCHS = 3  
BATCH_SIZE = 16  
GRADIENT_ACCUMULATION = 2  
LEARNING_RATE = 2e-4  
MAX_LENGTH = 512  
LORA_RANK = 64
LORA_ALPHA = 16



# WandB 및 HuggingFace 인증 설정
def setup_authentication():
    """WandB 및 HuggingFace 로그인"""
    wandb_api_key = os.environ.get('WANDB_API_KEY')
    if wandb_api_key:
        wandb.login(key=wandb_api_key)
    else:
        wandb.login()

    hf_token = os.environ.get('HF_TOKEN')
    if hf_token:
        login(token=hf_token)
    else:
        try:
            login()
        except Exception as e:
            print(f"HuggingFace 로그인 실패: {e}")

# 올라와있는 데이터 확인
def load_data():
    """학습 데이터 로드"""
    if not os.path.exists(TRAIN_FILE):
        print(f"학습 데이터 파일을 찾을 수 없음: {TRAIN_FILE}")
        sys.exit(1)
    if not os.path.exists(VALID_FILE):
        print(f"검증 데이터 파일을 찾을 수 없음: {VALID_FILE}")
        sys.exit(1)

    train_count = sum(1 for _ in open(TRAIN_FILE, 'r', encoding='utf-8'))
    valid_count = sum(1 for _ in open(VALID_FILE, 'r', encoding='utf-8'))

    print(f"학습 데이터: {train_count}개")
    print(f"검증 데이터: {valid_count}개")

    return train_count, valid_count

# 허깅페이스 모델로드
def load_model():
    """모델 및 토크나이저 로드"""
    # QLoRA 설정 (4bit 양자화) 8bit하면 항상 에러뜸 ㅠㅠ
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True
    )
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    return model, tokenizer

# LoRA 설정
def setup_lora(model):
    """LoRA 설정 및 적용"""
    lora_config = LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ], # 어텐션~
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, lora_config)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"학습 가능 파라미터: {trainable:,} ({100*trainable/total:.2f}%)")
    print(f"전체 파라미터: {total:,}")

    return model

# 데이터 전처리
def preprocess_data(tokenizer):
    """데이터 전처리"""
    dataset = load_dataset('json', data_files={
        'train': TRAIN_FILE,
        'validation': VALID_FILE
    })

    def convert_to_messages(example):
        system_msg = """당신은 정부 정책 관련 질문의 위반 유형을 분류하는 전문 시스템입니다.

다음 카테고리 중 하나로 분류하세요:
- SAFE: 공개된 정보에 대한 안전한 질문
- VIOLATION_PRIVACY_CITIZEN: 시민의 개인정보/사생활 침해
- VIOLATION_CLASSIFIED: 국가 기밀/분류된 정보 요청
- VIOLATION_HR: 공무원 인사 정보 요청
- VIOLATION_SALARY: 공무원 급여/연봉 정보 요청
- VIOLATION_DELIBERATION: 정부 내부 심의/의사결정 과정 요청"""

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"다음 질문을 분류하세요:\n\n{example['prompt']}"},
            {"role": "assistant", "content": example['policy']}
        ]
        return {"messages": messages}

    dataset = dataset.map(convert_to_messages)

    def preprocess_function(examples):
        texts = []
        for msgs in examples['messages']:
            text = tokenizer.apply_chat_template(
                msgs,
                tokenize=False,
                add_generation_prompt=False
            )
            texts.append(text)

        model_inputs = tokenizer(
            texts,
            max_length=MAX_LENGTH,
            truncation=True,
            padding="max_length",
        )
        model_inputs["labels"] = model_inputs["input_ids"].copy()
        return model_inputs

    tokenized_datasets = dataset.map(
        preprocess_function,
        batched=True,
        remove_columns=dataset["train"].column_names,
    )

    print(f"Train: {len(tokenized_datasets['train'])}")
    print(f"Valid: {len(tokenized_datasets['validation'])}")

    return tokenized_datasets

# 학습
def train_model(model, tokenizer, tokenized_datasets):
    """모델 학습"""
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE * 2,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION,
        learning_rate=LEARNING_RATE,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,  #
        logging_steps=50,
        save_steps=500,
        eval_steps=500,
        evaluation_strategy="steps",
        save_total_limit=2,
        load_best_model_at_end=True,
        bf16=True,
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        report_to="wandb",
        run_name=WANDB_RUN_NAME,
        dataloader_num_workers=4,  # 데이터 로딩 병렬화
        dataloader_pin_memory=True,  # GPU 전송 속도 향상
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
    )

    print(f"학습 시작 - Total steps: {len(tokenized_datasets['train']) // (BATCH_SIZE * GRADIENT_ACCUMULATION) * NUM_EPOCHS}")
    trainer.train()
    print("학습 완료")

    return trainer

# 모델 저장
def save_model(model, tokenizer):
    """모델 저장"""
    output_path = os.path.join(OUTPUT_DIR, "final")
    os.makedirs(output_path, exist_ok=True)

    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)

    print(f"모델 저장 완료: {output_path}")
    return output_path

# 허깅페이스 업로드
def upload_to_huggingface(output_path, tokenized_datasets):
    """HuggingFace Hub에 모델 업로드"""
    try:
        create_repo(
            repo_id=HF_REPO_NAME,
            repo_type="model",
            exist_ok=True,
            private=False
        )

        api = HfApi()
        api.upload_folder(
            folder_path=output_path,
            repo_id=HF_REPO_NAME,
            repo_type="model",
            commit_message=f"Update Parliament Detector v3 (EXAONE) - {len(tokenized_datasets['train'])} samples"
        )

        print(f"업로드 완료: https://huggingface.co/{HF_REPO_NAME}")

    except Exception as e:
        print(f"업로드 실패: {e}")
        print(f"수동 업로드: huggingface-cli upload {HF_REPO_NAME} {output_path}")

# 테스트
def test_model(model, tokenizer):
    """모델 테스트"""
    test_cases = [
        "정부의 공개된 정책 안내 자료는 어디서 확인할 수 있나요?",
        "국민의 인터넷 사용 기록을 정부가 추적하고 있나요?",
        "국가안보원의 기밀 문서에 접근할 수 있나요?",
        "특정 공무원의 인사 평가 기록을 알 수 있나요?",
        "장관의 정확한 연봉은 얼마인가요?",
        "정부의 내부 회의록을 공개해 주세요.",
    ]

    system_msg = """당신은 정부 정책 관련 질문의 위반 유형을 분류하는 전문 시스템입니다.

다음 카테고리 중 하나로 분류하세요:
- SAFE: 공개된 정보에 대한 안전한 질문
- VIOLATION_PRIVACY_CITIZEN: 시민의 개인정보/사생활 침해
- VIOLATION_CLASSIFIED: 국가 기밀/분류된 정보 요청
- VIOLATION_HR: 공무원 인사 정보 요청
- VIOLATION_SALARY: 공무원 급여/연봉 정보 요청
- VIOLATION_DELIBERATION: 정부 내부 심의/의사결정 과정 요청"""

    for test_text in test_cases:
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"다음 질문을 분류하세요:\n\n{test_text}"}
        ]

        inputs = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=100,
                temperature=0.1,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )

        response = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
        print(f"\n질문: {test_text}")
        print(f"판단: {response}")
        print("-"*60)

# 메인
def main():
    """메인 실행 함수"""
    try:
        # 1. GPU 확인
        check_gpu()

        # 2. 인증 설정
        setup_authentication()

        # 3. 데이터 로드
        train_count, valid_count = load_data()

        # 4. 모델 로드
        model, tokenizer = load_model()

        # 5. LoRA 설정
        model = setup_lora(model)

        # 6. 데이터 전처리
        tokenized_datasets = preprocess_data(tokenizer)

        # 7. 학습
        trainer = train_model(model, tokenizer, tokenized_datasets)

        # 8. 모델 저장
        output_path = save_model(model, tokenizer)

        # 9. HuggingFace 업로드
        upload_to_huggingface(output_path, tokenized_datasets)

        # 10. 테스트
        test_model(model, tokenizer)

        # WandB 종료
        if wandb.run:
            wandb.finish()

        print("="*60)
        print("모든 작업 완료!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
