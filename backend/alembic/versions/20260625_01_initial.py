"""Initial Secure UPI schema."""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260625_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_role", "users", ["role"])
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("transaction_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("merchant_category", sa.String(80), nullable=False),
        sa.Column("device_type", sa.String(40), nullable=False),
        sa.Column("location", sa.String(120), nullable=False),
        sa.Column("transaction_frequency", sa.Integer(), nullable=False),
        sa.Column("is_fraud", sa.Boolean(), nullable=False),
        sa.Column("fraud_probability", sa.Float(), nullable=False),
        sa.Column("explanation", sa.JSON(), nullable=False),
        sa.Column("model_version", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_transaction_time", "transactions", ["transaction_time"])
    op.create_index("ix_transactions_is_fraud", "transactions", ["is_fraud"])
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"])
    op.create_table(
        "prediction_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "transaction_id",
            sa.Integer(),
            sa.ForeignKey("transactions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("probability", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(80), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_prediction_logs_user_id", "prediction_logs", ["user_id"])
    op.create_index("ix_prediction_logs_transaction_id", "prediction_logs", ["transaction_id"])
    op.create_index("ix_prediction_logs_created_at", "prediction_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("prediction_logs")
    op.drop_table("transactions")
    op.drop_table("users")

