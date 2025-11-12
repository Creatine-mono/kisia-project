"""PII 탐지 직접 테스트"""
import asyncio
from app.ai.pii_detector import RobertaKoreanPIIDetector

async def test():
    print("Loading model...")
    detector = RobertaKoreanPIIDetector()
    print("Model loaded!")
    
    text = "내 이름은 이선욱이야"
    print(f"\n테스트 텍스트: {text}")
    
    print("\n추론 시작...")
    result = await detector.detect_pii(text)
    
    print(f"\n결과:")
    print(f"  has_pii: {result['has_pii']}")
    print(f"  entities: {result['entities']}")
    print(f"\n원시 예측 (처음 10개):")
    for pred in result['raw_predictions'][:10]:
        print(f"    {pred}")

if __name__ == "__main__":
    asyncio.run(test())
