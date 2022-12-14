"""empty message

Revision ID: d909842ed880
Revises: c972c34ede04
Create Date: 2022-11-17 22:52:12.796364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd909842ed880'
down_revision = 'c972c34ede04'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('candlestick', sa.Column('symbol', sa.String(length=8), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('candlestick', 'symbol')
    # ### end Alembic commands ###
