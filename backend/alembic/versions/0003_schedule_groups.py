"""schedule room/lamp groups

Revision ID: 0003
Revises: 0002
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE schedulescope ADD VALUE IF NOT EXISTS 'rooms_group'")
    op.execute("ALTER TYPE schedulescope ADD VALUE IF NOT EXISTS 'lamps_group'")
    op.add_column("lamp_schedules", sa.Column("room_ids", postgresql.ARRAY(sa.Integer()), nullable=True))
    op.add_column("lamp_schedules", sa.Column("lamp_ids", postgresql.ARRAY(sa.Integer()), nullable=True))


def downgrade() -> None:
    op.drop_column("lamp_schedules", "lamp_ids")
    op.drop_column("lamp_schedules", "room_ids")
