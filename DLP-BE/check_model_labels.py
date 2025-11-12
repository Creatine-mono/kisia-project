"""모델이 사용하는 라벨 확인"""
from transformers import AutoModelForTokenClassification

model_name = "psh3333/roberta-large-korean-pii5"
model = AutoModelForTokenClassification.from_pretrained(model_name)

print("모델이 사용하는 라벨:")
print(model.config.id2label)
