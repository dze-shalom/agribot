"""
User Model
Location: agribot/database/models/user.py

Defines the User model for storing user information, preferences,
and tracking user activity within the AgriBot system.
"""

from database import db
from datetime import datetime, timezone
from typing import Dict
from werkzeug.security import generate_password_hash, check_password_hash
import enum


class CameroonRegion(enum.Enum):
    CENTRE = 'centre'
    LITTORAL = 'littoral'
    WEST = 'west'
    NORTHWEST = 'northwest'
    SOUTHWEST = 'southwest'
    EAST = 'east'
    NORTH = 'north'
    FAR_NORTH = 'far_north'
    ADAMAWA = 'adamawa'
    SOUTH = 'south'

class AccountType(enum.Enum):
    USER = 'user'
    ADMIN = 'admin'

class UserStatus(enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DELETED = 'deleted'

class User(db.Model):
    """User model for storing farmer/user information and preferences"""
    __tablename__ = 'users'
    
    # Primary identification
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, default='Friend')
    
    # Authentication fields
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    
    # Geographic and role information
    country = db.Column(db.String(100), nullable=False, default='Cameroon')  # New: Support any country
    region = db.Column(db.String(100), nullable=False, default='Centre')  # Changed from Enum to String for flexibility
    account_type = db.Column(db.Enum(AccountType, values_callable=lambda x: [e.value for e in x]), nullable=False, default=AccountType.USER)
    status = db.Column(db.Enum(UserStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=UserStatus.ACTIVE)
    
    # User preferences (stored as JSON)
    preferred_language = db.Column(db.String(10), default='en')
    notification_preferences = db.Column(db.Text)  # JSON string
    profile_data = db.Column(db.JSON)  # Additional profile data
    
    # Tracking fields
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_active = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    total_conversations = db.Column(db.Integer, default=0)
    
    # Relationships
    conversations = db.relationship('Conversation', backref='user', lazy=True, cascade='all, delete-orphan')
    feedback_entries = db.relationship('Feedback', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name} ({self.email}) from {self.region.value}>'
    
    # Authentication methods
    def set_password(self, password: str):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_active(self):
        """Update the last active timestamp"""
        self.last_active = datetime.now(timezone.utc)
        db.session.commit()
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'country': self.country,  # New: Include country
            'region': self.region,  # Now string, no .value needed
            'account_type': self.account_type.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'total_conversations': self.total_conversations
        }
    
    # Class methods for the authentication system
    @classmethod
    def create(cls, user_data: dict):
        """Create a new user"""
        user = cls(
            name=user_data['name'],
            email=user_data['email'],
            phone=user_data.get('phone'),
            country=user_data.get('country', 'Cameroon'),  # New: Support any country, default Cameroon
            region=user_data['region'],  # Now accepts string directly
            account_type=AccountType(user_data['account_type']),
            created_at=user_data.get('created_at', datetime.now(timezone.utc))
        )
        user.password_hash = user_data['password_hash']

        # Status will use default value UserStatus.ACTIVE from model definition

        db.session.add(user)
        db.session.commit()
        return user
    
    @classmethod
    def get_by_id(cls, user_id: int):
        """Get user by ID"""
        return cls.query.filter_by(id=user_id).first()
    
    @classmethod
    def get_by_email(cls, email: str):
        """Get user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_all_paginated(cls, page=1, per_page=50, region=None, status=None, search=None):
        """Get paginated users with filters"""
        query = cls.query
        
        # Apply filters
        if region:
            query = query.filter(cls.region == CameroonRegion(region))
        if status:
            query = query.filter(cls.status == UserStatus(status))
        if search:
            query = query.filter(
                cls.name.ilike(f'%{search}%') | 
                cls.email.ilike(f'%{search}%')
            )
        
        total = query.count()
        users = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return users, total
    
    @classmethod
    def update(cls, user_id: int, update_data: dict):
        """Update user data"""
        user = cls.get_by_id(user_id)
        if not user:
            return False
        
        for key, value in update_data.items():
            if hasattr(user, key):
                if key == 'region' and isinstance(value, str):
                    value = CameroonRegion(value)
                elif key == 'account_type' and isinstance(value, str):
                    value = AccountType(value)
                elif key == 'status' and isinstance(value, str):
                    value = UserStatus(value)
                setattr(user, key, value)
        
        db.session.commit()
        return True
    
    @classmethod
    def update_last_login(cls, user_id: int):
        """Update last login timestamp"""
        cls.update(user_id, {'last_login': datetime.now(timezone.utc)})
    
    @classmethod
    def count_total(cls):
        """Count total users"""
        return cls.query.filter(cls.status != UserStatus.DELETED).count()
    
    @classmethod
    def count_active(cls):
        """Count active users"""
        return cls.query.filter(cls.status == UserStatus.ACTIVE).count()
    
    @classmethod
    def count_new_since(cls, date):
        """Count new users since date"""
        return cls.query.filter(
            cls.created_at >= date,
            cls.status != UserStatus.DELETED
        ).count()
    
    @classmethod
    def get_regional_distribution(cls):
        """Get user distribution by region"""
        from sqlalchemy import func
        
        result = db.session.query(
            cls.region,
            func.count(cls.id).label('count')
        ).filter(cls.status != UserStatus.DELETED).group_by(cls.region).all()
        
        return [{'region': r.region.value, 'count': r.count} for r in result]
    
    @classmethod
    def get_for_export(cls, region=None, status=None, start_date=None, end_date=None):
        """Get users for export"""
        query = cls.query
        
        if region:
            query = query.filter(cls.region == CameroonRegion(region))
        if status:
            query = query.filter(cls.status == UserStatus(status))
        if start_date:
            query = query.filter(cls.created_at >= start_date)
        if end_date:
            query = query.filter(cls.created_at <= end_date)
        
        return query.all()

    # Backward compatibility property
    @property
    def role(self):
        """Backward compatibility property"""
        return self.account_type.value if self.account_type else 'farmer'
    
    @role.setter
    def role(self, value):
        """Backward compatibility setter"""
        if value == 'farmer':
            self.account_type = AccountType.USER
        elif value == 'admin':
            self.account_type = AccountType.ADMIN
        else:
            self.account_type = AccountType.USER