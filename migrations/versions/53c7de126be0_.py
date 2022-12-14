"""empty message

Revision ID: 53c7de126be0
Revises: 48a3dff112c1
Create Date: 2022-11-12 11:03:25.149946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53c7de126be0'
down_revision = '48a3dff112c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscription', sa.Column('name', sa.String(length=10), nullable=True))
    op.add_column('subscription', sa.Column('purchase_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subscription', 'purchase_time')
    op.drop_column('subscription', 'name')
    # ### end Alembic commands ###
