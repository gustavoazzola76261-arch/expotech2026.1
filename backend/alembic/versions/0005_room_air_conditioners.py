"""room air conditioners (1 per room)

Revision ID: 0005
Revises: 0004
"""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "room_air_conditioners",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("is_on", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("target_temp_c", sa.Integer(), server_default="23", nullable=False),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_id", name="uq_room_air_conditioners_room_id"),
    )
    op.execute(
        sa.text(
            "INSERT INTO room_air_conditioners (room_id, is_on, target_temp_c) "
            "SELECT id, false, 23 FROM rooms"
        )
    )


def downgrade() -> None:
    op.drop_table("room_air_conditioners")
