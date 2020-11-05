"""empty message

Revision ID: a57f966fc869
Revises: ca640bef716a
Create Date: 2020-11-04 20:19:19.374525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a57f966fc869'
down_revision = 'ca640bef716a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('seeking_description', sa.String(), nullable=True))
    op.add_column('artists', sa.Column('seeking_venue', sa.Boolean(), nullable=False))
    op.add_column('artists', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artists', 'website')
    op.drop_column('artists', 'seeking_venue')
    op.drop_column('artists', 'seeking_description')
    # ### end Alembic commands ###
