from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.models import PredictionLog, Transaction
from app.schemas.transaction import PredictionResponse, TransactionInput
from app.services.ml_service import predictor

router = APIRouter(prefix="/predictions", tags=["Fraud Prediction"])


@router.post("", response_model=PredictionResponse)
def predict_transaction(
    payload: TransactionInput, db: DbSession, current_user: CurrentUser
) -> PredictionResponse:
    payload_dict = payload.model_dump()
    result = predictor.predict(payload_dict)
    transaction = Transaction(
        user_id=current_user.id,
        amount=payload.amount,
        transaction_time=payload.time,
        merchant_category=payload.merchant_category.strip().lower(),
        device_type=payload.device_type.strip().lower(),
        location=payload.location.strip(),
        transaction_frequency=payload.transaction_frequency,
        is_fraud=result["is_fraud"],
        fraud_probability=result["probability"],
        explanation=result["explanation"],
        model_version=result["model_version"],
    )
    db.add(transaction)
    db.flush()
    db.add(
        PredictionLog(
            user_id=current_user.id,
            transaction_id=transaction.id,
            probability=result["probability"],
            model_version=result["model_version"],
            input_payload={
                **payload_dict,
                "time": payload.time.isoformat(),
            },
            explanation=result["explanation"],
        )
    )
    db.commit()
    db.refresh(transaction)
    return PredictionResponse(
        transaction_id=transaction.id,
        prediction="Fraud" if result["is_fraud"] else "Not Fraud",
        **result,
    )

