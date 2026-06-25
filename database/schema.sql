CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DOUBLE PRECISION NOT NULL CHECK (amount > 0),
    transaction_time TIMESTAMPTZ NOT NULL,
    merchant_category VARCHAR(80) NOT NULL,
    device_type VARCHAR(40) NOT NULL,
    location VARCHAR(120) NOT NULL,
    transaction_frequency INTEGER NOT NULL CHECK (transaction_frequency >= 0),
    is_fraud BOOLEAN NOT NULL,
    fraud_probability DOUBLE PRECISION NOT NULL CHECK (
        fraud_probability >= 0 AND fraud_probability <= 1
    ),
    explanation JSONB NOT NULL DEFAULT '[]'::jsonb,
    model_version VARCHAR(80) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prediction_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id BIGINT NOT NULL UNIQUE REFERENCES transactions(id) ON DELETE CASCADE,
    probability DOUBLE PRECISION NOT NULL,
    model_version VARCHAR(80) NOT NULL,
    input_payload JSONB NOT NULL,
    explanation JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);
CREATE INDEX IF NOT EXISTS ix_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS ix_transactions_time ON transactions(transaction_time DESC);
CREATE INDEX IF NOT EXISTS ix_transactions_fraud ON transactions(is_fraud);
CREATE INDEX IF NOT EXISTS ix_transactions_category ON transactions(merchant_category);
CREATE INDEX IF NOT EXISTS ix_prediction_logs_user_id ON prediction_logs(user_id);
CREATE INDEX IF NOT EXISTS ix_prediction_logs_created_at ON prediction_logs(created_at DESC);

