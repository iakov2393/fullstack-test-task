"""cascade delete on alerts + indexes for sort/lookup columns

Revision ID: 70b476ea5266
Revises: 0d6439d2e79f
Create Date: 2026-07-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70b476ea5266'
down_revision: Union[str, Sequence[str], None] = '0d6439d2e79f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Fixes a real bug: deleting a file that already has alerts (i.e. any
    # file that finished processing) used to fail with a FK violation,
    # because the FK had no ON DELETE behaviour defined.
    op.drop_constraint('alerts_file_id_fkey', 'alerts', type_='foreignkey')
    op.create_foreign_key(
        'alerts_file_id_fkey', 'alerts', 'files', ['file_id'], ['id'], ondelete='CASCADE',
    )

    # Non-obvious optimization: Postgres does NOT automatically index
    # foreign key columns (unlike primary/unique keys), so lookups and the
    # cascade delete above would do a full scan of "alerts" without this.
    op.create_index('ix_alerts_file_id', 'alerts', ['file_id'])

    # Every listing endpoint orders by created_at; without an index that's
    # a full sort on every request as the tables grow.
    op.create_index('ix_alerts_created_at', 'alerts', ['created_at'])
    op.create_index('ix_files_created_at', 'files', ['created_at'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_files_created_at', table_name='files')
    op.drop_index('ix_alerts_created_at', table_name='alerts')
    op.drop_index('ix_alerts_file_id', table_name='alerts')

    op.drop_constraint('alerts_file_id_fkey', 'alerts', type_='foreignkey')
    op.create_foreign_key('alerts_file_id_fkey', 'alerts', 'files', ['file_id'], ['id'])
