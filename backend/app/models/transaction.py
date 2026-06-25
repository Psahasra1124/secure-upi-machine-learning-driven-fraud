from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    transaction_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    merchant_category: Mapped[str] = mapped_column(String(80), index=True)
    device_type: Mapped[str] = mapped_column(String(40), index=True)
    location: Mapped[str] = mapped_column(String(120), index=True)
    transaction_frequency: Mapped[int] = mapped_column(Integer)
    is_fraud: Mapped[bool] = mapped_column(Boolean, index=True)
    fraud_probability: Mapped[float] = mapped_column(Float)
    explanation: Mapped[list] = mapped_column(JSON, default=list)
    model_version: Mapped[str] = mapped_column(String(80), default="fallback")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )

    user = relationship("User", back_populates="transactions")
    prediction_log = relationship(
        "PredictionLog", back_populates="transaction", uselist=False, cascade="all, delete-orphan"
    )

