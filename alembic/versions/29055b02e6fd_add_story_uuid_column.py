"""Add story_uuid column

Revision ID: 29055b02e6fd
Revises: ac736ded48bc
Create Date: 2024-09-16 19:50:34.553173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from alembic.operations import ops

# revision identifiers, used by Alembic.
revision: str = '29055b02e6fd'
down_revision: Union[str, None] = 'ac736ded48bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch operations for SQLite
    with op.batch_alter_table('invite', schema=None) as batch_op:
        batch_op.drop_constraint('fk_invite_story', type_='foreignkey')

    with op.batch_alter_table('message', schema=None) as batch_op:
        op.execute("UPDATE message SET genai_text_model = 'gpt' WHERE genai_text_model IS NULL OR genai_text_model = ''")
        batch_op.alter_column('genai_text_model',
               existing_type=sa.VARCHAR(length=6),
               type_=sa.Enum('nvidia_llama', 'gpt', 'claude', 'groq', 'gpt4o', 'gpto1', name='textmodel'),
               nullable=False,
               server_default='gpt')
        batch_op.alter_column('genai_image_model',
               existing_type=sa.VARCHAR(length=6),
               type_=sa.Enum('dalle3', 'stablediffusion', 'none', name='imagemodel'),
               existing_nullable=True)

    with op.batch_alter_table('story', schema=None) as batch_op:
        batch_op.add_column(sa.Column('story_uuid', sqlmodel.sql.sqltypes.GUID(), nullable=True))
        batch_op.create_foreign_key(
            'fk_story_invite_join_code',
            'invite',
            ['join_code'],
            ['invite_code']
        )

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('openai_api_key', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        batch_op.add_column(sa.Column('nvidia_api_key', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        batch_op.add_column(sa.Column('anthropic_api_key', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        batch_op.add_column(sa.Column('groq_api_key', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        batch_op.add_column(sa.Column('elevenlabs_api_key', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        batch_op.add_column(sa.Column('elevenlabs_voice_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))

    # Set default values for new columns in user table
    op.execute("UPDATE user SET openai_api_key = '', elevenlabs_api_key = '', elevenlabs_voice_id = '' WHERE openai_api_key IS NULL")
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('openai_api_key', nullable=False)
        batch_op.alter_column('elevenlabs_api_key', nullable=False)
        batch_op.alter_column('elevenlabs_voice_id', nullable=False)


def downgrade() -> None:
    # Use batch operations for SQLite
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('elevenlabs_voice_id')
        batch_op.drop_column('elevenlabs_api_key')
        batch_op.drop_column('groq_api_key')
        batch_op.drop_column('anthropic_api_key')
        batch_op.drop_column('nvidia_api_key')
        batch_op.drop_column('openai_api_key')

    with op.batch_alter_table('story', schema=None) as batch_op:
        batch_op.drop_constraint('fk_story_invite_join_code', type_='foreignkey')
        batch_op.drop_column('story_uuid')

    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.alter_column('genai_image_model',
               existing_type=sa.Enum('dalle3', 'stablediffusion', 'none', name='imagemodel'),
               type_=sa.VARCHAR(length=6),
               existing_nullable=True)
        batch_op.alter_column('genai_text_model',
               existing_type=sa.Enum('nvidia_llama', 'gpt', 'claude', 'groq', 'gpt4o', 'gpto1', name='textmodel'),
               type_=sa.VARCHAR(length=6),
               nullable=True)

    with op.batch_alter_table('invite', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_invite_story', 'story', ['story_id'], ['story_id'])