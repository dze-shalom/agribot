# database/migrations/001_initial_schema.py
"""
Initial database schema for AgriBot
Creates users, conversations, analytics, and other core tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create initial database schema"""
    
    # Create enum types
    cameroon_regions = sa.Enum(
        'centre', 'littoral', 'west', 'northwest', 'southwest',
        'east', 'north', 'far_north', 'adamawa', 'south',
        name='cameroon_regions'
    )
    
    account_types = sa.Enum('user', 'admin', name='account_types')
    user_status = sa.Enum('active', 'inactive', 'deleted', name='user_status')
    conversation_status = sa.Enum('active', 'ended', 'archived', name='conversation_status')
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(120), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('region', cameroon_regions, nullable=False),
        sa.Column('account_type', account_types, nullable=False, default='user'),
        sa.Column('status', user_status, nullable=False, default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('profile_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create indexes for users table
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_region', 'users', ['region'])
    op.create_index('ix_users_account_type', 'users', ['account_type'])
    op.create_index('ix_users_status', 'users', ['status'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])
    
    # Conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(100), nullable=False),
        sa.Column('status', conversation_status, nullable=False, default='active'),
        sa.Column('started_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=False, default=0),
        sa.Column('context_data', sa.JSON(), nullable=True),
        sa.Column('satisfaction_rating', sa.Integer(), nullable=True),
        sa.Column('feedback_comment', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes for conversations table
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_session_id', 'conversations', ['session_id'])
    op.create_index('ix_conversations_started_at', 'conversations', ['started_at'])
    op.create_index('ix_conversations_status', 'conversations', ['status'])
    
    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('message_type', sa.Enum('user', 'bot', name='message_types'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('intent', sa.String(100), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('entities', sa.JSON(), nullable=True),
        sa.Column('sentiment_data', sa.JSON(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE')
    )
    
    # Create indexes for messages table
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_timestamp', 'messages', ['timestamp'])
    op.create_index('ix_messages_intent', 'messages', ['intent'])
    op.create_index('ix_messages_message_type', 'messages', ['message_type'])
    
    # Analytics events table
    op.create_table(
        'analytics_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('conversation_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('event_data', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='SET NULL')
    )
    
    # Create indexes for analytics events
    op.create_index('ix_analytics_events_event_type', 'analytics_events', ['event_type'])
    op.create_index('ix_analytics_events_timestamp', 'analytics_events', ['timestamp'])
    op.create_index('ix_analytics_events_user_id', 'analytics_events', ['user_id'])
    
    # Feedback table for detailed feedback
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('accuracy_rating', sa.Integer(), nullable=True),
        sa.Column('completeness_rating', sa.Integer(), nullable=True),
        sa.Column('helpfulness_rating', sa.Integer(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('feedback_type', sa.Enum('thumbs', 'detailed', 'survey', name='feedback_types'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='SET NULL')
    )
    
    # Create indexes for feedback
    op.create_index('ix_feedback_conversation_id', 'feedback', ['conversation_id'])
    op.create_index('ix_feedback_user_id', 'feedback', ['user_id'])
    op.create_index('ix_feedback_created_at', 'feedback', ['created_at'])
    op.create_index('ix_feedback_rating', 'feedback', ['rating'])
    
    # Crop knowledge base table
    op.create_table(
        'crop_knowledge',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crop_name', sa.String(100), nullable=False),
        sa.Column('scientific_name', sa.String(150), nullable=True),
        sa.Column('region_suitability', sa.ARRAY(sa.String(20)), nullable=True),
        sa.Column('planting_seasons', sa.JSON(), nullable=True),
        sa.Column('growth_requirements', sa.JSON(), nullable=True),
        sa.Column('common_diseases', sa.JSON(), nullable=True),
        sa.Column('common_pests', sa.JSON(), nullable=True),
        sa.Column('harvesting_info', sa.JSON(), nullable=True),
        sa.Column('market_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for crop knowledge
    op.create_index('ix_crop_knowledge_crop_name', 'crop_knowledge', ['crop_name'])
    
    # System settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('setting_key', sa.String(100), nullable=False),
        sa.Column('setting_value', sa.Text(), nullable=True),
        sa.Column('setting_type', sa.Enum('string', 'integer', 'boolean', 'json', name='setting_types'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('setting_key'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL')
    )


def downgrade():
    """Drop all tables"""
    op.drop_table('system_settings')
    op.drop_table('crop_knowledge')
    op.drop_table('feedback')
    op.drop_table('analytics_events')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('users')
    
    # Drop enum types
    sa.Enum(name='setting_types').drop(op.get_bind())
    sa.Enum(name='feedback_types').drop(op.get_bind())
    sa.Enum(name='message_types').drop(op.get_bind())
    sa.Enum(name='conversation_status').drop(op.get_bind())
    sa.Enum(name='user_status').drop(op.get_bind())
    sa.Enum(name='account_types').drop(op.get_bind())
    sa.Enum(name='cameroon_regions').drop(op.get_bind())











