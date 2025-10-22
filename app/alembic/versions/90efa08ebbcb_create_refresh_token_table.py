"""create refresh_token table

Revision ID: 90efa08ebbcb
Revises: 2962e3d0bc06
Create Date: 2025-10-22 15:51:41.672394

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "90efa08ebbcb"
down_revision: Union[str, Sequence[str], None] = "2962e3d0bc06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "refresh_token",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "account_id", sa.BigInteger, sa.ForeignKey("account.id"), nullable=False
        ),
        sa.Column("token_hash", sa.Text, nullable=False, unique=True),
        sa.Column(
            "issued_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("absolute_expires_at", sa.DateTime, nullable=True),
        sa.Column("revoked_at", sa.DateTime, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("refresh_token")
