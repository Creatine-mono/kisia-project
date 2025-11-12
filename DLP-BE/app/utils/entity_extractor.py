from typing import Any
import re
from transformers import AutoTokenizer

def extract_bio_entities(
    predictions: list[dict[str, Any]],
    tokenizer: AutoTokenizer | None = None,
    original_text: str = ""
) -> list[dict[str, Any]]:
    """
    BIO 태그 예측 결과에서 엔티티를 추출
    
    Args:
        predictions: 토큰별 예측 결과 [{"token": str, "label": str, "confidence": float}]
        tokenizer: 토큰을 문자열로 변환하기 위한 토크나이저
        original_text: 원본 텍스트 (위치 정보 계산용)
    
    Returns:
        List of entities: [{"type": str, "value": str, "confidence": float, "token_count": int}]
    """
    entities = []
    current_entity = None
    
    for i, pred in enumerate(predictions):
        label = pred["label"]
        token = pred["token"]
        confidence = pred["confidence"]
        
        # O 태그나 UNKNOWN 태그는 무시
        if label in ["O", "UNKNOWN", "UNK"] or not label:
            if current_entity:
                entities.append(_finalize_entity(current_entity, tokenizer))
                current_entity = None
            continue
        
        if label.startswith("B-"):
            # 새로운 엔티티 시작
            entity_type = label[2:]  # B- 제거
            
            # 현재 엔티티와 같은 타입의 B- 태그가 연속으로 나오는 경우 합치기
            if (current_entity and 
                current_entity["type"] == entity_type and 
                _is_consecutive_tokens(current_entity, pred, predictions, i)):
                # 연속된 같은 타입이면 합치기
                current_entity["tokens"].append(token)
                current_entity["confidences"].append(confidence)
                current_entity["positions"].append(pred.get("position", i))
            else:
                # 다른 타입이거나 연속되지 않은 경우 새로운 엔티티 시작
                if current_entity:
                    entities.append(_finalize_entity(current_entity, tokenizer))
                
                current_entity = {
                    "type": entity_type,
                    "tokens": [token],
                    "confidences": [confidence],
                    "start_idx": i,
                    "positions": [pred.get("position", i)]
                }
            
        elif label.startswith("I-"):
            # 기존 엔티티 확장
            entity_type = label[2:]  # I- 제거
            
            if current_entity and current_entity["type"] == entity_type:
                # 같은 타입의 엔티티라면 확장
                current_entity["tokens"].append(token)
                current_entity["confidences"].append(confidence)
                current_entity["positions"].append(pred.get("position", i))
            else:
                # 타입이 다르거나 current_entity가 없다면 새로 시작
                if current_entity:
                    entities.append(_finalize_entity(current_entity, tokenizer))
                
                current_entity = {
                    "type": entity_type,
                    "tokens": [token],
                    "confidences": [confidence],
                    "start_idx": i,
                    "positions": [pred.get("position", i)]
                }
        else:
            # 완전히 다른 형태의 태그 (BIO가 아닌 경우)
            if current_entity:
                entities.append(_finalize_entity(current_entity, tokenizer))
                current_entity = None
            
            # 단독 엔티티로 처리
            entities.append({
                "type": label,
                "value": _clean_token_value([token], tokenizer, label),
                "confidence": confidence,
                "token_count": 1
            })
    
    # 마지막 엔티티 처리
    if current_entity:
        entities.append(_finalize_entity(current_entity, tokenizer))
    
    return entities

def _is_consecutive_tokens(current_entity: dict[str, Any], pred: dict[str, Any],
                          predictions: list[dict[str, Any]], current_idx: int) -> bool:
    """
    현재 토큰이 기존 엔티티와 연속된 토큰인지 확인
    단순히 위치 인덱스가 연속되는지만 확인
    """
    if not current_entity or not current_entity.get("positions"):
        return False
    
    last_position = current_entity["positions"][-1]
    current_position = pred.get("position", current_idx)
    
    # 위치가 연속되는지 확인 (1 차이)
    return current_position == last_position + 1

def _finalize_entity(entity: dict[str, Any], tokenizer: AutoTokenizer | None = None) -> dict[str, Any]:
    """엔티티 정보 완성"""
    tokens = entity["tokens"]
    entity_type = entity["type"]

    # 토큰들을 문자열로 변환
    value = _clean_token_value(tokens, tokenizer, entity_type)

    # 평균 신뢰도 계산
    avg_confidence = sum(entity["confidences"]) / len(entity["confidences"])

    return {
        "type": entity_type,
        "value": value,
        "confidence": avg_confidence,
        "token_count": len(tokens)
    }

def _clean_token_value(tokens: list[str], tokenizer: AutoTokenizer | None = None, entity_type: str = "") -> str:
    """
    토큰들을 깔끔한 문자열로 변환
    
    Args:
        tokens: 토큰 리스트
        tokenizer: 토크나이저 (있으면 convert_tokens_to_string 사용)
        entity_type: 엔티티 타입 (정리 방식 결정용)
    
    Returns:
        정리된 문자열
    """
    if not tokens:
        return ""
    
    if tokenizer:
        try:
            # 특수 토큰 필터링
            clean_tokens = []
            for token in tokens:
                # RoBERTa 토크나이저의 특수 토큰들 제거
                if token.startswith('[') and token.endswith(']'):
                    continue  # [CLS], [SEP], [PAD] 등 제거
                clean_tokens.append(token)
            
            if clean_tokens:
                # 토크나이저를 사용해서 올바른 문자열 복원
                value = tokenizer.convert_tokens_to_string(clean_tokens)
            else:
                value = ""
        except Exception:
            # 토크나이저 오류 시 폴백
            value = "".join(tokens).replace("##", "")
    else:
        # 토크나이저가 없는 경우 수동 처리
        value = "".join(tokens).replace("##", "")
    
    # 타입별 후처리
    value = _post_process_by_type(value, entity_type)
    
    return value.strip()

def _post_process_by_type(value: str, entity_type: str) -> str:
    """엔티티 타입에 따른 후처리"""
    
    # 전화번호, 카드번호 등 숫자 기반 정보
    if entity_type.upper() in ["PHONE", "PHONE_NUM", "CREDIT_CARD", "CARD", "ID_NUM", "SSN"]:
        # 불필요한 공백 제거, 하이픈은 유지
        value = value.replace(" ", "")
        # 연속된 하이픈 정리
        value = re.sub(r'-+', '-', value)
        
    # 이름, 주소 등 텍스트 기반 정보  
    elif entity_type.upper() in ["PERSON", "NAME", "ADDRESS", "LOCATION", "ORG", "ORGANIZATION"]:
        # 단어 간 공백은 하나로 통일
        value = re.sub(r'\s+', ' ', value)
        
    # 이메일
    elif entity_type.upper() in ["EMAIL", "MAIL"]:
        # 공백 완전 제거
        value = value.replace(" ", "")
        
    # URL
    elif entity_type.upper() in ["URL", "WEBSITE", "LINK"]:
        # 공백 완전 제거
        value = value.replace(" ", "")
    
    return value

# 역호환성을 위한 함수들
def has_pii_entities(entities: list[dict[str, Any]]) -> bool:
    """PII 엔티티가 존재하는지 확인"""
    return len(entities) > 0

def get_entity_types(entities: list[dict[str, Any]]) -> list[str]:
    """탐지된 엔티티 타입들 반환"""
    return list(set(entity["type"] for entity in entities))

def get_entity_count_by_type(entities: list[dict[str, Any]]) -> dict[str, int]:
    """타입별 엔티티 개수 반환"""
    count_dict = {}
    for entity in entities:
        entity_type = entity["type"]
        count_dict[entity_type] = count_dict.get(entity_type, 0) + 1
    return count_dict