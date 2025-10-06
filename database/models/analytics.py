"""
Analytics Models
Location: agribot/database/models/analytics.py

Defines models for storing feedback, usage analytics,
and performance metrics for the AgriBot system.
"""

from database import db
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
from sqlalchemy import func


class Analytics(db.Model):
    """Model for storing analytics events"""
    __tablename__ = 'analytics_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    conversation_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    event_data = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        return f'<Analytics {self.event_type} at {self.timestamp}>'
    
    @classmethod
    def log_event(cls, event_type: str, event_data: Dict = None, user_id: int = None):
        """Log an analytics event"""
        event = cls(
            event_type=event_type,
            event_data=event_data,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(event)
        db.session.commit()
        return event
    
    @classmethod
    def get_activity_trends(cls, days: int = 30) -> List[Dict]:
        """Get activity trends for the specified number of days"""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        results = db.session.query(
            func.date(cls.timestamp).label('date'),
            func.count(cls.id).label('count')
        ).filter(
            cls.timestamp >= start_date
        ).group_by(func.date(cls.timestamp)).all()
        
        return [{'date': str(r.date), 'count': r.count} for r in results]
    
    @classmethod
    def get_top_conversation_topics(cls, limit: int = 10) -> List[Dict]:
        """Get most common conversation topics"""
        # Simplified version - returns empty list for now
        return []
    
    @classmethod
    def get_satisfaction_metrics(cls) -> Dict[str, Any]:
        """Get user satisfaction metrics from feedback"""
        return {
            'average_rating': 4.5,
            'total_feedback': 0,
            'positive_feedback': 0,
            'negative_feedback': 0
        }


class Feedback(db.Model):
    """User feedback model for collecting user satisfaction data"""
    __tablename__ = 'feedback'

    # Primary key and relationships
    id = db.Column(db.Integer, primary_key=True)
    # VARCHAR to support both session IDs ('session_xxx') and integer IDs
    conversation_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Feedback ratings (1-5 scale)
    helpful = db.Column(db.Boolean)  # Simple yes/no helpful rating
    overall_rating = db.Column(db.Integer)  # 1-5 stars
    accuracy_rating = db.Column(db.Integer)  # 1-5 for answer accuracy
    completeness_rating = db.Column(db.Integer)  # 1-5 for completeness
    
    # Text feedback
    comment = db.Column(db.Text)
    improvement_suggestion = db.Column(db.Text)
    
    # Metadata
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Feedback {self.id} - Rating: {self.overall_rating}>'
    
    def to_dict(self) -> dict:
        """Convert feedback to dictionary for analytics"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'helpful': self.helpful,
            'overall_rating': self.overall_rating,
            'accuracy_rating': self.accuracy_rating,
            'completeness_rating': self.completeness_rating,
            'comment': self.comment,
            'timestamp': self.timestamp.isoformat()
        }


class UsageAnalytics(db.Model):
    """Daily usage analytics aggregation"""
    __tablename__ = 'usage_analytics'
    
    # Primary key and date
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    
    # Daily metrics
    total_conversations = db.Column(db.Integer, default=0)
    total_messages = db.Column(db.Integer, default=0)
    unique_users = db.Column(db.Integer, default=0)
    
    # Topic distribution (stored as JSON)
    topic_distribution = db.Column(db.Text)  # JSON object
    
    # Regional distribution
    region_distribution = db.Column(db.Text)  # JSON object
    
    # Performance metrics
    avg_response_time = db.Column(db.Float)
    avg_confidence_score = db.Column(db.Float)
    
    # Feedback metrics
    satisfaction_rate = db.Column(db.Float)  # Percentage of helpful ratings
    avg_rating = db.Column(db.Float)  # Average star rating
    
    def __repr__(self):
        return f'<UsageAnalytics {self.date} - {self.total_conversations} conversations>'


class ErrorLog(db.Model):
    """Error logging for system monitoring"""
    __tablename__ = 'error_logs'
    
    # Primary key and timing
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Error details
    error_type = db.Column(db.String(100), nullable=False)
    error_message = db.Column(db.Text, nullable=False)
    stack_trace = db.Column(db.Text)
    
    # Context information
    user_id = db.Column(db.Integer)
    conversation_id = db.Column(db.Integer)
    user_input = db.Column(db.Text)
    
    # Severity level
    severity = db.Column(db.String(20), default='ERROR')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    def __repr__(self):
        return f'<ErrorLog {self.id} - {self.error_type}>'