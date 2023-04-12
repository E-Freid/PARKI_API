"""empty message

Revision ID: ee74491abc16
Revises: 
Create Date: 2023-04-10 16:31:53.204782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee74491abc16'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('parkings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('park_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('address', sa.String(length=100), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('park_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('parkings')
    # ### end Alembic commands ###