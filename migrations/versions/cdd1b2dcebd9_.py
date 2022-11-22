"""empty message

Revision ID: cdd1b2dcebd9
Revises: 78c8196d9416
Create Date: 2022-10-26 09:12:00.796727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdd1b2dcebd9'
down_revision = '78c8196d9416'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('strategy', sa.Column('interval', sa.String(length=3), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('strategy', 'interval')
    # ### end Alembic commands ###
