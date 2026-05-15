"""schedule weekdays + IA persisted state

Revision ID: 0004
Revises: 0003
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lamp_schedules",
        sa.Column("days_of_week", postgresql.ARRAY(sa.Integer()), nullable=True),
    )
    op.create_table(
        "campus_ia_state",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("operation_context", sa.Text(), nullable=True),
        sa.Column("last_insights", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("last_generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(sa.text("INSERT INTO campus_ia_state (id) VALUES (1)"))


def downgrade() -> None:
    op.drop_table("campus_ia_state")
    op.drop_column("lamp_schedules", "days_of_week")
