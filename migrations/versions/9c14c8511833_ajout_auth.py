"""ajout auth

Revision ID: 9c14c8511833
Revises: db4ca2b7b39c
Create Date: 2025-03-21 09:27:36.500148

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision = '9c14c8511833'
down_revision = 'db4ca2b7b39c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', mssql.DATETIMEOFFSET(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('updated_at', mssql.DATETIMEOFFSET(), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
