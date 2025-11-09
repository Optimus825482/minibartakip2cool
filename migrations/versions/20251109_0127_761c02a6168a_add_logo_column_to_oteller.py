"""add_logo_column_to_oteller

Revision ID: 761c02a6168a
Revises: 8c28dcd8e1ca
Create Date: 2025-11-09 01:27:54.465642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '761c02a6168a'
down_revision = '8c28dcd8e1ca'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Logo kolonunu ekle (Text tipinde, nullable)
    op.add_column('oteller', sa.Column('logo', sa.Text(), nullable=True))


def downgrade() -> None:
    # Logo kolonunu kaldır
    op.drop_column('oteller', 'logo')
