"""
Conversation Repository
Location: agribot/database/repositories/conversation_repository.py

Data access layer for conversation and message-related database operations.
Handles conversation lifecycle, message storage, and context management.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from database.models.conversation import Conversation, Message, db
from database.models.user import User
from utils.exceptions import DatabaseError

class ConversationRepository:
    """Repository for conversation data access operations"""
    
    @staticmethod
    def create_conversation(user_id: str, region: str = 'centre',
                          topic: str = 'general', title: str = 'New Conversation') -> Conversation:
        """Create a new conversation session"""
        try:
            conversation = Conversation(
                user_id=user_id,
                region=region,
                current_topic=topic,
                title=title,
                mentioned_crops='[]'
            )
            db.session.add(conversation)
            db.session.commit()
            return conversation
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create conversation: {str(e)}")
    
    @staticmethod
    def get_conversation_by_id(conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID"""
        try:
            return Conversation.query.get(conversation_id)
        except Exception as e:
            raise DatabaseError(f"Failed to get conversation: {str(e)}")
    
    @staticmethod
    def get_active_conversation(user_id: str) -> Optional[Conversation]:
        """Get the most recent active conversation for a user"""
        try:
            return Conversation.query.filter_by(
                user_id=user_id, 
                is_active=True
            ).order_by(Conversation.start_time.desc()).first()
        except Exception as e:
            raise DatabaseError(f"Failed to get active conversation: {str(e)}")
    
    @staticmethod
    def add_message(conversation_id: int, content: str, message_type: str,
                   intent: str = None, confidence: float = None,
                   entities: Dict = None, sentiment: float = None) -> Message:
        """Add a message to a conversation"""
        try:
            message = Message(
                conversation_id=conversation_id,
                content=content,
                message_type=message_type,
                intent_classification=intent,
                confidence_score=confidence,
                sentiment_score=sentiment
            )
            
            if entities:
                message.set_entities(entities)
            
            db.session.add(message)
            
            # Update conversation message count
            conversation = Conversation.query.get(conversation_id)
            if conversation:
                conversation.message_count += 1
                
                # Update average confidence if this is a bot message
                if message_type == 'bot' and confidence is not None:
                    total_confidence = (conversation.avg_confidence * 
                                      (conversation.message_count - 1) + confidence)
                    conversation.avg_confidence = total_confidence / conversation.message_count
            
            db.session.commit()
            return message
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to add message: {str(e)}")
    
    @staticmethod
    def update_conversation_context(conversation_id: int, topic: str = None,
                                  crops: List[str] = None, title: str = None) -> bool:
        """Update conversation context information"""
        try:
            conversation = Conversation.query.get(conversation_id)
            if not conversation:
                return False

            if topic:
                conversation.current_topic = topic

            if crops is not None:
                conversation.set_mentioned_crops(crops)

            if title:
                conversation.title = title

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to update conversation context: {str(e)}")
    
    @staticmethod
    def end_conversation(conversation_id: int) -> bool:
        """Mark a conversation as ended"""
        try:
            conversation = Conversation.query.get(conversation_id)
            if conversation:
                conversation.end_conversation()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to end conversation: {str(e)}")
    
    @staticmethod
    def get_user_conversations(user_id: str, limit: int = 50) -> List[Conversation]:
        """Get conversation history for a user"""
        try:
            return Conversation.query.filter_by(user_id=user_id)\
                     .order_by(Conversation.start_time.desc())\
                     .limit(limit).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get user conversations: {str(e)}")
    
    @staticmethod
    def get_conversation_messages(conversation_id: int) -> List[Message]:
        """Get all messages for a conversation"""
        try:
            return Message.query.filter_by(conversation_id=conversation_id)\
                         .order_by(Message.timestamp.asc()).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get conversation messages: {str(e)}")
    
    @staticmethod
    def get_conversation_statistics(days: int = 30) -> Dict[str, Any]:
        """Get conversation statistics for the last N days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Total conversations
            total_conversations = Conversation.query.filter(
                Conversation.start_time >= cutoff_date
            ).count()
            
            # Total messages
            total_messages = db.session.query(Message)\
                .join(Conversation)\
                .filter(Conversation.start_time >= cutoff_date)\
                .count()
            
            # Average conversation length
            avg_length = db.session.query(
                db.func.avg(Conversation.message_count)
            ).filter(Conversation.start_time >= cutoff_date).scalar() or 0
            
            # Topic distribution
            topic_counts = db.session.query(
                Conversation.current_topic,
                db.func.count(Conversation.id)
            ).filter(Conversation.start_time >= cutoff_date)\
             .group_by(Conversation.current_topic).all()
            
            # Intent distribution from messages
            intent_counts = db.session.query(
                Message.intent_classification,
                db.func.count(Message.id)
            ).join(Conversation)\
             .filter(Conversation.start_time >= cutoff_date)\
             .filter(Message.intent_classification.isnot(None))\
             .group_by(Message.intent_classification).all()
            
            return {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'avg_messages_per_conversation': round(avg_length, 2),
                'topic_distribution': dict(topic_counts),
                'intent_distribution': dict(intent_counts),
                'period_days': days
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get conversation statistics: {str(e)}")