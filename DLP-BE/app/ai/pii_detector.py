# app/ai/pii_detector.py
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from app.utils.entity_extractor import extract_bio_entities, has_pii_entities

class RobertaKoreanPIIDetector:
    """
    한국어 PII 탐지를 위한 RoBERTa 모델
    psh3333/roberta-large-korean-pii3 모델 사용
    """
    
    def __init__(self):
        self.model_name = "psh3333/roberta-large-korean-pii5"
        self.tokenizer: AutoTokenizer | None = None
        self.model: AutoModelForTokenClassification | None = None
        self._load_model()
    
    def _load_model(self):
        """모델과 토크나이저 로드"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_name)
            self.model.eval()
        except Exception as e:
            raise RuntimeError(f"Failed to load PII detection model: {str(e)}")
    
    async def detect_pii(self, text: str) -> dict[str, any]:
        """
        텍스트에서 PII 탐지

        Returns:
            Dict containing:
            - has_pii: bool
            - entities: List of detected PII entities
            - raw_predictions: Raw model predictions
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("PII detection model not loaded")

        # CPU intensive한 모델 추론을 별도 스레드에서 실행
        import asyncio
        predictions = await asyncio.to_thread(self._predict_tokens_sync, text)

        # 새로운 엔티티 추출 함수 사용
        entities = extract_bio_entities(predictions, self.tokenizer, text)

        # PII 존재 여부 확인
        has_pii = has_pii_entities(entities)

        return {
            "has_pii": has_pii,
            "entities": entities,
            "raw_predictions": predictions
        }

    def _predict_tokens_sync(self, text: str) -> list[dict[str, any]]:
        """토큰별 PII 라벨 예측 (동기 함수)"""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_classes = predictions.argmax(-1)

        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        predictions_list = predicted_classes[0].tolist()

        results = []
        for i, (token, prediction) in enumerate(zip(tokens, predictions_list)):
            if token in ["[CLS]", "[SEP]", "[PAD]"]:
                continue

            label = self.model.config.id2label[prediction]
            confidence = float(predictions[0][i][prediction])

            results.append({
                "token": token,
                "label": label,
                "confidence": confidence,
                "position": i
            })

        return results