from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TransactionInput(BaseModel):
    amount: float = Field(gt=0, le=10_000_000)
    time: datetime
    merchant_category: str = Field(min_length=2, max_length=80)
    device_type: str = Field(min_length=2, max_length=40)
    location: str = Field(min_length=2, max_length=120)
    transaction_frequency: int = Field(ge=0, le=10_000)


class ExplanationItem(BaseModel):
    feature: str
    impact: float
    direction: str


class PredictionResponse(BaseModel):
    transaction_id: int
    prediction: str
    is_fraud: bool
    probability: float
    threshold: float
    explanation: list[ExplanationItem]
    model_version: str


class TransactionRead(BaseModel):
    id: int
    user_id: int
    amount: float
    transaction_time: datetime
    merchant_category: str
    device_type: str
    location: str
    transaction_frequency: int
    is_fraud: bool
    fraud_probability: float
    explanation: list[dict]
    model_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedTransactions(BaseModel):
    items: list[TransactionRead]
    total: int
    page: int
    page_size: int
    pages: int

