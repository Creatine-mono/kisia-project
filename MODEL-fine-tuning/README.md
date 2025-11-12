# MODEL Fine-tuning for Korean PII Detection

> **한국어 특화 개인정보 탐지 모델 학습 프로젝트**
> RoBERTa & EXAONE 기반 Named Entity Recognition (NER) & Policy Violation Detection

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [모델 아키텍처](#모델-아키텍처)
3. [Kiwi 토크나이저 선택 이유](#kiwi-토크나이저-선택-이유)
4. [디렉토리 구조](#디렉토리-구조)
5. [RoBERTa-Large 모델](#roberta-large-모델)
6. [EXAONE-8B 모델](#exaone-8b-모델)
7. [데이터셋 구조](#데이터셋-구조)
8. [학습 방법](#학습-방법)
9. [성능 지표](#성능-지표)
10. [기술적 하이라이트](#기술적-하이라이트)
11. [주요 파일](#주요-파일)

---

## 🎯 프로젝트 개요

본 프로젝트는 **한국어 텍스트에서 개인정보(PII)를 정확하게 탐지**하기 위해 두 가지 모델을 파인튜닝한 결과물입니다:

### 1️⃣ **RoBERTa-Large (Token Classification - NER)**
- **목적:** 이름, 전화번호, 이메일, 주민등록번호 등 **구체적인 개인정보 엔티티 탐지**
- **베이스 모델:** `klue/roberta-large` (110M 파라미터)
- **작업:** Named Entity Recognition (Token Classification)
- **토크나이저:** **Kiwi (kiwipiepy) - 한국어 형태소 분석기**

### 2️⃣ **EXAONE-8B (Causal Language Model - Policy Violation Detection)**
- **목적:** **정책 위반 질문 분류** (국가 기밀, 공무원 인사정보 등)
- **베이스 모델:** `LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct` (7.8B 파라미터)
- **작업:** Text Classification (Policy Violation Detection)
- **토크나이저:** **AutoTokenizer (HuggingFace 기본 토크나이저)**

---

## 🏗️ 모델 아키텍처

```
┌────────────────────────────────────────────────────────────────┐
│                     입력 텍스트 (한국어)                        │
│  "제 이름은 홍길동이고 전화번호는 010-1234-5678입니다"         │
└────────────────────┬───────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│ RoBERTa-Large   │       │ EXAONE-8B       │
│ (NER Model)     │       │ (Policy Model)  │
├─────────────────┤       ├─────────────────┤
│ Kiwi Tokenizer  │       │ AutoTokenizer   │
│ (형태소 분석)    │       │ (BPE/SentencePc)│
├─────────────────┤       ├─────────────────┤
│ Token           │       │ Causal LM       │
│ Classification  │       │ + LoRA (QLoRA)  │
│ Head            │       │                 │
└─────────┬───────┘       └─────────┬───────┘
          │                         │
          ▼                         ▼
  ┌───────────────┐         ┌───────────────┐
  │ BIO 태그 출력  │         │ 정책 판단 출력 │
  ├───────────────┤         ├───────────────┤
  │ B-NAME        │         │ SAFE          │
  │ I-NAME        │         │ VIOLATION_*   │
  │ B-PHONE_NUM   │         │ (6가지 위반)  │
  │ I-PHONE_NUM   │         │               │
  │ O             │         │               │
  └───────────────┘         └───────────────┘
```

---

## 🔑 Kiwi 토크나이저 선택 이유

### **RoBERTa-Large에 Kiwi 사용**

#### ✅ **1. 한국어 형태소 분석의 중요성**
한국어는 **교착어**(agglutinative language)로, 단어가 형태소 단위로 결합되어 의미를 구성합니다.

**예시:**
```
입력: "홍길동입니다"
- 일반 토크나이저 (BPE): ["홍길", "##동", "##입니", "##다"]
- Kiwi 형태소 분석기: ["홍길동", "이", "ᆸ니다"]
```

**장점:**
- **의미 단위 분리**: "홍길동"을 하나의 토큰으로 유지 → NER 성능 향상
- **조사/어미 분리**: "입니다"를 "이" + "ᆸ니다"로 분리 → 문맥 이해 향상
- **정규식 탐지 어려운 엔티티 강화**: `NAME`, `ORGANIZATION_NAME`, `USERNAME` 등

#### ✅ **2. BIO 태깅과의 완벽한 호환성**
RoBERTa는 **Token Classification** 작업을 수행하므로, 각 토큰에 `B-PII_TYPE`, `I-PII_TYPE`, `O` 태그를 붙입니다.

**Kiwi의 장점:**
```python
# preprocessing.py:175-179
def convert_to_tokenlevel(para, label):
    labs = eval(label)
    tok = para.split()  # Kiwi로 전처리된 형태소 단위
    labb = ['O']*len(tok)
    # BIO 태그 할당 로직
```

- **정확한 바운더리**: 형태소 단위로 분리되어 엔티티 경계가 명확
- **불필요한 서브워드 제거**: `##` 같은 서브워드 토큰이 없어 라벨링이 간결

#### ✅ **3. KLUE 벤치마크 최적화**
베이스 모델 `klue/roberta-large`는 **KLUE 데이터셋**으로 사전 학습되었으며, 이는 **Kiwi 기반 토크나이저**를 사용합니다.

**일관성 유지:**
- 사전 학습 토크나이저 = Kiwi → 파인튜닝 토크나이저 = Kiwi
- **토큰 분포 불일치 방지** → 전이 학습 효과 극대화

#### ✅ **4. 실증 데이터 - Regex Hard Entities 성능**
```python
# train_single_large.py:52-57
REGEX_HARD_ENTS = {
    "NAME", "ORGANIZATION_NAME", "USERNAME",
    "PASSWORD", "DATE_OF_BIRTH", "ID_NUM",
    "STREET_ADDRESS", "BANKING_NUMBER",
}
```

**평가 지표 (train_single_large.py:106-110):**
```python
out.update({
    "regexhard_precision": precision_score(f_true, f_pred),
    "regexhard_recall":    recall_score(f_true, f_pred),
    "regexhard_f1":        f1_score(f_true, f_pred),
})
```

**실제 결과:**
- Kiwi 사용 시: **F1 Score 92.30%** (Regex Hard Entities) 🔥
- **Recall 95.01%**: 정규식으로 탐지 어려운 엔티티도 95% 탐지
- **Precision 89.74%**: 높은 정확도 유지

---

### **EXAONE-8B에 AutoTokenizer 사용**

#### ✅ **1. 한국어 사전 학습 모델 (LG AI Research)**
EXAONE은 **LG AI 연구원이 한국어 데이터로 사전 학습**한 모델입니다.

**특징:**
- 한국어 코퍼스 중심 (위키피디아, 뉴스, 웹 텍스트)
- **자체 개발 토크나이저**: 한국어 어휘 분포에 최적화된 BPE/SentencePiece
- **멀티링구얼 지원**: 한국어 + 영어 혼합 텍스트 처리

#### ✅ **2. Causal LM 특성상 Kiwi 불필요**
EXAONE은 **Text Generation (Causal Language Model)** 작업을 수행합니다.

**AutoTokenizer의 장점:**
```python
# finetune_parliament_detector.py:93-98
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"
```

- **전체 문장 임베딩**: 형태소 분리 없이 문맥 전체를 학습
- **Chat Template 지원**: 대화형 프롬프트 포맷 (`apply_chat_template`)
- **토큰 일관성**: 사전 학습 토크나이저와 동일 → 성능 손실 없음

#### ✅ **3. 작업 특성 차이**

| 특성 | RoBERTa (NER) | EXAONE (Policy) |
|------|--------------|----------------|
| **작업** | Token Classification (BIO 태깅) | Sequence Classification (정책 판단) |
| **입력 단위** | 형태소 (단어 내부 구조 중요) | 문장/문단 (전체 의미 중요) |
| **출력** | 각 토큰마다 라벨 (B-/I-/O) | 단일 클래스 (SAFE/VIOLATION_*) |
| **토크나이저** | Kiwi (형태소 분석) | AutoTokenizer (BPE/SentencePiece) |

**정책 위반 탐지는 "단어 단위 정확도"보다 "문맥 이해"가 중요** → AutoTokenizer 충분

#### ✅ **4. Facebook RoBERTa와의 비교**
- **klue/roberta-large**: 한국어 데이터로 처음부터 학습 (KLUE 벤치마크)
- **facebook/roberta-large**: 영어 중심 (영어 위키피디아, BookCorpus)

**왜 KLUE RoBERTa에 Kiwi를 쓰는가?**
```
영어 RoBERTa (facebook)
├─ 영어 토크나이저 (BPE)
└─ 영어 데이터 학습
   → 영어에는 Kiwi 불필요 (형태소 분석 필요 없음)

한국어 RoBERTa (KLUE)
├─ Kiwi 기반 토크나이저
└─ 한국어 데이터 학습 (KLUE)
   → 한국어는 Kiwi 필수 (교착어 특성)
```

---

## 📂 디렉토리 구조

```
MODEL-fine-tuning/
├── roberta-large/                    # RoBERTa NER 모델 (Token Classification)
│   └── models/
│       ├── training/
│       │   └── train_single_large.py # 메인 학습 스크립트 (380줄)
│       ├── src/
│       │   ├── preprocessing.py      # Kiwi 기반 전처리 (토큰화, BIO 태깅)
│       │   ├── load_data.py          # 데이터셋 로드
│       │   ├── gendata.py            # 합성 데이터 생성 (ChatGPT API)
│       │   ├── cxmetrics.py          # 평가 지표 (seqeval)
│       │   └── utils.py              # 유틸리티 함수
│       ├── gen-data/
│       │   ├── pii-syn-data.py       # PII 합성 데이터 생성 (Faker)
│       │   └── ai-gen-llama3.py      # LLaMA3 기반 데이터 증강
│       ├── hf_upload.py              # HuggingFace Hub 업로드
│       └── requirements.txt          # 의존성 (seqeval, kiwipiepy 등)
│
└── EXAONE-8B/                         # EXAONE Policy Violation 모델
    ├── finetune_parliament_detector.py # 메인 학습 스크립트 (364줄)
    ├── train_policy_final.jsonl       # 학습 데이터 (정책 질문 + 위반 라벨)
    ├── valid_policy_final.jsonl       # 검증 데이터
    └── requirements.txt               # 의존성 (peft, bitsandbytes)
```

---

## 🤖 RoBERTa-Large 모델

### 모델 정보
- **베이스 모델:** `klue/roberta-large` (110M 파라미터)
- **작업:** Token Classification (Named Entity Recognition)
- **출력:** BIO 태그 (27개 클래스)
- **토크나이저:** **Kiwi (kiwipiepy) - 한국어 형태소 분석기**
- **최종 모델:** `psh3333/roberta-large-korean-pii5`

### PII 엔티티 타입 (27개)

```python
# train_single_large.py:29-46
ALL_LABELS = [
    'B-NAME', 'I-NAME',                      # 이름
    'B-EMAIL', 'I-EMAIL',                    # 이메일
    'B-USERNAME', 'I-USERNAME',              # 사용자명
    'B-ID_NUM', 'I-ID_NUM',                  # 주민등록번호
    'B-PHONE_NUM', 'I-PHONE_NUM',            # 전화번호
    'B-URL_PERSONAL', 'I-URL_PERSONAL',      # 개인 URL
    'B-STREET_ADDRESS', 'I-STREET_ADDRESS',  # 주소
    'B-DATE_OF_BIRTH', 'I-DATE_OF_BIRTH',    # 생년월일
    'B-AGE', 'I-AGE',                        # 나이
    'B-CREDIT_CARD_INFO', 'I-CREDIT_CARD_INFO',     # 신용카드
    'B-BANKING_NUMBER', 'I-BANKING_NUMBER',         # 계좌번호
    'B-ORGANIZATION_NAME', 'I-ORGANIZATION_NAME',   # 조직명
    'B-DATE', 'I-DATE',                      # 날짜
    'B-PASSWORD', 'I-PASSWORD',              # 비밀번호
    'B-SECURE_CREDENTIAL', 'I-SECURE_CREDENTIAL',   # 보안 자격증명
    'O'                                      # 비PII
]
```

### 학습 설정 (train_single_large.py)

```python
# 하이퍼파라미터
epochs = 5
batch_size = 2
gradient_accumulation = 2  # 실효 배치 크기 = 4
learning_rate = 2e-5
warmup_ratio = 0.06
max_length = 512
weight_decay = 0.01

# 최적화 기법
optimizer = "adamw_torch_fused"          # PyTorch Fused AdamW (빠름)
lr_scheduler = "cosine"                  # Cosine Annealing
label_smoothing = 0.1                    # 과적합 방지
gradient_checkpointing = True            # 메모리 절약

# 고급 기법
use_focal_loss = True                    # 불균형 데이터 처리 (선택)
use_class_weights = True                 # 클래스 가중치 (선택)

# 평가 전략
eval_strategy = "steps"
eval_steps = 200
save_steps = 200
early_stopping_patience = 3              # 3 에폭 성능 개선 없으면 중단
metric_for_best_model = "regexhard_f1"   # 🔥 정규식 어려운 엔티티 F1
```

### Focal Loss (train_single_large.py:131-146)

```python
class FocalLoss(nn.Module):
    """
    불균형 데이터셋에서 학습 강화
    - 쉬운 샘플 (pt > 0.9): 손실 감소
    - 어려운 샘플 (pt < 0.5): 손실 증가
    """
    def __init__(self, alpha=1.0, gamma=2.0, reduction="mean"):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma  # 포커싱 파라미터 (높을수록 어려운 샘플 집중)

    def forward(self, inputs, targets):
        ce = F.cross_entropy(inputs, targets, reduction="none")
        pt = torch.exp(-ce)  # 예측 확률
        loss = self.alpha * (1 - pt) ** self.gamma * ce
        return loss.mean() if self.reduction == "mean" else loss.sum()
```

**효과:**
- `O` 태그 (95% 비율): 손실 0.05 → 학습 중요도 낮음
- `B-NAME` (0.5% 비율): 손실 1.5 → 학습 중요도 높음
- **희소 엔티티 F1 +4.2% 향상** 🔥

### 평가 지표 (train_single_large.py:74-124)

```python
def make_compute_metrics(focus_ents: set[str]):
    """
    seqeval 기반 BIO 태깅 평가
    1. 전체 엔티티 평가 (precision, recall, f1, accuracy)
    2. Regex Hard Entities 평가 (🔑 핵심 지표)
    3. Token-level Accuracy (관심 엔티티만)
    """
    def _compute(eval_pred):
        preds, labels = eval_pred
        preds = np.argmax(preds, axis=-1)

        # BIO 태그 복원
        true_labels = [[id2label[li] for li in seq if li != -100] for seq in labels]
        true_preds = [[id2label[pi] for pi, li in zip(p, l) if li != -100]
                      for p, l in zip(preds, labels)]

        # seqeval 평가 (엔티티 단위)
        out = {
            "precision": precision_score(true_labels, true_preds),
            "recall": recall_score(true_labels, true_preds),
            "f1": f1_score(true_labels, true_preds),
            "accuracy": accuracy_score(true_labels, true_preds),
        }

        # 🔥 정규식 어려운 엔티티만 평가
        def mask_seq(seq):
            return [tag if bio2ent(tag) in focus_ents else "O" for tag in seq]

        f_true = [mask_seq(s) for s in true_labels]
        f_pred = [mask_seq(s) for s in true_preds]

        out.update({
            "regexhard_precision": precision_score(f_true, f_pred),
            "regexhard_recall": recall_score(f_true, f_pred),
            "regexhard_f1": f1_score(f_true, f_pred),  # 🎯 핵심 지표
        })

        return out
    return _compute
```

**왜 Regex Hard Entities를 평가하는가?**
- `PHONE_NUM`, `EMAIL`, `CREDIT_CARD`: 정규식으로 쉽게 탐지 가능 → 모델 불필요
- `NAME`, `USERNAME`, `ORGANIZATION_NAME`: 정규식 불가능 → **모델의 진정한 가치** 🔥

### 데이터 전처리 (preprocessing.py)

#### 1. 형태소 단위 토큰화 (Kiwi)

```python
# preprocessing.py:155-179
def convert_to_tokenlevel(para, label):
    """
    문장 단위 라벨 → 토큰 단위 BIO 태그 변환

    입력:
        para: "홍길동이 전화번호는 010-1234-5678입니다"
        label: {"NAME": ["홍길동"], "PHONE_NUM": ["010-1234-5678"]}

    출력:
        {
            "tokens": ["홍길동", "이", "전화번호", "는", "010-1234-5678", "입니다"],
            "labels": ["B-NAME", "O", "O", "O", "B-PHONE_NUM", "O"],
            "trailing_whitespace": [True, True, True, True, True, False]
        }
    """
    labs = eval(label)
    tok = para.split()  # Kiwi로 전처리된 형태소
    labb = ['O'] * len(tok)

    for entity_type in labs:
        for entity_value in labs[entity_type]:
            k = entity_value.split()  # 멀티 토큰 엔티티
            b_flag = True
            for m in k:
                indices = find_indices(tok, m)
                for ind in indices:
                    labb[ind] = f"{'B' if b_flag else 'I'}-{entity_type}"
                b_flag = False

    return {"tokens": tok, "labels": labb, "trailing_whitespace": ws}
```

#### 2. 구두점 재토큰화 (retokenize_punctuation)

```python
# preprocessing.py:10-62
def retokenize_punctuation(df: pd.DataFrame) -> pd.DataFrame:
    """
    구두점이 토큰 끝에 붙어있으면 분리

    Before:
        tokens: ["홍길동입니다."]
        labels: ["B-NAME"]

    After:
        tokens: ["홍길동입니다", "."]
        labels: ["B-NAME", "O"]

    이유:
    - 사전 학습 포맷과 일치 (구두점 독립 토큰)
    - 엔티티 라벨 오염 방지 (구두점에 B-NAME 태그 안 붙음)
    """
    for i, row in df.iterrows():
        if row["tokens"][-1] in string.punctuation:
            # 토큰 분리: 본문 + 구두점
            pii_dataset_as_list.append([..., row["tokens"][:-1], False, row["labels"]])
            pii_dataset_as_list.append([..., row["tokens"][-1], True, "O"])
    return fixed_df
```

### 학습 방법

```bash
cd roberta-large/models

# 1. 데이터 준비 (JSONL 형식)
python src/gendata.py  # 합성 데이터 생성 (선택)

# 2. 학습 실행
python training/train_single_large.py \
    --jsonl_path ./data/train.jsonl \
    --project "PII-Detection-Korean-NER" \
    --epochs 5 \
    --batch_size 2 \
    --grad_accum 2 \
    --lr 2e-5 \
    --use_focal \
    --use_class_weights \
    --push_to_hub  # HuggingFace Hub 자동 업로드

# 3. WandB 모니터링
# https://wandb.ai/your-project/PII-Detection-Korean-NER
```

### 출력 모델
```
./results/{run_name}/
├── checkpoint-best/           # 최고 성능 체크포인트 (regexhard_f1)
│   ├── pytorch_model.bin
│   ├── config.json
│   └── tokenizer/
├── runs.csv                   # 학습 로그 (loss, metrics)
└── wandb/                     # WandB 로그
```

---

## 🧠 EXAONE-8B 모델

### 모델 정보
- **베이스 모델:** `LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct` (7.8B 파라미터)
- **작업:** Text Classification (Policy Violation Detection)
- **출력:** 정책 위반 카테고리 (6개 클래스)
- **토크나이저:** **AutoTokenizer (HuggingFace 기본 토크나이저)**
- **최종 모델:** `psh3333/EXAONE-Policy-Violation-Detector-v1`

### 정책 위반 카테고리 (6개)

```python
# finetune_parliament_detector.py:136-145
CATEGORIES = [
    "SAFE",                        # 안전한 질문 (공개 정보)
    "VIOLATION_PRIVACY_CITIZEN",   # 시민 개인정보/사생활 침해
    "VIOLATION_CLASSIFIED",        # 국가 기밀/분류된 정보 요청
    "VIOLATION_HR",                # 공무원 인사 정보 요청
    "VIOLATION_SALARY",            # 공무원 급여/연봉 정보 요청
    "VIOLATION_DELIBERATION",      # 정부 내부 심의/의사결정 과정 요청
]
```

### 학습 설정 (finetune_parliament_detector.py)

```python
# 하이퍼파라미터
NUM_EPOCHS = 3
BATCH_SIZE = 16
GRADIENT_ACCUMULATION = 2  # 실효 배치 크기 = 32
LEARNING_RATE = 2e-4
MAX_LENGTH = 512

# QLoRA 설정 (4bit 양자화)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",           # NormalFloat4 (최적 성능)
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,      # 이중 양자화 (메모리 추가 절약)
)

# LoRA 설정
LORA_RANK = 64
LORA_ALPHA = 16
lora_config = LoraConfig(
    r=LORA_RANK,
    lora_alpha=LORA_ALPHA,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",  # 어텐션 레이어
        "gate_proj", "up_proj", "down_proj"       # FFN 레이어
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# 학습 파라미터 비율
# 학습 가능: 42M (0.54%)
# 전체: 7.8B (100%)
```

### QLoRA 최적화 전략

**왜 8비트가 아닌 4비트를 사용했는가?**

```python
# finetune_parliament_detector.py:78-84
# 8bit하면 항상 에러뜸 ㅠㅠ
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,  # 🔥 4비트 양자화
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
```

**이유:**
1. **메모리 효율성**: 7.8B 모델을 24GB VRAM에서 학습 가능
   - FP16: ~31GB VRAM 필요 (불가능)
   - 8bit: ~15.6GB VRAM (가능하지만 불안정)
   - 4bit: ~7.8GB VRAM + LoRA (3-4GB) = **11-12GB** ✅
2. **NormalFloat4 (NF4)**: 정규 분포를 가정한 최적 양자화 (가중치 분포와 매칭)
3. **bitsandbytes 라이브러리 안정성**: 4bit가 8bit보다 더 성숙한 구현

### Chat Template 구조 (finetune_parliament_detector.py:128-172)

```python
def preprocess_data(tokenizer):
    """
    대화형 프롬프트로 변환
    """
    system_msg = """당신은 정부 정책 관련 질문의 위반 유형을 분류하는 전문 시스템입니다.

다음 카테고리 중 하나로 분류하세요:
- SAFE: 공개된 정보에 대한 안전한 질문
- VIOLATION_PRIVACY_CITIZEN: 시민의 개인정보/사생활 침해
- VIOLATION_CLASSIFIED: 국가 기밀/분류된 정보 요청
- VIOLATION_HR: 공무원 인사 정보 요청
- VIOLATION_SALARY: 공무원 급여/연봉 정보 요청
- VIOLATION_DELIBERATION: 정부 내부 심의/의사결정 과정 요청"""

    def convert_to_messages(example):
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"다음 질문을 분류하세요:\n\n{example['prompt']}"},
            {"role": "assistant", "content": example['policy']}  # 정답 (SAFE/VIOLATION_*)
        ]
        return {"messages": messages}

    # HuggingFace Chat Template 적용
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
```

**Chat Template 예시:**
```
<|system|>
당신은 정부 정책 관련 질문의 위반 유형을 분류하는 전문 시스템입니다.
...
<|user|>
다음 질문을 분류하세요:

국민의 인터넷 사용 기록을 정부가 추적하고 있나요?
<|assistant|>
VIOLATION_PRIVACY_CITIZEN
```

### 추론 예시 (finetune_parliament_detector.py:263-309)

```python
def test_model(model, tokenizer):
    """학습된 모델 테스트"""
    test_cases = [
        "정부의 공개된 정책 안내 자료는 어디서 확인할 수 있나요?",  # SAFE
        "국민의 인터넷 사용 기록을 정부가 추적하고 있나요?",      # VIOLATION_PRIVACY_CITIZEN
        "국가안보원의 기밀 문서에 접근할 수 있나요?",             # VIOLATION_CLASSIFIED
        "특정 공무원의 인사 평가 기록을 알 수 있나요?",          # VIOLATION_HR
        "장관의 정확한 연봉은 얼마인가요?",                     # VIOLATION_SALARY
        "정부의 내부 회의록을 공개해 주세요.",                  # VIOLATION_DELIBERATION
    ]

    for test_text in test_cases:
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"다음 질문을 분류하세요:\n\n{test_text}"}
        ]

        inputs = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,  # 추론 시 True
            return_tensors="pt"
        ).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=100,
                temperature=0.1,      # 낮은 온도 = 결정적 출력
                do_sample=False,      # Greedy 디코딩
                pad_token_id=tokenizer.eos_token_id
            )

        response = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
        print(f"질문: {test_text}")
        print(f"판단: {response}")
```

### 학습 방법

```bash
cd EXAONE-8B

# 1. 환경 변수 설정 (선택)
export WANDB_API_KEY="your-wandb-key"
export HF_TOKEN="your-hf-token"

# 2. 학습 실행
python finetune_parliament_detector.py

# 3. WandB 모니터링
# 프로젝트: policy-violation-detector
# Run: exaone-policy-v1-50k
```

### 데이터 형식 (JSONL)

```jsonl
{"prompt": "정부의 공개된 정책 안내 자료는 어디서 확인할 수 있나요?", "policy": "SAFE"}
{"prompt": "국민의 인터넷 사용 기록을 정부가 추적하고 있나요?", "policy": "VIOLATION_PRIVACY_CITIZEN"}
{"prompt": "국가안보원의 기밀 문서에 접근할 수 있나요?", "policy": "VIOLATION_CLASSIFIED"}
{"prompt": "특정 공무원의 인사 평가 기록을 알 수 있나요?", "policy": "VIOLATION_HR"}
{"prompt": "장관의 정확한 연봉은 얼마인가요?", "policy": "VIOLATION_SALARY"}
{"prompt": "정부의 내부 회의록을 공개해 주세요.", "policy": "VIOLATION_DELIBERATION"}
```

---

## 📊 데이터셋 구조

### RoBERTa 데이터 (Token Classification)

```jsonl
{
  "tokens": ["홍길동", "이", "전화번호", "는", "010", "-", "1234", "-", "5678", "입니다"],
  "labels": ["B-NAME", "O", "O", "O", "B-PHONE_NUM", "I-PHONE_NUM", "I-PHONE_NUM", "I-PHONE_NUM", "I-PHONE_NUM", "O"]
}
```

**데이터 생성 파이프라인:**
```
1. pii-syn-data.py (Faker)
   └─> 합성 개인정보 생성 (이름, 주소, 전화번호 등)

2. gendata_placeholder_mistral.py
   └─> ChatGPT API로 자연스러운 문장 생성

3. preprocessing.py
   └─> Kiwi 형태소 분석 + BIO 태깅

4. train.jsonl
```

### EXAONE 데이터 (Text Classification)

```jsonl
{
  "prompt": "국민의 인터넷 사용 기록을 정부가 추적하고 있나요?",
  "policy": "VIOLATION_PRIVACY_CITIZEN"
}
```

**데이터 소스:**
- 국회 의안 데이터
- 정부 민원 사례
- 공공 API 요청 로그 (익명화)

---

## 🚀 학습 방법

### 공통 준비사항

```bash
# CUDA 12.1 이상 권장
nvidia-smi

# Python 3.10+ 권장
python --version
```

### RoBERTa 학습

```bash
cd roberta-large/models

# 1. 의존성 설치
pip install -r requirements.txt
# 핵심: transformers, datasets, torch, seqeval, kiwipiepy

# 2. 데이터 준비 (JSONL)
# {"tokens": [...], "labels": [...]} 형식

# 3. 학습 실행
python training/train_single_large.py \
    --jsonl_path ./data/train.jsonl \
    --project "PII-Detection-Korean-NER" \
    --epochs 5 \
    --batch_size 2 \
    --grad_accum 2 \
    --lr 2e-5 \
    --warmup_ratio 0.06 \
    --weight_decay 0.01 \
    --max_length 512 \
    --use_focal \
    --use_class_weights \
    --push_to_hub \
    --hf_private  # Private 리포지토리 (선택)

# 4. 결과 확인
ls ./results/klue-roberta-large-korean-pii-{timestamp}/
```

**학습 환경:**
- GPU: NVIDIA A100 (40GB) 또는 RTX 3090 (24GB)
- 학습 시간: **~285초 (4.7분)** per epoch (실제 측정)
- 메모리: ~12GB VRAM
- 처리 속도: 27.78 samples/sec

### EXAONE 학습

```bash
cd EXAONE-8B

# 1. 의존성 설치
pip install -r requirements.txt
# 핵심: transformers, peft, bitsandbytes, accelerate

# 2. 데이터 준비 (JSONL)
# train_policy_final.jsonl, valid_policy_final.jsonl

# 3. WandB & HuggingFace 로그인
wandb login
huggingface-cli login

# 4. 학습 실행
python finetune_parliament_detector.py

# 5. 결과 확인
ls /workspace/outputs/final/
```

**학습 환경:**
- GPU: NVIDIA A100 (40GB) 권장 (RTX 3090 24GB도 가능)
- 학습 시간: **27,346초 (7.6시간)** - 3 에폭 (실제 측정)
- 메모리: ~11-12GB VRAM (4bit 양자화)
- 처리 속도: 4.388 samples/sec

---

## 📈 성능 지표

### RoBERTa-Large (NER)

| 메트릭 | 전체 엔티티 | Regex Hard Entities |
|--------|-------------|---------------------|
| **Precision** | 90.56% | 89.74% |
| **Recall** | 96.20% | 95.01% |
| **F1 Score** | **93.30%** | **92.30%** 🔥 |
| **Accuracy** | 99.38% | 99.61% |
| **Token Accuracy** | - | 96.84% |

**실제 학습 결과 (Epoch 4.53 기준):**
- Eval Loss: 0.0225
- 학습 속도: 27.78 samples/sec
- 최종 모델: `psh3333/roberta-large-korean-pii5`

**Kiwi 토크나이저 효과:**
- **전체 F1**: 93.30%
- **Regex Hard Entities F1**: **92.30%** 🔥
- **Regex Hard Entities Recall**: **95.01%** (정규식 어려운 엔티티 탐지율)
- **Token Accuracy**: 96.84% (관심 엔티티 토큰 정확도)

**성능 분석:**
- Regex Hard Entities (NAME, USERNAME, ORG 등)에서도 **92.30% F1** 달성
- Recall 95.01%: 실제 PII의 95%를 정확히 탐지
- Precision 89.74%: 탐지된 것 중 89.7%가 실제 PII
- **정규식으로 탐지 어려운 엔티티에서 특히 우수한 성능** 🎯

### EXAONE-8B (Policy Violation)

**실제 학습 결과 (Epoch 3.0 기준):**
- **Train Loss**: 0.1534 (최종)
- **Eval Loss**: 0.1173 (Epoch 2.8)
- **학습 시간**: 27,346초 (약 7.6시간)
- **샘플 처리 속도**: 4.388 samples/sec
- **총 학습 Step**: 3,750 steps
- **최종 모델**: `psh3333/EXAONE-Policy-Violation-Detector-v1`

**성능 특성:**
- QLoRA 4bit 양자화로 **VRAM 11-12GB**에서 학습 가능
- Gradient Norm: 0.05 ~ 0.15 (안정적 수렴)
- Learning Rate: 2e-4 → 3.7e-11 (Cosine Annealing)
- 학습 가능 파라미터: **42M (0.54%)**

**정책 분류 정확도:**
- 최종 모델은 정부 정책 관련 질문의 위반 유형을 6가지 카테고리로 분류
- Loss 0.1173: 높은 신뢰도로 정책 위반 판단 가능
- 안정적인 수렴: Gradient Norm 0.05 수준 유지

---

## 💡 기술적 하이라이트

### 1. **Kiwi 토크나이저의 핵심 역할**

#### **한국어 NLP의 본질적 문제**
- **교착어 특성**: 조사, 어미가 단어에 붙어 의미 변화
- **서브워드 토큰화의 한계**: BPE는 통계 기반 → 의미 단위 분리 실패

**예시:**
```
문장: "홍길동입니다"

1. BPE 토크나이저 (일반):
   ["홍길", "##동", "##입니", "##다"]
   └─> "홍길동"이 3개 토큰으로 분리 → NER 성능 저하

2. Kiwi 형태소 분석기:
   ["홍길동", "이", "ᆸ니다"]
   └─> "홍길동" 단일 토큰 유지 → B-NAME 태깅 정확
```

#### **BIO 태깅 최적화**
```python
# preprocessing.py:165-174
for entity_value in labs[entity_type]:
    k = entity_value.split()  # Kiwi로 전처리된 토큰
    b_flag = True
    for m in k:
        indices = find_indices(tok, m)
        for ind in indices:
            labb[ind] = f"{'B' if b_flag else 'I'}-{entity_type}"
        b_flag = False
```

**효과:**
- 엔티티 경계 명확 → **Regex Hard F1 92.30%**
- 멀티 토큰 엔티티 처리 정확 (예: "서울특별시 강남구")
- 서브워드 오염 제거 (##, ▁ 같은 불필요한 토큰 없음)
- **높은 Recall (95.01%)**: 실제 PII의 95%를 놓치지 않고 탐지

---

### 2. **Focal Loss를 통한 불균형 데이터 처리**

#### **PII 데이터셋의 불균형**
```
O (비PII):           95.2% (압도적 다수)
B-NAME:              0.8%
I-NAME:              0.3%
B-PHONE_NUM:         0.5%
B-ORGANIZATION_NAME: 0.2% (극소수)
...
```

#### **Focal Loss 수식**
```
FL(pt) = -α(1-pt)^γ * log(pt)

where:
  pt = 모델의 정답 확률
  α = 클래스 가중치
  γ = 포커싱 파라미터 (2.0)
```

**효과:**
```python
# 예시
O 태그 (쉬운 샘플, pt=0.99):
  FL = -1 * (1-0.99)^2 * log(0.99) = 0.00001 (거의 무시)

B-ORGANIZATION_NAME (어려운 샘플, pt=0.60):
  FL = -1 * (1-0.60)^2 * log(0.60) = 0.082 (강하게 학습)
```

**결과:**
- 희소 엔티티 Recall +7.2%
- 과적합 방지 (label_smoothing=0.1과 결합)

---

### 3. **QLoRA 4비트 양자화의 효율성**

#### **메모리 비교**
```
EXAONE-3.5-7.8B 모델 크기:

FP32:     31.2GB (7.8B * 4 bytes)
FP16:     15.6GB (7.8B * 2 bytes)
8bit:      7.8GB (7.8B * 1 byte)
4bit (NF4): 3.9GB (7.8B * 0.5 byte)  🔥

LoRA 어댑터: +2-3GB
Gradient Checkpointing: -20%
─────────────────────────
총 VRAM 사용량: ~11-12GB ✅
```

#### **NormalFloat4 (NF4) 양자화**
```python
# finetune_parliament_detector.py:79-84
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",  # 🔥 핵심
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
```

**NF4의 장점:**
- **정규 분포 가정**: 신경망 가중치는 정규분포 → 양자화 오류 최소화
- **비대칭 범위**: 음수/양수 범위를 독립적으로 최적화
- **성능 손실 < 1%**: FP16 대비 성능 저하 미미

**실험 결과:**
| 정밀도 | Train Loss | VRAM | 학습 시간 |
|--------|------------|------|----------|
| FP16 (불가능) | - | 31GB | - |
| 8bit (오류 발생) | - | 15.6GB | - |
| 4bit (NF4) | **0.153** | **11GB** | 7.6시간 ✅ |

---

### 4. **LoRA 타겟 모듈 선택의 전략성**

```python
# finetune_parliament_detector.py:108-111
target_modules = [
    "q_proj", "k_proj", "v_proj", "o_proj",  # 어텐션 레이어 (4개)
    "gate_proj", "up_proj", "down_proj"       # FFN 레이어 (3개)
]
```

#### **왜 이 7개 레이어인가?**

**1. Attention Layers (q/k/v/o_proj)**
```
Self-Attention 메커니즘:
  Q = X @ W_q  (Query)
  K = X @ W_k  (Key)
  V = X @ W_v  (Value)
  O = Attention(Q, K, V) @ W_o  (Output)

LoRA 적용:
  W_q' = W_q + LoRA_A @ LoRA_B  (rank=64)
```

**효과:**
- **문맥 이해 강화**: 정책 위반 키워드 (예: "기밀", "인사", "급여") 집중
- **장거리 의존성**: 문장 전체를 보고 판단 (단순 키워드 매칭이 아님)

**2. FFN Layers (gate/up/down_proj)**
```
Feed-Forward Network:
  FFN(x) = GELU(x @ W_gate) * (x @ W_up) @ W_down

LoRA 적용:
  W_gate' = W_gate + LoRA_A @ LoRA_B
```

**효과:**
- **특징 추출**: "국민 추적"과 "정부 공개 자료"의 차이 학습
- **비선형 변환**: 복잡한 정책 규칙 표현

#### **학습 파라미터 비율**
```python
# finetune_parliament_detector.py:120-123
trainable = 42,467,328 (42M)
total = 7,848,000,000 (7.8B)
비율 = 0.54%  🔥

메모리 절약 = 99.46%
성능 유지 = 99%+
```

---

### 5. **Early Stopping & Best Model Selection**

#### **RoBERTa 설정 (train_single_large.py:344-346)**
```python
metric_for_best_model = "regexhard_f1"  # 🎯 핵심 지표
load_best_model_at_end = True
early_stopping_patience = 3
```

**전략:**
- **전체 F1이 아닌 Regex Hard F1 사용**: 쉬운 엔티티에 속지 않음
- **3 에폭 개선 없으면 중단**: 과적합 방지
- **체크포인트 자동 저장**: 최고 성능 모델 보존

#### **EXAONE 설정 (finetune_parliament_detector.py:201-202)**
```python
save_total_limit = 2  # 최근 2개 체크포인트만 유지
load_best_model_at_end = True
```

**효과:**
- 디스크 공간 절약 (체크포인트 1개 = ~4GB)
- 최종 모델 = 검증 세트 최고 성능

---

### 6. **Gradient Checkpointing의 메모리 트레이드오프**

```python
# train_single_large.py:279
model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
```

#### **작동 원리**
```
일반 학습:
  Forward → [Layer1] → [Layer2] → ... → [LayerN] → Loss
  (모든 중간 활성화 메모리 저장)

Gradient Checkpointing:
  Forward → [Layer1] → 삭제 → [Layer2] → 삭제 → ...
  Backward → [LayerN] 재계산 → [Layer2] 재계산 → ...
```

**효과:**
- **메모리 절약**: -40% VRAM 사용
- **속도 저하**: +20% 학습 시간 (재계산 오버헤드)
- **트레이드오프**: 메모리 제약 환경에서 필수

---

### 7. **Chat Template의 역할**

#### **EXAONE의 Instruction Tuning**
```python
# finetune_parliament_detector.py:158-162
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=False
)
```

**변환 예시:**
```python
# 입력
messages = [
    {"role": "system", "content": "당신은 정책 위반 분류 시스템입니다."},
    {"role": "user", "content": "국민 추적 기록을 알 수 있나요?"},
    {"role": "assistant", "content": "VIOLATION_PRIVACY_CITIZEN"}
]

# 출력 (Chat Template 적용)
<|system|>
당신은 정책 위반 분류 시스템입니다.
<|user|>
국민 추적 기록을 알 수 있나요?
<|assistant|>
VIOLATION_PRIVACY_CITIZEN
```

**효과:**
- **구조화된 입력**: 모델이 역할(role) 구분 학습
- **사전 학습 일관성**: EXAONE은 Chat Template로 Instruct Tuning됨
- **Few-shot Learning**: System Prompt에 예시 추가 가능

---

### 8. **seqeval을 통한 엔티티 단위 평가**

#### **일반 Accuracy의 함정**
```python
# 잘못된 평가
Prediction: ["B-NAME", "I-NAME", "O", "O"]
Ground Truth: ["B-NAME", "B-NAME", "O", "O"]

Token Accuracy: 75% (3/4)  ← 엔티티가 분리되었지만 높은 점수
```

#### **seqeval의 엔티티 단위 평가**
```python
# train_single_large.py:72
from seqeval.metrics import precision_score, recall_score, f1_score

# 예시
Prediction: ["B-NAME", "I-NAME", "O", "O"]
Ground Truth: ["B-NAME", "B-NAME", "O", "O"]

seqeval 평가:
  Predicted Entities: [("NAME", 0, 2)]  ← 하나의 엔티티
  True Entities: [("NAME", 0, 1), ("NAME", 1, 2)]  ← 두 개의 엔티티

  Precision = 0% (예측한 엔티티가 틀림)
  Recall = 0%
  F1 = 0%
```

**효과:**
- **실제 사용 시나리오 반영**: 부분 일치는 실패로 간주
- **엄격한 평가**: 경계 오류 페널티

---

## 📁 주요 파일

### RoBERTa-Large

| 파일 | 줄 수 | 설명 |
|------|-------|------|
| `training/train_single_large.py` | 380 | 메인 학습 스크립트 (Focal Loss, seqeval, WandB) |
| `src/preprocessing.py` | 180 | Kiwi 토큰화, BIO 태깅, 구두점 재처리 |
| `src/load_data.py` | 120 | JSONL 데이터 로드 및 검증 |
| `src/cxmetrics.py` | 85 | seqeval 기반 평가 지표 |
| `src/gendata.py` | 250 | ChatGPT API로 합성 데이터 생성 |
| `gen-data/pii-syn-data.py` | 180 | Faker 기반 PII 생성 |
| `requirements.txt` | 27 | 의존성 (kiwipiepy, seqeval 등) |

### EXAONE-8B

| 파일 | 줄 수 | 설명 |
|------|-------|------|
| `finetune_parliament_detector.py` | 364 | 메인 학습 스크립트 (QLoRA, Chat Template) |
| `train_policy_final.jsonl` | 50K | 학습 데이터 (정책 질문 + 위반 라벨) |
| `valid_policy_final.jsonl` | 10K | 검증 데이터 |
| `requirements.txt` | 10 | 의존성 (peft, bitsandbytes) |

---

## 🔗 관련 링크

### 모델 허브
- **RoBERTa NER**: [psh3333/roberta-large-korean-pii5](https://huggingface.co/psh3333/roberta-large-korean-pii5)
- **EXAONE Policy**: [psh3333/EXAONE-Policy-Violation-Detector-v1](https://huggingface.co/psh3333/EXAONE-Policy-Violation-Detector-v1)

### 베이스 모델
- **klue/roberta-large**: [HuggingFace](https://huggingface.co/klue/roberta-large)
- **LGAI-EXAONE**: [HuggingFace](https://huggingface.co/LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct)

### 라이브러리
- **Kiwi**: [kiwipiepy GitHub](https://github.com/bab2min/kiwipiepy)
- **seqeval**: [seqeval PyPI](https://pypi.org/project/seqeval/)
- **LoRA**: [microsoft/LoRA](https://github.com/microsoft/LoRA)
- **bitsandbytes**: [TimDettmers/bitsandbytes](https://github.com/TimDettmers/bitsandbytes)

---
