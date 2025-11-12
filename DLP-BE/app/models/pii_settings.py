"""
PII Settings 모델
"""
from sqlalchemy import String, Boolean, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class PIISettings(Base):
    """PII 탐지 설정 모델 - 엔티티 타입별 활성화 및 민감도 설정"""
    __tablename__ = "pii_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    entity_type: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="PII 엔티티 타입 (PERSON, PHONE_NUM, EMAIL 등)"
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="탐지 활성화 여부"
    )
    threshold: Mapped[int] = mapped_column(
        Integer,
        default=59,
        nullable=False,
        comment="탐지 민감도 (0-100, 이 값 이상일 때만 탐지)"
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="PII 타입 설명"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<PIISettings(type={self.entity_type}, enabled={self.enabled}, threshold={self.threshold})>"