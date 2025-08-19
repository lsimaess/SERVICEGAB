"""Split phone into country code and number

Revision ID: 8440a11e8e1a
Revises: f8aec8f9b361
Create Date: 2025-08-15 18:36:26.098547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8440a11e8e1a'
down_revision = 'f8aec8f9b361'
branch_labels = None
depends_on = None


def upgrade():
    # Split phone field in requester
    with op.batch_alter_table('requester', schema=None) as batch_op:
        batch_op.add_column(sa.Column('country_code', sa.String(length=6), nullable=False, server_default='+241'))
        batch_op.add_column(sa.Column('phone_number', sa.String(length=20), nullable=False, server_default='00000000'))
        batch_op.drop_column('phone')

    # Split phone field in worker
    with op.batch_alter_table('worker', schema=None) as batch_op:
        batch_op.add_column(sa.Column('country_code', sa.String(length=6), nullable=False, server_default='+241'))
        batch_op.add_column(sa.Column('phone_number', sa.String(length=20), nullable=False, server_default='00000000'))
        batch_op.drop_column('phone')


def downgrade():
    # Restore old phone field for worker
    with op.batch_alter_table('worker', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone', sa.VARCHAR(length=50), nullable=False))
        batch_op.drop_column('phone_number')
        batch_op.drop_column('country_code')

    # Restore old phone field for requester
    with op.batch_alter_table('requester', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone', sa.VARCHAR(length=50), nullable=False))
        batch_op.drop_column('phone_number')
        batch_op.drop_column('country_code')
