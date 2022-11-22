"""empty message

Revision ID: 48a3dff112c1
Revises: 303cb3992e79
Create Date: 2022-11-12 10:49:45.015981

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '48a3dff112c1'
down_revision = '303cb3992e79'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('celery_taskmeta')
    op.drop_table('celery_tasksetmeta')
    op.add_column('subscription', sa.Column('status', sa.String(length=10), nullable=True))
    op.drop_column('subscription', 'grade')
    op.drop_column('subscription', 'priority')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscription', sa.Column('priority', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('subscription', sa.Column('grade', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.drop_column('subscription', 'status')
    op.create_table('celery_tasksetmeta',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('taskset_id', sa.VARCHAR(length=155), autoincrement=False, nullable=True),
    sa.Column('result', postgresql.BYTEA(), autoincrement=False, nullable=True),
    sa.Column('date_done', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='celery_tasksetmeta_pkey'),
    sa.UniqueConstraint('taskset_id', name='celery_tasksetmeta_taskset_id_key')
    )
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
    # ### end Alembic commands ###
