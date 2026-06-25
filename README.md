# Secure UPI

Machine Learning-Driven Fraud Detection System for UPI Transactions

Secure UPI is a full-stack fraud-intelligence platform that scores payment
context in real time, records an auditable transaction trail, and explains
model decisions with SHAP. It includes JWT authentication, role-based data
access, an operations dashboard, CSV reporting, PostgreSQL persistence, and a
reproducible training pipeline.

## Architecture

```text
React + Tailwind + Recharts
           |
       Nginx / REST
           |
FastAPI -- JWT/RBAC -- PostgreSQL
   |
Preprocessor + selected classifier
   |
Logistic Regression / Random Forest / XGBoost
   |
SMOTE training + SHAP explanations
```

## Features

- User registration, login, JWT sessions, and protected routes
- Admin and user roles with row-level transaction scoping
- Total, fraud, legitimate, fraud-rate, processed-value, and exposure metrics
- Interactive time-series and merchant-category charts
- Searchable/filterable history with server-side pagination
- CSV report export
- Real-time prediction endpoint and feature-level explanations
- Comparison of Logistic Regression, Random Forest, and XGBoost
- Leakage-safe preprocessing and SMOTE on training data only
- PostgreSQL schema, Alembic migration, health checks, and Docker deployment
- Automatic local heuristic fallback when no trained artifact exists
- Swagger UI at `/docs` and ReDoc at `/redoc`

## Repository layout

```text
frontend/    React/Vite UI, Tailwind components, charts, protected routing
backend/     FastAPI API, SQLAlchemy models, auth, services, tests, Alembic
ml/          Dataset adapter, sample generator, training and model artifacts
database/    PostgreSQL schema
docker/      Production container definitions and Nginx configuration
docs/        API reference
```

## One-command Docker run

1. Copy `.env.example` to `.env`.
2. Replace `SECRET_KEY`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD`.
3. Optionally train a model first (see the ML section).
4. Start the stack:

```bash
docker compose up --build
```

Open:

- Application: <http://localhost:3000>
- Swagger API: <http://localhost:3000/docs>
- Health: <http://localhost:3000/health>

PostgreSQL data is stored in the `postgres_data` Docker volume. The backend
creates the configured administrator if it does not exist.

## Local development

### Backend

Python 3.11 or 3.12 is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

Without a `DATABASE_URL`, local development uses `backend/secure_upi.db`
(SQLite). Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL for parity with
production.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI defaults to `http://localhost:8000/api/v1`. Override this with
`VITE_API_URL`.

## Train the fraud model

Generate a reproducible demo dataset and train:

```bash
cd ml
python generate_sample_data.py --rows 20000
python train.py --data data/sample_upi_transactions.csv
```

The trainer:

1. stratifies train/test data;
2. imputes and scales numeric fields;
3. imputes and one-hot encodes categorical fields;
4. applies SMOTE only to transformed training data;
5. trains Logistic Regression, Random Forest, and XGBoost;
6. compares average precision, ROC-AUC, precision, recall, and F1;
7. saves the best model and metadata under `ml/artifacts/`.

For the public ULB/Kaggle Credit Card Fraud Detection dataset, download
`creditcard.csv` and run:

```bash
python train.py --data data/creditcard.csv
```

The dataset adapter maps `Time`, `Amount`, and `Class` to the product contract
and deterministically supplies contextual fields. See [ml/README.md](ml/README.md).
For a production deployment, train on institution-approved UPI data with the
native contextual columns and establish drift, fairness, threshold, and
human-review policies before allowing automatic declines.

## Configuration

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | JWT signing key | development-only value |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT lifetime | `60` |
| `DATABASE_URL` | SQLAlchemy connection URL | local SQLite |
| `CORS_ORIGINS` | Comma-separated browser origins | `localhost:5173` |
| `MODEL_PATH` | Joblib model artifact | `ml/artifacts/fraud_model.joblib` |
| `MODEL_METADATA_PATH` | Training metadata JSON | beside model |
| `ADMIN_EMAIL` | Bootstrapped admin account | `admin@secureupi.com` |
| `ADMIN_PASSWORD` | Bootstrapped admin password | must be changed |
| `VITE_API_URL` | Browser API base URL | `localhost:8000/api/v1` |

## Database and migrations

The canonical PostgreSQL DDL is in `database/schema.sql`. Alembic is included
for controlled changes:

```bash
cd backend
alembic upgrade head
```

The three core tables are:

- `users` — identity, password hash, role, status
- `transactions` — normalized transaction context and model decision
- `prediction_logs` — immutable scoring input, explanation, and model version

## Tests and quality checks

```bash
cd backend
pytest -q

cd ../frontend
npm run lint
npm run build
```

## Security notes

- Passwords use Argon2 through `pwdlib`; plaintext passwords are never stored.
- Self-registration cannot request an admin role.
- API authorization scopes every user query; admin-only routes use a separate
  dependency.
- Prediction inputs are validated with bounded Pydantic fields.
- Production deployments must use a randomly generated secret, TLS, restricted
  CORS origins, managed database credentials, rate limiting, centralized logs,
  backup/restore procedures, and secret management.
- SHAP explains the model, not ground truth. Explanations should support—not
  replace—fraud analyst review.

Detailed endpoint documentation is in [docs/API.md](docs/API.md).
