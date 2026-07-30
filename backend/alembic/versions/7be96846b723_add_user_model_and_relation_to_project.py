"""Add User model and relation to Project

Revision ID: 7be96846b723
Revises: bc7c1ba8a188
Create Date: 2026-07-30 17:44:13.069723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7be96846b723'
down_revision: Union[str, Sequence[str], None] = 'bc7c1ba8a188'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import uuid
from datetime import datetime, timezone

def upgrade() -> None:
    # 1. Create users table
    op.create_table('users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('full_name', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 2. Insert a default system user
    system_user_id = uuid.uuid4()
    # Note: Using raw string representation formatted safely for sqlite
    system_user_id_hex = system_user_id.hex
    now = datetime.now(timezone.utc).isoformat()
    
    op.execute(f"""
        INSERT INTO users (id, full_name, email, username, password_hash, is_active, is_superuser, email_verified, created_at, updated_at)
        VALUES ('{system_user_id_hex}', 'System User', 'system@researchos.local', 'system', 'no-password', 1, 1, 1, '{now}', '{now}')
    """)

    # 3. Add user_id column as nullable initially
    op.add_column('projects', sa.Column('user_id', sa.Uuid(), nullable=True))

    # 4. Backfill user_id on existing projects
    op.execute(f"UPDATE projects SET user_id = '{system_user_id_hex}'")

    # 5. Use batch mode to alter the table safely in SQLite
    with op.batch_alter_table('projects', schema=None) as batch_op:
        # Alter user_id to be NOT NULL
        batch_op.alter_column('user_id', existing_type=sa.Uuid(), nullable=False)
        
        # Create foreign key and index on user_id
        batch_op.create_foreign_key('fk_projects_user_id', 'users', ['user_id'], ['id'])
        batch_op.create_index(batch_op.f('ix_projects_user_id'), ['user_id'], unique=False)
        
        # Drop legacy owner_id column and index
        batch_op.drop_index('ix_projects_owner_id')
        batch_op.drop_column('owner_id')


def downgrade() -> None:
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_id', sa.VARCHAR(length=100), nullable=True))
        batch_op.create_index('ix_projects_owner_id', ['owner_id'], unique=False)
        
        batch_op.drop_index(batch_op.f('ix_projects_user_id'))
        batch_op.drop_constraint('fk_projects_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
