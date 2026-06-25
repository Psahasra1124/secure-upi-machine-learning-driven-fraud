from pydantic import BaseModel


class Summary(BaseModel):
    total_transactions: int
    fraudulent_transactions: int
    legitimate_transactions: int
    fraud_percentage: float
    total_amount: float
    blocked_amount: float


class ChartPoint(BaseModel):
    label: str
    total: int
    fraud: int


class CategoryPoint(BaseModel):
    category: str
    total: int
    fraud: int

