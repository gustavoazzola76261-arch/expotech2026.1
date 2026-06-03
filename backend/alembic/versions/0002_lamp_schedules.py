"""lamp schedules

Revision ID: 0002
Revises: 7a3d57024e18
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "7a3d57024e18"
branch_labels = None
depends_on = None

schedule_scope_type = postgresql.ENUM("all", "room", "lamp", name="schedulescope", create_type=False)
lamp_action_type = postgresql.ENUM("on", "off", name="lampaction", create_type=False)


def upgrade() -> None:
    # Create enum explicitly once; column types use create_type=False to avoid duplicate DDL.
    postgresql.ENUM("all", "room", "lamp", name="schedulescope").create(
        op.get_bind(), checkfirst=True
    )
    op.create_table(
        "lamp_schedules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("scope", schedule_scope_type, nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=True),
        sa.Column("lamp_id", sa.Integer(), nullable=True),
        sa.Column("action", lamp_action_type, nullable=False),
        sa.Column("hour", sa.Integer(), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lamp_id"], ["lamps.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("lamp_schedules")
    postgresql.ENUM("all", "room", "lamp", name="schedulescope").drop(
        op.get_bind(), checkfirst=True
    )
