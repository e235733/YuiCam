"""empty message

Revision ID: a640d44d3276
Revises: 
Create Date: 2024-07-25 18:47:27.502803

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a640d44d3276'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('faculty', sa.Integer(), nullable=False),
    sa.Column('univ_year', sa.Integer(), nullable=False),
    sa.Column('bio', sa.String(length=160), nullable=True),
    sa.Column('profile_picture', sa.LargeBinary(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('like',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('liker_id', sa.Integer(), nullable=False),
    sa.Column('liked_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['liked_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['liker_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('match',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user1_id', sa.Integer(), nullable=False),
    sa.Column('user2_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user1_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user2_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('match')
    op.drop_table('like')
    op.drop_table('user')
    # ### end Alembic commands ###
