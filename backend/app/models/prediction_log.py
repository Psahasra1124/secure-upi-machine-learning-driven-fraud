from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"), unique=True, index=True
    )
    probability: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(80))
    input_payload: Mapped[dict] = mapped_column(JSON)
    explanation: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )

    user = relationship("User", back_populates="prediction_logs")
    transaction = relationship("Transaction", back_populates="prediction_log")

