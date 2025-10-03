from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    name = db.Column(db.String(100), nullable=False, default='Friend')
    region = db.Column(db.String(50), nullable=False, default='centre')
    role = db.Column(db.String(50), default='farmer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    feedback_entries = db.relationship('Feedback', backref='user', lazy=True)

class Conversation(db.Model):
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), default='New Conversation')
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    current_topic = db.Column(db.String(100), default='general')
    mentioned_crops = db.Column(db.Text)  # JSON string
    region = db.Column(db.String(50))
    message_count = db.Column(db.Integer, default=0)
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    feedback_entries = db.relationship('Feedback', backref='conversation', lazy=True)
    
    def get_mentioned_crops(self):
        if self.mentioned_crops:
            return json.loads(self.mentioned_crops)
        return []
    
    def set_mentioned_crops(self, crops):
        self.mentioned_crops = json.dumps(crops)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # 'user' or 'bot'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    intent_classification = db.Column(db.String(50))
    confidence_score = db.Column(db.Float)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    helpful = db.Column(db.Boolean)
    rating = db.Column(db.Integer)  # 1-5 scale
    accuracy_rating = db.Column(db.Integer)  # 1-5 scale
    completeness_rating = db.Column(db.Integer)  # 1-5 scale
    comment = db.Column(db.Text)
    improvement_suggestion = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class GeographicData(db.Model):
    __tablename__ = 'geographic_data'
    
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50), nullable=False)
    division = db.Column(db.String(100))
    subdivision = db.Column(db.String(100))
    city_town = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    climate_zone = db.Column(db.String(50))
    main_crops = db.Column(db.Text)  # JSON string
    population = db.Column(db.Integer)
    
    def get_main_crops(self):
        if self.main_crops:
            return json.loads(self.main_crops)
        return []
    
    def set_main_crops(self, crops):
        self.main_crops = json.dumps(crops)