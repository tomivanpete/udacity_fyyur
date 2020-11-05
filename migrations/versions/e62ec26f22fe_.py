"""empty message

Revision ID: e62ec26f22fe
Revises: ef8d4de433eb
Create Date: 2020-11-04 19:45:04.422339

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e62ec26f22fe'
down_revision = 'ef8d4de433eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.execute('UPDATE venues SET seeking_talent = FALSE WHERE seeking_talent IS NULL;')
    op.alter_column('venues', 'seeking_talent', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'seeking_talent')
    # ### end Alembic commands ###