from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'some_revision_id'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None


def upgrade():
    # Здесь вы добавляете команды для изменения схемы базы данных
    op.add_column('your_table', sa.Column('new_column', sa.String(length=50), nullable=True))


def downgrade():
    # Все изменения, которые необходимо отменить
    op.drop_column('your_table', 'new_column')
