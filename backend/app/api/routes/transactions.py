import csv
import io
import math
from datetime import datetime

from fastapi import APIRouter, Query, Response
from sqlalchemy import func, or_, select

from app.api.deps import CurrentUser, DbSession
from app.models import Transaction
from app.schemas.transaction import PaginatedTransactions

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def scoped_query(current_user: CurrentUser):
    query = select(Transaction)
    if current_user.role != "admin":
        query = query.where(Transaction.user_id == current_user.id)
    return query


def apply_filters(query, search, fraud, start_date, end_date):
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(
            or_(
                Transaction.merchant_category.ilike(pattern),
                Transaction.device_type.ilike(pattern),
                Transaction.location.ilike(pattern),
            )
        )
    if fraud is not None:
        query = query.where(Transaction.is_fraud == fraud)
    if start_date:
        query = query.where(Transaction.transaction_time >= start_date)
    if end_date:
        query = query.where(Transaction.transaction_time <= end_date)
    return query


@router.get("", response_model=PaginatedTransactions)
def list_transactions(
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    fraud: bool | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> PaginatedTransactions:
    filtered = apply_filters(
        scoped_query(current_user), search, fraud, start_date, end_date
    )
    total = db.scalar(select(func.count()).select_from(filtered.subquery())) or 0
    rows = db.scalars(
        filtered.order_by(Transaction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PaginatedTransactions(
        items=list(rows),
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/export.csv")
def export_transactions(
    db: DbSession,
    current_user: CurrentUser,
    search: str | None = None,
    fraud: bool | None = None,
) -> Response:
    query = apply_filters(scoped_query(current_user), search, fraud, None, None)
    rows = db.scalars(query.order_by(Transaction.created_at.desc())).all()
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(
        [
            "id",
            "time",
            "amount",
            "merchant_category",
            "device_type",
            "location",
            "transaction_frequency",
            "prediction",
            "probability",
            "model_version",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row.id,
                row.transaction_time.isoformat(),
                row.amount,
                row.merchant_category,
                row.device_type,
                row.location,
                row.transaction_frequency,
                "Fraud" if row.is_fraud else "Not Fraud",
                row.fraud_probability,
                row.model_version,
            ]
        )
    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=secure-upi-report.csv"},
    )

