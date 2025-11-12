# app/util/tag_parser.py
import re
from typing import List, Tuple, Dict

# [B-LABEL] / [I-LABEL]
TAG = re.compile(r"\[(B|I)-([A-Z_]+)\]")

def canonical_label(label: str) -> str:
    # 예: NAME_STUDENT -> NAME 로 정규화 (요구 라벨셋과 샘플 불일치 보정)
    if label.startswith("NAME"):
        return "NAME"
    return label

def extract_entities(tagged: str) -> Tuple[str, List[Dict]]:
    """
    태그 포함 문자열 -> (cleaned_text, entities)
    entities: {label, value, start, end} (cleaned_text 기준)
    - 토큰 앞/뒤 어디에나 태그가 붙어도 동작하도록 2패스 처리
    """
    # 1) 클린 텍스트 (태그 제거)
    cleaned = TAG.sub("", tagged)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

    # 2) 엔티티 토큰 시퀀스 추출
    #   뒤태그:  token [B-LABEL]
    trailing = re.findall(r"([^\s\[\]]+)\s*\[(B|I)-([A-Z_]+)\]", tagged)
    #   앞태그:  [B-LABEL] token
    leading = re.findall(r"\[(B|I)-([A-Z_]+)\]\s*([^\s\[\]]+)", tagged)

    # 토큰 시퀀스 만들기: [(order, BIO, label, token)]
    seq: List[Tuple[int, str, str, str]] = []
    for m in TAG.finditer(tagged):
        pos = m.start()

    # trailing 매칭
    for token, bio, label in trailing:
        seq.append((1, bio, canonical_label(label), token))
    # leading 매칭
    for bio, label, token in leading:
        seq.append((2, bio, canonical_label(label), token))

    # 시퀀스를 정렬(앞/뒤 우선 순위로 충돌 완화)
    seq.sort(key=lambda x: x[0])

    # 3) B/I 묶어 값 합치기
    entities_tokens: List[Tuple[str, List[str]]] = []  # (label, [tokens...])
    cur_label = None
    cur_tokens: List[str] = []
    for _, bio, label, token in seq:
        if bio == "B" or label != cur_label:
            if cur_label and cur_tokens:
                entities_tokens.append((cur_label, cur_tokens))
            cur_label = label
            cur_tokens = [token]
        else:  # I
            cur_tokens.append(token)
    if cur_label and cur_tokens:
        entities_tokens.append((cur_label, cur_tokens))

    # 4) cleaned_text 내에서 각 value의 start/end 탐색 (중복 완화 위해 점진적 탐색)
    entities = []
    search_from = 0
    for label, toks in entities_tokens:
        value = "".join(toks) if label in {"PHONE_NUM", "ID_NUM", "CREDIT_CARD_INFO"} else " ".join(toks)
        pat = re.escape(value)
        m = re.search(pat, cleaned[search_from:])
        if not m:
            # 공백/기호 변형 완화 시도
            alt = re.sub(r"\s+", r"\\s*", pat)
            m = re.search(alt, cleaned[search_from:])
        if m:
            start = search_from + m.start()
            end = start + (m.end() - m.start())
            entities.append({"label": label, "value": cleaned[start:end], "start": start, "end": end})
            search_from = end
    return cleaned, entities

def format_ner_text(original_text: str, ner_results: List[Dict]) -> str:
    """
    NER 결과를 원본 텍스트에 라벨과 함께 삽입하여 자연스러운 형태로 변환
    
    Args:
        original_text (str): 원본 텍스트
        ner_results (List[Dict]): NER 파이프라인 결과 [{'entity', 'start', 'end', ...}]
        
    Returns:
        str: 라벨이 삽입된 텍스트 "홍길동<PII:B-NAME>" 형태
    """
    if not ner_results:
        return original_text
    
    # start 위치 기준으로 정렬 (뒤에서부터 삽입하기 위해 역순)
    sorted_results = sorted(ner_results, key=lambda x: x['start'], reverse=True)
    
    formatted_text = original_text
    
    for entity in sorted_results:
        start = entity['start']
        end = entity['end']
        entity_type = entity['entity']
        
        # 원본 단어 추출
        original_word = formatted_text[start:end]
        
        # 라벨과 함께 새로운 형태로 변환
        labeled_word = f"{original_word}<PII:{entity_type}>"
        
        # 텍스트에서 해당 부분을 교체
        formatted_text = formatted_text[:start] + labeled_word + formatted_text[end:]
    
    return formatted_text