"""Initial archive database schema.

Revision ID: archive_0001
Revises:
Create Date: 2026-09-17
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "archive_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "archive_databases",
        sa.Column("ad_id", sa.Integer(), primary_key=True),
        sa.Column("history_type", sa.String(), nullable=False),
        sa.Column("main_db_name", postgresql.JSONB(), nullable=False),
        sa.Column("db_structure", postgresql.JSONB(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("archive_databases")
