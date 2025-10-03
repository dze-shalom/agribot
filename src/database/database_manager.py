from database.models import db, User, Conversation, Message, Feedback, GeographicData
from datetime import datetime
import uuid
import json

class DatabaseManager:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        db.init_app(app)
        self.app = app
    
    def create_tables(self):
        """Create all database tables"""
        with self.app.app_context():
            db.create_all()
            self.populate_geographic_data()
    
    def get_or_create_user(self, user_id, name='Friend', region='centre'):
        """Get existing user or create new one"""
        user = User.query.get(user_id)
        if not user:
            user = User(
                id=user_id,
                name=name,
                region=region,
                role='farmer'
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Update last active
            user.last_active = datetime.utcnow()
            user.name = name  # Update name if changed
            user.region = region  # Update region if changed
            db.session.commit()
        
        return user
    
    def create_conversation(self, user_id, region='centre'):
        """Start a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            region=region,
            current_topic='greeting',
            mentioned_crops='[]'
        )
        db.session.add(conversation)
        db.session.commit()
        return conversation
    
    def add_message(self, conversation_id, content, message_type, intent=None, confidence=None):
        """Add a message to conversation"""
        message = Message(
            conversation_id=conversation_id,
            content=content,
            message_type=message_type,
            intent_classification=intent,
            confidence_score=confidence
        )
        db.session.add(message)
        
        # Update conversation message count
        conversation = Conversation.query.get(conversation_id)
        if conversation:
            conversation.message_count += 1
        
        db.session.commit()
        return message
    
    def update_conversation_context(self, conversation_id, topic=None, crops=None):
        """Update conversation context"""
        conversation = Conversation.query.get(conversation_id)
        if conversation:
            if topic:
                conversation.current_topic = topic
            if crops:
                conversation.set_mentioned_crops(crops)
            db.session.commit()
        return conversation
    
    def add_feedback(self, conversation_id, user_id, helpful=None, rating=None, comment=None):
        """Add user feedback"""
        feedback = Feedback(
            conversation_id=conversation_id,
            user_id=user_id,
            helpful=helpful,
            rating=rating,
            comment=comment
        )
        db.session.add(feedback)
        db.session.commit()
        return feedback
    
    def get_analytics_data(self):
        """Get comprehensive analytics"""
        total_conversations = Conversation.query.count()
        total_users = User.query.count()
        total_messages = Message.query.count()
        total_feedback = Feedback.query.count()
        
        # Calculate satisfaction metrics
        positive_feedback = Feedback.query.filter_by(helpful=True).count()
        satisfaction_rate = (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0
        
        # Intent distribution
        intent_query = db.session.query(Message.intent_classification, db.func.count(Message.id))\
                                .filter(Message.intent_classification.isnot(None))\
                                .group_by(Message.intent_classification).all()
        intent_distribution = dict(intent_query)
        
        # Region distribution
        region_query = db.session.query(User.region, db.func.count(User.id))\
                               .group_by(User.region).all()
        region_distribution = dict(region_query)
        
        # Recent feedback
        recent_feedback = Feedback.query.order_by(Feedback.timestamp.desc()).limit(10).all()
        
        # Average ratings
        avg_rating_query = db.session.query(db.func.avg(Feedback.rating)).scalar()
        avg_rating = round(avg_rating_query, 1) if avg_rating_query else 0
        
        return {
            'overview': {
                'total_conversations': total_conversations,
                'total_users': total_users,
                'total_messages': total_messages,
                'total_feedback': total_feedback,
                'satisfaction_rate': round(satisfaction_rate, 1),
                'helpful_percentage': round(satisfaction_rate, 1),
                'average_rating': avg_rating,
                'feedback_response_rate': round((total_feedback / total_conversations * 100) if total_conversations > 0 else 0, 1),
                'average_accuracy': avg_rating,
                'average_completeness': avg_rating
            },
            'intent_analysis': {
                'distribution': intent_distribution
            },
            'user_demographics': {
                'regions': region_distribution,
                'roles': {'farmer': total_users}  # For now, all users are farmers
            },
            'recent_feedback': [
                {
                    'helpful': f.helpful,
                    'rating': f.rating,
                    'comment': f.comment,
                    'timestamp': f.timestamp.isoformat(),
                    'improvement_suggestion': f.improvement_suggestion
                }
                for f in recent_feedback
            ]
        }
    
    def populate_geographic_data(self):
        """Populate geographic data if empty"""
        if GeographicData.query.count() == 0:
            # Add all 10 regions with their main data
            regions_data = [
                {
                    'region': 'centre',
                    'division': 'Mfoundi',
                    'city_town': 'Yaounde',
                    'latitude': 3.848,
                    'longitude': 11.502,
                    'climate_zone': 'humid_forest',
                    'main_crops': ['cassava', 'plantain', 'maize', 'cocoa', 'yam'],
                    'population': 4200000
                },
                {
                    'region': 'littoral',
                    'division': 'Wouri',
                    'city_town': 'Douala',
                    'latitude': 4.061,
                    'longitude': 9.786,
                    'climate_zone': 'coastal_humid',
                    'main_crops': ['banana', 'oil_palm', 'pineapple', 'cocoa', 'rubber'],
                    'population': 3200000
                },
                # Add more regions as needed
            ]
            
            for region_data in regions_data:
                geo = GeographicData(
                    region=region_data['region'],
                    division=region_data['division'],
                    city_town=region_data['city_town'],
                    latitude=region_data['latitude'],
                    longitude=region_data['longitude'],
                    climate_zone=region_data['climate_zone'],
                    population=region_data['population']
                )
                geo.set_main_crops(region_data['main_crops'])
                db.session.add(geo)
            
            db.session.commit()
    
    def migrate_existing_data(self, conversations_list, feedback_list):
        """Migrate data from in-memory storage to database"""
        for conv_data in conversations_list:
            # Create or get user
            user = self.get_or_create_user(
                conv_data['user_id'],
                conv_data.get('user_name', 'Friend'),
                conv_data.get('user_region', 'centre')
            )
            
            # Create conversation
            conversation = Conversation(
                user_id=user.id,
                start_time=datetime.fromisoformat(conv_data['timestamp']),
                current_topic=conv_data.get('current_topic', 'general'),
                region=conv_data.get('user_region', 'centre'),
                message_count=2  # User message + bot response
            )
            db.session.add(conversation)
            db.session.flush()  # Get the ID
            
            # Add user message
            user_msg = Message(
                conversation_id=conversation.id,
                content=conv_data['user_message'],
                message_type='user',
                timestamp=datetime.fromisoformat(conv_data['timestamp'])
            )
            db.session.add(user_msg)
            
            # Add bot response
            bot_msg = Message(
                conversation_id=conversation.id,
                content=conv_data['bot_response'],
                message_type='bot',
                timestamp=datetime.fromisoformat(conv_data['timestamp'])
            )
            db.session.add(bot_msg)
        
        # Migrate feedback
        for feedback_data in feedback_list:
            # Find corresponding conversation
            conv = Conversation.query.filter_by(id=feedback_data.get('conversation_id')).first()
            if conv:
                feedback = Feedback(
                    conversation_id=conv.id,
                    user_id=conv.user_id,
                    helpful=feedback_data.get('helpful'),
                    rating=feedback_data.get('rating'),
                    comment=feedback_data.get('comment'),
                    timestamp=datetime.fromisoformat(feedback_data['timestamp'])
                )
                db.session.add(feedback)
        
        db.session.commit()
        print(f"Migrated {len(conversations_list)} conversations and {len(feedback_list)} feedback entries")

# Global instance
db_manager = DatabaseManager()