# Secure UPI API

Base URL: `/api/v1`

Interactive OpenAPI documentation is available at `/docs`, with ReDoc at
`/redoc`. Except for registration and login, endpoints require
`Authorization: Bearer <JWT>`.

## Authentication

- `POST /auth/register` — JSON body: `full_name`, `email`, `password`.
- `POST /auth/login` — form body: `username` (email), `password`.
- `GET /auth/me` — current user profile.

Registration always creates a `user` account. The administrator is provisioned
from `ADMIN_EMAIL` and `ADMIN_PASSWORD`; this prevents public role escalation.

## Prediction

`POST /predictions`

```json
{
  "amount": 6500,
  "time": "2026-06-25T01:20:00+05:30",
  "merchant_category": "gaming",
  "device_type": "emulator",
  "location": "Mumbai",
  "transaction_frequency": 14
}
```

Response:

```json
{
  "transaction_id": 42,
  "prediction": "Fraud",
  "is_fraud": true,
  "probability": 0.91,
  "threshold": 0.5,
  "explanation": [
    {
      "feature": "Device Type Emulator",
      "impact": 1.42,
      "direction": "increases risk"
    }
  ],
  "model_version": "xgboost-20260625143000"
}
```

Every prediction atomically creates a `transactions` row and a
`prediction_logs` audit row.

## Transactions

- `GET /transactions` — paginated history. Query: `page`, `page_size`,
  `search`, `fraud`, `start_date`, `end_date`.
- `GET /transactions/export.csv` — filtered CSV report.

Administrators see all transactions. Users see only their own.

## Analytics

- `GET /analytics/summary`
- `GET /analytics/trend?days=14`
- `GET /analytics/categories`

## Administration

- `GET /admin/users` — administrator-only user list.

## System

- `GET /health` — service, environment, and model readiness.

Common errors use FastAPI's standard `{"detail": "..."}` response shape.

