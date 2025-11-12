#!/usr/bin/env python3
"""
종합 분석 메시지 포맷팅 및 백엔드 연동 테스트
"""

from response import ResponseGenerator
from backend import backend_client

# 제공된 API 응답 데이터
test_data = {
    "input_text": "공공 부문 리포트 (기밀: 외교 및 국가 안보 정보)\n[리포트] 동맹국 간 사이버 보안 정보 교환을 위한 보안 채널 구축 방안 \n작성자: {박현우}\n\n이메일: {hwpark@moef.go.kr}\n\n소속: {대한민국 기획재정부}\n\n1. 개요\n사이버 공격이 고도화되며, 동맹국과 실시간 위협 정보를 교환하는 것이 국가 안보의 핵심이 되었습니다. 그러나 이 과정에서 대한민국의 민감한 정보가 유출될 위험이 있습니다. 본 리포트는 안전한 정보 교환을 위한 보안 프로토콜 수립을 제안합니다.\n\n2. 기밀 보호 전략\n동맹국과 정보를 공유할 때, 국가 안보 기밀을 보호하기 위한 방법은 다음과 같습니다.\n\n- 전용 보안 통신망 구축: 암호화된 전용 회선을 통해 해킹과 감청을 차단합니다.\n- 정보 공유 등급 및 'Need-to-Know' 원칙: 정보를 최소한으로 공유하고, 필요한 사람에게만 접근을 허용합니다.\n- TLP(교차색 신호 프로토콜) 적용: 정보의 민감도에 따라 공유 범위를 구분합니다.\n\n3. 결론\n사이버 위협 정보 교환을 위한 표준 보안 프로토콜이 필요하며, '쿼드(Quad)' 국가들 간 실무 협의를 시작할 것을 제안합니다.\n\n보고자: 박현우 드림",
    "input_hash": "e3d60172560b783b94254fddcb7d697f6685313229e607c726abcc489498cd88",
    "blocked": True,
    "block_reasons": [
        "pii_detected",
        "similarity_detected"
    ],
    "analysis_time_ms": 354,
    "pii_analysis": {
        "has_pii": True,
        "threshold": 0.9,
        "entities": [
            {
                "type": "NAME",
                "value": "박현우",
                "confidence": 0.9973056614398956,
                "token_count": 2
            },
            {
                "type": "EMAIL",
                "value": "hwpark@moef.go.kr",
                "confidence": 0.9994219094514847,
                "token_count": 12
            },
            {
                "type": "NAME",
                "value": "박현우",
                "confidence": 0.9967585206031799,
                "token_count": 2
            }
        ],
        "total_entities": 3,
        "reason": "개인정보 3개 탐지됨 (EMAIL, NAME), 유사 문서 1개 탐지됨 ('공공 분야', 85.5%)",
        "details": "탐지된 개인정보: NAME '박현우' (신뢰도: 99.7%), EMAIL 'hwpark@moef.go.kr' (신뢰도: 99.9%), NAME '박현우' (신뢰도: 99.7%). 임계값 이상 유사 문서: '공공 분야' (85.5%)."
    },
    "similarity_analysis": {
        "is_similar": True,
        "max_similarity": 0.85510136,
        "threshold": 0.85,
        "matched_count": 1,
        "total_found_count": 3,
        "matched_documents": [
            {
                "document_id": "f48865eb-1609-4d54-995b-743eed1405ef",
                "document_title": "공공 분야",
                "max_similarity": 0.85510136,
                "matched_chunks_count": 3,
                "matched_texts": [
                    {
                        "content": "공공 분야 보고서 (기밀: 외교 및 국가 안보 정보) [보고서] 동맹국과의 사이버 안보 위협 정보 공유 를 위한 보안 채널 구축 방안 작성자: {박현우} 이메일: {hwpark@moef.go.kr} 소속: {대한민국 기획재정부} 비밀번호: {Ntnl_ScrtY#2025} 1. 개요 국가 기반 시설을 위협하는 사이버 공격이 고도화됨에 따라, 동맹국과의 실시간...",
                        "similarity": 0.85510136,
                        "similarity_percentage": "85.5%",
                        "chunk_index": 0
                    },
                    {
                        "content": "전용 보안 통신망(Encrypted Network) 구축: 일반 상용 인터넷망과 물리적으로 분리된 양국 간 암호화 전용 회선을 구축하여, 해킹 및 감청 위협을 원천적으로 차단한 보안 채널을 통해서만 정보를 유통합니다. 정보 공유 등급 및 'Need-to-Know' 원칙 적용: 공유되는 모든 정보는 '대외비', '비밀', '극비' 등급으로 분류하고, 열람 대...",
                        "similarity": 0.71863455,
                        "similarity_percentage": "71.9%",
                        "chunk_index": 1
                    },
                    {
                        "content": "3. 결론 및 제언 신속한 정보 공유와 철저한 보안은 동전의 양면과 같습니다. APEC, G20 등 다자 안보 협의체에서 사이버 위협 정보 공유를 위한 표준 보안 프로토콜을 의제화하고, 우선적으로 '쿼드(Quad)' 참여국과 양자 간 보안 채널 구축을 위한 실무 협의를 개시할 것을 제언합니다. 보고자: 박현우 드림",
                        "similarity": 0.5738376000000001,
                        "similarity_percentage": "57.4%",
                        "chunk_index": 2
                    }
                ]
            }
        ]
    }
}

if __name__ == "__main__":
    print("=== 종합 분석 API 테스트 ===")
    
    # 1. 포맷팅 함수 테스트
    print("\n1. 메시지 포맷팅 테스트")
    formatted_message = ResponseGenerator.format_comprehensive_analysis_message(test_data)
    print("--- 차단 메시지 ---")
    print(formatted_message)
    print()
    
    # 승인 사례도 테스트
    approved_data = {
        "blocked": False,
        "block_reasons": []
    }
    
    approved_message = ResponseGenerator.format_comprehensive_analysis_message(approved_data)
    print("--- 승인 메시지 ---")
    print(approved_message)
    print()
    
    # 2. 백엔드 API 테스트 (백엔드가 실행 중일 때만)
    print("2. 백엔드 API 연결 테스트")
    if backend_client.health_check():
        print("✅ 백엔드 연결 성공")
        
        # 종합 분석 테스트
        test_prompt = "안녕하세요. 저는 홍길동이고 이메일은 hong@example.com입니다."
        should_block, reason, details = backend_client.comprehensive_analysis(
            prompt=test_prompt,
            files_data=[],
            metadata={}
        )
        
        print(f"테스트 프롬프트: {test_prompt}")
        print(f"차단 여부: {should_block}")
        print(f"사유: {reason}")
        if details and "message" in details:
            print(f"메시지:\n{details['message']}")
            
    else:
        print("❌ 백엔드 연결 실패")
        print("   - 백엔드 서버가 실행 중인지 확인하세요")
        print(f"   - 백엔드 URL: {backend_client.base_url}")
        print(f"   - 종합 분석 엔드포인트: {backend_client.base_url}/api/v1/analyze/comprehensive")
    
    print("\n=== 테스트 완료 ===")