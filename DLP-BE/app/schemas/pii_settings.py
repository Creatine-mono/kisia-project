"""
PII Settings 스키마 정의
"""
from pydantic import BaseModel, Field
from datetime import datetime


class PIISettingBase(BaseModel):
    """PII 설정 기본 스키마"""
    entity_type: str = Field(..., description="PII 엔티티 타입 (PERSON, PHONE_NUM 등)")
    enabled: bool = Field(..., description="탐지 활성화 여부")
    threshold: int = Field(..., description="탐지 민감도 (0-100)", ge=0, le=100)
    description: str | None = Field(None, description="PII 타입 설명")


class PIISettingResponse(PIISettingBase):
    """PII 설정 조회 응답"""
    id: int = Field(..., description="설정 ID")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "entity_type": "PERSON",
                    "enabled": True,
                    "threshold": 59,
                    "description": "사람 이름 (예: 홍길동, John Doe)",
                    "created_at": "2025-11-04T01:00:00Z",
                    "updated_at": "2025-11-04T01:00:00Z"
                }
            ]
        }
    }


class PIISettingUpdate(BaseModel):
    """PII 설정 업데이트 요청"""
    enabled: bool | None = Field(None, description="탐지 활성화 여부")
    threshold: int | None = Field(None, description="탐지 민감도 (0-100)", ge=0, le=100)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "enabled": False
                },
                {
                    "threshold": 80
                },
                {
                    "enabled": True,
                    "threshold": 75
                }
            ]
        }
    }


class PIISettingsListResponse(BaseModel):
    """PII 설정 목록 응답"""
    settings: list[PIISettingResponse] = Field(..., description="PII 설정 목록")
    total: int = Field(..., description="전체 설정 개수")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "settings": [
                        {
                            "id": 1,
                            "entity_type": "PERSON",
                            "enabled": True,
                            "threshold": 59,
                            "description": "사람 이름",
                            "created_at": "2025-11-04T01:00:00Z",
                            "updated_at": "2025-11-04T01:00:00Z"
                        }
                    ],
                    "total": 10
                }
            ]
        }
    }