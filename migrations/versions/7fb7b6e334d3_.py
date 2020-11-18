"""empty message

Revision ID: 7fb7b6e334d3
Revises: fcba09f478b1
Create Date: 2020-11-17 20:54:00.368875

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fb7b6e334d3'
down_revision = 'fcba09f478b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('show_venue_id_fkey', 'show', type_='foreignkey')
    op.drop_constraint('show_artist_id_fkey', 'show', type_='foreignkey')
    op.create_foreign_key(None, 'show', 'artist', ['artist_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'show', 'venue', ['venue_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'show', type_='foreignkey')
    op.drop_constraint(None, 'show', type_='foreignkey')
    op.create_foreign_key('show_artist_id_fkey', 'show', 'artist', ['artist_id'], ['id'])
    op.create_foreign_key('show_venue_id_fkey', 'show', 'venue', ['venue_id'], ['id'])
    # ### end Alembic commands ###
