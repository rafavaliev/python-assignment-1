"""init tables

Revision ID: 261ea2959558
Revises: 
Create Date: 2022-12-23 01:16:24.115243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '261ea2959558'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'patient',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('external_id', sa.Integer, nullable=False),
        sa.Column('age', sa.Integer, nullable=False),
    )


def downgrade():
    op.drop_table('patient')

