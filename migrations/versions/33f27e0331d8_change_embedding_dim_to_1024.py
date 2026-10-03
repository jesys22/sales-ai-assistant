"""change embedding dim to 1024

Revision ID: 33f27e0331d8
Revises: e12846f2762e
Create Date: 2026-10-03 16:50:56.292383

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "33f27e0331d8"
down_revision: Union[str, Sequence[str], None] = "e12846f2762e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Таблица documents пустая — безопасно дропнуть и создать колонку заново.
    op.execute("ALTER TABLE documents DROP COLUMN IF EXISTS embedding")
    op.execute("ALTER TABLE documents ADD COLUMN embedding vector(1024) NOT NULL")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE documents DROP COLUMN IF EXISTS embedding")
    op.execute("ALTER TABLE documents ADD COLUMN embedding vector(1536) NOT NULL")