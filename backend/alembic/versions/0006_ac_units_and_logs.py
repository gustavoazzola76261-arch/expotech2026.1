"""multiple AC units per room, power tracking, actuation logs

Revision ID: 0006
Revises: 0005
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

DEFAULT_AC_POWER_W = 1500
# Reutiliza o ENUM já criado em actuation_logs / lamp_schedules (não chamar .create()).
lamp_action_type = postgresql.ENUM("on", "off", name="lampaction", create_type=False)


def upgrade() -> None:
    op.add_column("room_air_conditioners", sa.Column("slot", sa.Integer(), nullable=True))
    op.add_column("room_air_conditioners", sa.Column("name", sa.String(length=255), nullable=True))
    op.add_column(
        "room_air_conditioners",
        sa.Column("power_watts", sa.Integer(), server_default=str(DEFAULT_AC_POWER_W), nullable=False),
    )
    op.add_column(
        "room_air_conditioners",
        sa.Column("last_on_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.execute(
        sa.text(
            "UPDATE room_air_conditioners SET slot = 1, name = 'Ar 1' "
            "WHERE slot IS NULL"
        )
    )

    op.alter_column("room_air_conditioners", "slot", nullable=False)
    op.alter_column("room_air_conditioners", "name", nullable=False)

    op.drop_constraint("uq_room_air_conditioners_room_id", "room_air_conditioners", type_="unique")

    op.create_table(
        "ac_actuation_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("air_conditioner_id", sa.Integer(), nullable=False),
        sa.Column("action", lamp_action_type, nullable=False),
        sa.Column("energy_kwh", sa.Numeric(12, 6), nullable=True),
        sa.ForeignKeyConstraint(["air_conditioner_id"], ["room_air_conditioners.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ac_actuation_logs_created_at", "ac_actuation_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_ac_actuation_logs_created_at", table_name="ac_actuation_logs")
    op.drop_table("ac_actuation_logs")

    op.create_unique_constraint(
        "uq_room_air_conditioners_room_id", "room_air_conditioners", ["room_id"]
    )

    op.drop_column("room_air_conditioners", "last_on_at")
    op.drop_column("room_air_conditioners", "power_watts")
    op.drop_column("room_air_conditioners", "name")
    op.drop_column("room_air_conditioners", "slot")
