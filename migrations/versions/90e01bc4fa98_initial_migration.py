"""initial migration

Revision ID: 90e01bc4fa98
Revises: 
Create Date: 2023-12-09 13:18:53.055349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90e01bc4fa98'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('log_entry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=120), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('request', sa.Text(), nullable=True),
    sa.Column('response', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('log_entry', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_log_entry_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_log_entry_timestamp'), ['timestamp'], unique=False)
        batch_op.create_index(batch_op.f('ix_log_entry_user_id'), ['user_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('log_entry', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_log_entry_user_id'))
        batch_op.drop_index(batch_op.f('ix_log_entry_timestamp'))
        batch_op.drop_index(batch_op.f('ix_log_entry_status'))

    op.drop_table('log_entry')
    # ### end Alembic commands ###
