"""Initial users database schema.

Revision ID: users_0001
Revises:
Create Date: 2026-09-17
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "users_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), primary_key=True),
        sa.Column("firstname", sa.String(), nullable=False),
        sa.Column("lastname", sa.String(), nullable=False),
        sa.Column("sex", sa.String(), nullable=False),
        sa.Column("school_class", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False, unique=True),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("rank", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "users_statistics",
        sa.Column("us_id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=False),
        *[
            sa.Column(f"q_type_{number}", sa.String(), nullable=False)
            for number in range(1, 28)
        ],
    )

    op.create_table(
        "users_sessions",
        sa.Column("session_id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("session_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expire_date", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "daily_statistics",
        sa.Column("ds_id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("test", sa.String(), nullable=False),
        sa.Column("result", sa.String(), nullable=False),
        sa.Column("date", sa.String(), nullable=False),
        sa.Column("test_time", sa.Integer(), nullable=False),
        sa.Column("problem_type_intervals", postgresql.JSONB(), nullable=False),
        sa.Column("easy_accuracy", sa.Float(), nullable=False),
        sa.Column("programming_accuracy", sa.Float(), nullable=False),
        sa.Column("hard_accuracy", sa.Float(), nullable=False),
        sa.Column("final_result", sa.Integer(), nullable=False),
    )

    op.create_table(
        "active_students_test",
        sa.Column("ast_id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column(
            "session_id",
            sa.String(),
            sa.ForeignKey("users_sessions.session_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_time", sa.Integer(), nullable=False),
        sa.Column("stop_time", sa.Integer(), nullable=False),
        sa.Column("test", postgresql.JSONB(), nullable=False),
        sa.Column("answers", postgresql.JSONB(), nullable=False),
        sa.Column("problem_type_intervals", postgresql.JSONB(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("active_students_test")
    op.drop_table("daily_statistics")
    op.drop_table("users_sessions")
    op.drop_table("users_statistics")
    op.drop_table("users")
