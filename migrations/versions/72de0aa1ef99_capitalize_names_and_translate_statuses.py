"""Capitalize names and translate statuses"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '72de0aa1ef99'
down_revision = 'eb770f9cfee0'
branch_labels = None
depends_on = None


def upgrade():
    # Capitalize names for Worker
    op.execute("""
        UPDATE worker
        SET first_name = INITCAP(LOWER(first_name)),
            last_name = INITCAP(LOWER(last_name))
    """)

    # Capitalize names for Requester
    op.execute("""
        UPDATE requester
        SET first_name = INITCAP(LOWER(first_name)),
            last_name = INITCAP(LOWER(last_name))
    """)

    # Translate statuses from English to French
    op.execute("UPDATE worker SET status = 'En attente' WHERE status = 'pending'")
    op.execute("UPDATE worker SET status = 'Approuvé' WHERE status = 'approved'")
    op.execute("UPDATE worker SET status = 'Rejeté' WHERE status = 'rejected'")

    op.execute("UPDATE requester SET status = 'En attente' WHERE status = 'pending'")
    op.execute("UPDATE requester SET status = 'Approuvé' WHERE status = 'approved'")
    op.execute("UPDATE requester SET status = 'Rejeté' WHERE status = 'rejected'")


def downgrade():
    # Revert French statuses back to English
    op.execute("UPDATE worker SET status = 'pending' WHERE status = 'En attente'")
    op.execute("UPDATE worker SET status = 'approved' WHERE status = 'Approuvé'")
    op.execute("UPDATE worker SET status = 'rejected' WHERE status = 'Rejeté'")

    op.execute("UPDATE requester SET status = 'pending' WHERE status = 'En attente'")
    op.execute("UPDATE requester SET status = 'approved' WHERE status = 'Approuvé'")
    op.execute("UPDATE requester SET status = 'rejected' WHERE status = 'Rejeté'")
