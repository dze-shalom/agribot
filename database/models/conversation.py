"""
Conversation Model
Location: agribot/database/models/conversation.py

Defines models for storing conversation sessions, messages,
and conversation context within the AgriBot system.
"""

from database import db
from datetime import datetime, timezone
import json
from typing import List, Dict, Optional


class Conversation(db.Model):
    """Conversation session model for tracking user interactions"""
    __tablename__ = 'conversations'
    
    # Primary key and user relationship
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, index=True)  # Frontend session ID for feedback matching
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Timing information
    start_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    end_time = db.Column(db.DateTime, nullable=True)

    # Conversation context
    title = db.Column(db.String(200), default='New Conversation')
    current_topic = db.Column(db.String(100), default='general')
    mentioned_crops = db.Column(db.Text)  # JSON array of crops discussed
    # mentioned_livestock = db.Column(db.Text, nullable=True)  # TODO: Uncomment after migration
    region = db.Column(db.String(50))
    
    # Conversation metrics
    message_count = db.Column(db.Integer, default=0)
    avg_confidence = db.Column(db.Float, default=0.0)
    
    # Status tracking
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    feedback_entries = db.relationship('Feedback', backref='conversation', lazy=True)
    
    def __repr__(self):
        return f'<Conversation {self.id} - Topic: {self.current_topic}>'
    
    def get_mentioned_crops(self) -> List[str]:
        """Get list of crops mentioned in this conversation"""
        if self.mentioned_crops:
            try:
                return json.loads(self.mentioned_crops)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_mentioned_crops(self, crops: List[str]):
        """Set the mentioned crops list"""
        self.mentioned_crops = json.dumps(crops)
    
    def add_crop(self, crop: str):
        """Add a crop to the mentioned crops list"""
        crops = self.get_mentioned_crops()
        if crop not in crops:
            crops.append(crop)
            self.set_mentioned_crops(crops)

    # TODO: Uncomment after running migration
    # def get_mentioned_livestock(self) -> List[str]:
    #     """Get list of livestock mentioned in this conversation"""
    #     if self.mentioned_livestock:
    #         try:
    #             return json.loads(self.mentioned_livestock)
    #         except json.JSONDecodeError:
    #             return []
    #     return []

    # def set_mentioned_livestock(self, livestock: List[str]):
    #     """Set the mentioned livestock list"""
    #     self.mentioned_livestock = json.dumps(livestock)

    # def add_livestock(self, animal: str):
    #     """Add livestock to the mentioned livestock list"""
    #     livestock = self.get_mentioned_livestock()
    #     if animal not in livestock:
    #         livestock.append(animal)
    #         self.set_mentioned_livestock(livestock)

    def end_conversation(self):
        """Mark conversation as ended"""
        self.end_time = datetime.now(timezone.utc)
        self.is_active = False
    
    def get_duration_minutes(self) -> Optional[float]:
        """Get conversation duration in minutes"""
        if self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 60
        return None

    @classmethod
    def count_by_user(cls, user_id: int) -> int:
        """Count conversations for a specific user"""
        return cls.query.filter_by(user_id=user_id).count()

class Message(db.Model):
    """Individual message model for storing conversation messages"""
    __tablename__ = 'messages'

    # Primary key and conversation relationship
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)

    # Message content and metadata
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # 'user' or 'bot'
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Image attachment (NEW)
    image_path = db.Column(db.String(500), nullable=True)  # Path to stored image
    image_filename = db.Column(db.String(255), nullable=True)  # Original filename
    image_url = db.Column(db.String(500), nullable=True)  # URL to access image
    has_image = db.Column(db.Boolean, default=False)  # Quick check for image

    # Image analysis results (NEW)
    image_analysis = db.Column(db.Text, nullable=True)  # JSON with disease detection results

    # NLP analysis results
    intent_classification = db.Column(db.String(50))
    confidence_score = db.Column(db.Float)
    entities_found = db.Column(db.Text)  # JSON string
    sentiment_score = db.Column(db.Float)
    
    def __repr__(self):
        return f'<Message {self.id} - {self.message_type}>'
    
    def get_entities(self) -> Dict:
        """Get entities found in this message"""
        if self.entities_found:
            try:
                return json.loads(self.entities_found)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_entities(self, entities: Dict):
        """Set the entities found in this message"""
        # Convert EntityMatch objects to dictionaries for JSON serialization
        serializable_entities = {}

        for entity_type, entity_list in entities.items():
            if isinstance(entity_list, list):
                serializable_entities[entity_type] = []
                for entity in entity_list:
                    if hasattr(entity, '__dict__'):
                        # Convert dataclass/object to dictionary
                        entity_dict = {
                            'text': getattr(entity, 'text', ''),
                            'entity_type': getattr(entity, 'entity_type', entity_type),
                            'start_pos': getattr(entity, 'start_pos', 0),
                            'end_pos': getattr(entity, 'end_pos', 0),
                            'confidence': getattr(entity, 'confidence', 0.0),
                            'normalized_form': getattr(entity, 'normalized_form', getattr(entity, 'text', ''))
                        }
                        serializable_entities[entity_type].append(entity_dict)
                    else:
                        # Already a dictionary or primitive
                        serializable_entities[entity_type].append(entity)
            else:
                # Handle non-list values
                serializable_entities[entity_type] = entity_list

        self.entities_found = json.dumps(serializable_entities)

    def get_image_analysis(self) -> Optional[Dict]:
        """Get image analysis results"""
        if self.image_analysis:
            try:
                return json.loads(self.image_analysis)
            except json.JSONDecodeError:
                return None
        return None

    def set_image_analysis(self, analysis: Dict):
        """Set the image analysis results"""
        self.image_analysis = json.dumps(analysis)

    def to_dict(self) -> Dict:
        """Convert message to dictionary for API responses"""
        result = {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'has_image': self.has_image
        }

        if self.has_image:
            result['image'] = {
                'filename': self.image_filename,
                'url': self.image_url,
                'analysis': self.get_image_analysis()
            }

        return result