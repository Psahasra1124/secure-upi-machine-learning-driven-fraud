from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Query
from sqlalchemy import case, func, select

from app.api.deps import CurrentUser, DbSession
from app.models import Transaction
from app.schemas.analytics import CategoryPoint, ChartPoint, Summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def scope(statement, current_user: CurrentUser):
    if current_user.role != "admin":
        statement = statement.where(Transaction.user_id == current_user.id)
    return statement


@router.get("/summary", response_model=Summary)
def summary(db: DbSession, current_user: CurrentUser) -> Summary:
    statement = select(
        func.count(Transaction.id),
        func.coalesce(func.sum(case((Transaction.is_fraud, 1), else_=0)), 0),
        func.coalesce(func.sum(Transaction.amount), 0.0),
        func.coalesce(
            func.sum(case((Transaction.is_fraud, Transaction.amount), else_=0.0)), 0.0
        ),
    )
    total, fraud, total_amount, blocked_amount = db.execute(scope(statement, current_user)).one()
    return Summary(
        total_transactions=total,
        fraudulent_transactions=fraud,
        legitimate_transactions=total - fraud,
        fraud_percentage=round((fraud / total * 100) if total else 0, 2),
        total_amount=round(float(total_amount), 2),
        blocked_amount=round(float(blocked_amount), 2),
    )


@router.get("/trend", response_model=list[ChartPoint])
def trend(
    db: DbSession,
    current_user: CurrentUser,
    days: int = Query(7, ge=1, le=90),
) -> list[ChartPoint]:
    start = datetime.now(UTC) - timedelta(days=days - 1)
    statement = (
        select(
            func.date(Transaction.transaction_time).label("day"),
            func.count(Transaction.id),
            func.coalesce(func.sum(case((Transaction.is_fraud, 1), else_=0)), 0),
        )
        .where(Transaction.transaction_time >= start)
        .group_by(func.date(Transaction.transaction_time))
        .order_by(func.date(Transaction.transaction_time))
    )
    rows = db.execute(scope(statement, current_user)).all()
    by_day = {str(day): (total, fraud) for day, total, fraud in rows}
    return [
        ChartPoint(
            label=(start + timedelta(days=index)).date().isoformat(),
            total=by_day.get((start + timedelta(days=index)).date().isoformat(), (0, 0))[0],
            fraud=by_day.get((start + timedelta(days=index)).date().isoformat(), (0, 0))[1],
        )
        for index in range(days)
    ]


@router.get("/categories", response_model=list[CategoryPoint])
def categories(db: DbSession, current_user: CurrentUser) -> list[CategoryPoint]:
    statement = (
        select(
            Transaction.merchant_category,
            func.count(Transaction.id),
            func.coalesce(func.sum(case((Transaction.is_fraud, 1), else_=0)), 0),
        )
        .group_by(Transaction.merchant_category)
        .order_by(func.count(Transaction.id).desc())
        .limit(10)
    )
    return [
        CategoryPoint(category=category, total=total, fraud=fraud)
        for category, total, fraud in db.execute(scope(statement, current_user)).all()
    ]

