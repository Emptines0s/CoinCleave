"""empty message

Revision ID: f3a857a1190f
Revises: aea219b1a438
Create Date: 2022-11-06 19:02:51.883893

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f3a857a1190f'
down_revision = 'aea219b1a438'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('candlestick',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bot_id', sa.Integer(), nullable=True),
    sa.Column('datetime', sa.DateTime(), nullable=True),
    sa.Column('open', sa.String(length=20), nullable=True),
    sa.Column('high', sa.String(length=20), nullable=True),
    sa.Column('low', sa.String(length=20), nullable=True),
    sa.Column('close', sa.String(length=20), nullable=True),
    sa.Column('volume', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['bot_id'], ['bot.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('celery_tasksetmeta')
    op.drop_table('celery_taskmeta')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('celery_taskmeta',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('task_id', sa.VARCHAR(length=155), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('result', postgresql.BYTEA(), autoincrement=False, nullable=True),
    sa.Column('date_done', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('traceback', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=155), autoincrement=False, nullable=True),
    sa.Column('args', postgresql.BYTEA(), autoincrement=False, nullable=True),
    sa.Column('kwargs', postgresql.BYTEA(), autoincrement=False, nullable=True),
    sa.Column('worker', sa.VARCHAR(length=155), autoincrement=False, nullable=True),
    sa.Column('retries', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('queue', sa.VARCHAR(length=155), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='celery_taskmeta_pkey'),
    sa.UniqueConstraint('task_id', name='celery_taskmeta_task_id_key')
    )
    op.create_table('celery_tasksetmeta',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('taskset_id', sa.VARCHAR(length=155), autoincrement=False, nullable=True),
    sa.Column('result', postgresql.BYTEA(), autoincrement=False, nullable=True),
    sa.Column('date_done', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='celery_tasksetmeta_pkey'),
    sa.UniqueConstraint('taskset_id', name='celery_tasksetmeta_taskset_id_key')
    )
    op.drop_table('candlestick')
    # ### end Alembic commands ###
