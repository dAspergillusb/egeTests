"""Initial informatics database schema.

Revision ID: informatics_0001
Revises:
Create Date: 2026-09-17
"""

from alembic import op
import sqlalchemy as sa

revision = "informatics_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "informatics_main",
        sa.Column("q_id", sa.Integer(), primary_key=True),
        sa.Column("q_number", sa.Integer(), nullable=False),
        sa.Column("q_school_class", sa.String(), nullable=False),
        sa.Column("q_text", sa.String(), nullable=False),
        sa.Column("q_difficulty", sa.String(), nullable=False),
        sa.Column("q_files", sa.String(), nullable=False),
        sa.Column("q_right_answer", sa.String(), nullable=False),
        sa.Column("q_linked_with", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("informatics_main")
