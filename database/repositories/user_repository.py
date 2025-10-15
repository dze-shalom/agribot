"""
User Repository
Location: agribot/database/repositories/user_repository.py

Data access layer for user-related database operations.
Provides clean interface between business logic and database.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from database.models.user import User, db
from database.models.conversation import Conversation
from utils.exceptions import DatabaseError

class UserRepository:
    """Repository for user data access operations"""
    
    @staticmethod
    def create_user(user_id: str, name: str = 'Friend', region: str = 'centre', 
                   role: str = 'farmer') -> User:
        """Create a new user in the database"""
        try:
            user = User(
                id=user_id,
                name=name,
                region=region,
                role=role
            )
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create user: {str(e)}")
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return User.query.get(user_id)
        except Exception as e:
            raise DatabaseError(f"Failed to get user: {str(e)}")
    
    @staticmethod
    def get_or_create_user(user_id: str, name: str = 'Friend', 
                          region: str = 'centre', role: str = 'farmer') -> User:
        """Get existing user or create new one"""
        user = UserRepository.get_user_by_id(user_id)
        if user:
            # Update last active and possibly other fields
            user.last_active = datetime.utcnow()
            user.name = name  # Update name if changed
            user.region = region  # Update region if changed
            db.session.commit()
            return user
        else:
            return UserRepository.create_user(user_id, name, region, role)
    
    @staticmethod
    def update_user_activity(user_id: str) -> bool:
        """Update user's last active timestamp"""
        try:
            user = User.query.get(user_id)
            if user:
                user.last_active = datetime.utcnow()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to update user activity: {str(e)}")
    
    @staticmethod
    def increment_user_conversations(user_id: str):
        """Increment the user's conversation counter"""
        try:
            user = User.query.get(user_id)
            if user:
                user.total_conversations += 1
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to increment conversations: {str(e)}")
    
    @staticmethod
    def get_users_by_region(region: str) -> List[User]:
        """Get all users from a specific region"""
        try:
            return User.query.filter_by(region=region).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get users by region: {str(e)}")
    
    @staticmethod
    def get_active_users(days: int = 30) -> List[User]:
        """Get users active within the last N days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return User.query.filter(User.last_active >= cutoff_date).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get active users: {str(e)}")
    
    @staticmethod
    def get_user_statistics() -> Dict[str, Any]:
        """Get overall user statistics"""
        try:
            total_users = User.query.count()
            
            # Users by region
            region_counts = db.session.query(
                User.region, 
                db.func.count(User.id)
            ).group_by(User.region).all()
            
            # Active users (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_users = User.query.filter(User.last_active >= thirty_days_ago).count()
            
            # New users (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            new_users = User.query.filter(User.created_at >= seven_days_ago).count()
            
            return {
                'total_users': total_users,
                'active_users_30d': active_users,
                'new_users_7d': new_users,
                'users_by_region': dict(region_counts),
                'activity_rate': round((active_users / total_users * 100) if total_users > 0 else 0, 2)
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get user statistics: {str(e)}")
    
    @staticmethod
    def delete_inactive_users(days: int = 365) -> int:
        """Delete users inactive for more than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            inactive_users = User.query.filter(User.last_active < cutoff_date)
            count = inactive_users.count()
            inactive_users.delete()
            db.session.commit()
            return count
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to delete inactive users: {str(e)}")