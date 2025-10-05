"""
Analytics Repository
Location: agribot/database/repositories/analytics_repository.py

Data access layer for analytics, feedback, and performance metrics.
Handles feedback collection, usage analytics, and error logging.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, date
import json
from database.models.analytics import Feedback, UsageAnalytics, ErrorLog, db
from database.models.conversation import Conversation, Message
from database.models.user import User
from utils.exceptions import DatabaseError

class AnalyticsRepository:
    """Repository for analytics and feedback data operations"""
    
    @staticmethod
    def add_feedback(conversation_id: int, user_id: str, helpful: bool = None,
                    overall_rating: int = None, accuracy_rating: int = None,
                    completeness_rating: int = None, comment: str = None,
                    improvement_suggestion: str = None) -> Feedback:
        """Add user feedback for a conversation"""
        try:
            feedback = Feedback(
                conversation_id=conversation_id,
                user_id=user_id,
                helpful=helpful,
                overall_rating=overall_rating,
                accuracy_rating=accuracy_rating,
                completeness_rating=completeness_rating,
                comment=comment,
                improvement_suggestion=improvement_suggestion
            )
            db.session.add(feedback)
            db.session.commit()
            return feedback
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to add feedback: {str(e)}")
    
    @staticmethod
    def get_feedback_by_conversation(conversation_id: int) -> List[Feedback]:
        """Get all feedback for a conversation"""
        try:
            return Feedback.query.filter_by(conversation_id=conversation_id).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get feedback: {str(e)}")
    
    @staticmethod
    def get_satisfaction_metrics(days: int = 30) -> Dict[str, Any]:
        """Get satisfaction metrics for the last N days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Total feedback count
            total_feedback = Feedback.query.filter(Feedback.timestamp >= cutoff_date).count()
            
            if total_feedback == 0:
                return {
                    'total_feedback': 0,
                    'satisfaction_rate': 0,
                    'avg_overall_rating': 0,
                    'avg_accuracy_rating': 0,
                    'avg_completeness_rating': 0
                }
            
            # Helpful feedback percentage
            helpful_count = Feedback.query.filter(
                Feedback.timestamp >= cutoff_date,
                Feedback.helpful == True
            ).count()
            
            satisfaction_rate = (helpful_count / total_feedback * 100) if total_feedback > 0 else 0
            
            # Average ratings
            ratings_query = db.session.query(
                db.func.avg(Feedback.overall_rating),
                db.func.avg(Feedback.accuracy_rating), 
                db.func.avg(Feedback.completeness_rating)
            ).filter(Feedback.timestamp >= cutoff_date)
            
            avg_overall, avg_accuracy, avg_completeness = ratings_query.first()
            
            return {
                'total_feedback': total_feedback,
                'satisfaction_rate': round(satisfaction_rate, 2),
                'avg_overall_rating': round(avg_overall or 0, 2),
                'avg_accuracy_rating': round(avg_accuracy or 0, 2),
                'avg_completeness_rating': round(avg_completeness or 0, 2),
                'feedback_response_rate': round((total_feedback / Conversation.query.filter(
                    Conversation.start_time >= cutoff_date
                ).count() * 100) if Conversation.query.filter(
                    Conversation.start_time >= cutoff_date
                ).count() > 0 else 0, 2)
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get satisfaction metrics: {str(e)}")
    
    @staticmethod
    def get_recent_feedback(limit: int = 10) -> List[Feedback]:
        """Get most recent feedback entries"""
        try:
            return Feedback.query.order_by(Feedback.timestamp.desc()).limit(limit).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get recent feedback: {str(e)}")
    
    @staticmethod
    def create_or_update_daily_analytics(target_date: date = None) -> UsageAnalytics:
        """Create or update daily analytics aggregation"""
        if target_date is None:
            target_date = date.today()
        
        try:
            # Check if analytics already exist for this date
            analytics = UsageAnalytics.query.filter_by(date=target_date).first()
            
            if not analytics:
                analytics = UsageAnalytics(date=target_date)
                db.session.add(analytics)
            
            # Calculate metrics for the day
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())
            
            # Total conversations and messages
            daily_conversations = Conversation.query.filter(
                Conversation.start_time >= start_datetime,
                Conversation.start_time <= end_datetime
            ).all()
            
            analytics.total_conversations = len(daily_conversations)
            analytics.total_messages = sum(conv.message_count for conv in daily_conversations)
            
            # Unique users
            unique_user_ids = set(conv.user_id for conv in daily_conversations)
            analytics.unique_users = len(unique_user_ids)
            
            # Topic distribution
            topic_counts = {}
            region_counts = {}
            
            for conv in daily_conversations:
                topic_counts[conv.current_topic] = topic_counts.get(conv.current_topic, 0) + 1
                region_counts[conv.region] = region_counts.get(conv.region, 0) + 1
            
            analytics.topic_distribution = str(topic_counts)
            analytics.region_distribution = str(region_counts)
            
            # Performance metrics
            if daily_conversations:
                avg_confidence = sum(
                    conv.avg_confidence for conv in daily_conversations if conv.avg_confidence
                ) / len([conv for conv in daily_conversations if conv.avg_confidence])
                analytics.avg_confidence_score = avg_confidence or 0
            
            # Satisfaction metrics
            daily_feedback = Feedback.query.filter(
                Feedback.timestamp >= start_datetime,
                Feedback.timestamp <= end_datetime
            ).all()
            
            if daily_feedback:
                helpful_count = sum(1 for f in daily_feedback if f.helpful)
                analytics.satisfaction_rate = (helpful_count / len(daily_feedback) * 100)
                
                ratings = [f.overall_rating for f in daily_feedback if f.overall_rating]
                analytics.avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            db.session.commit()
            return analytics
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create daily analytics: {str(e)}")
    
    @staticmethod
    def log_error(error_type: str, error_message: str, stack_trace: str = None,
                  user_id: str = None, conversation_id: int = None,
                  user_input: str = None, severity: str = 'ERROR') -> ErrorLog:
        """Log an error for monitoring and debugging"""
        try:
            error_log = ErrorLog(
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                user_id=user_id,
                conversation_id=conversation_id,
                user_input=user_input,
                severity=severity
            )
            db.session.add(error_log)
            db.session.commit()
            return error_log
        except Exception as e:
            db.session.rollback()
            # Don't raise exception here to avoid infinite loops
            print(f"Failed to log error: {str(e)}")
            return None
    
    @staticmethod
    def get_error_summary(days: int = 7) -> Dict[str, Any]:
        """Get error summary for monitoring dashboard"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Error counts by type
            error_counts = db.session.query(
                ErrorLog.error_type,
                db.func.count(ErrorLog.id)
            ).filter(ErrorLog.timestamp >= cutoff_date)\
             .group_by(ErrorLog.error_type).all()
            
            # Error counts by severity
            severity_counts = db.session.query(
                ErrorLog.severity,
                db.func.count(ErrorLog.id)
            ).filter(ErrorLog.timestamp >= cutoff_date)\
             .group_by(ErrorLog.severity).all()
            
            # Recent critical errors
            critical_errors = ErrorLog.query.filter(
                ErrorLog.timestamp >= cutoff_date,
                ErrorLog.severity == 'CRITICAL'
            ).order_by(ErrorLog.timestamp.desc()).limit(5).all()
            
            total_errors = ErrorLog.query.filter(ErrorLog.timestamp >= cutoff_date).count()
            
            return {
                'total_errors': total_errors,
                'error_types': dict(error_counts),
                'severity_distribution': dict(severity_counts),
                'recent_critical_errors': [
                    {
                        'timestamp': err.timestamp.isoformat(),
                        'error_type': err.error_type,
                        'message': err.error_message[:200]  # Truncate for summary
                    }
                    for err in critical_errors
                ],
                'period_days': days
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get error summary: {str(e)}")
    
    @staticmethod
    def get_comprehensive_analytics(days: int = 30, region: str = 'all') -> Dict[str, Any]:
        """Get comprehensive analytics dashboard data with optional region filtering"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Build base user query with region filter
            user_query = User.query
            if region != 'all':
                user_query = user_query.filter(User.region == region)

            # User metrics
            total_users = user_query.count()
            active_users = user_query.filter(User.last_active >= cutoff_date).count()
            new_users = user_query.filter(User.created_at >= cutoff_date).count()

            # Build base conversation query with region filter
            conv_query = Conversation.query.join(User).filter(Conversation.start_time >= cutoff_date)
            if region != 'all':
                conv_query = conv_query.filter(User.region == region)

            # Conversation metrics
            total_conversations = conv_query.count()

            # Build message query with region filter
            msg_query = db.session.query(Message).join(Conversation).join(User).filter(Conversation.start_time >= cutoff_date)
            if region != 'all':
                msg_query = msg_query.filter(User.region == region)

            total_messages = msg_query.count()

            # AI Accuracy - based on average confidence scores (with region filter)
            ai_acc_query = db.session.query(db.func.avg(Message.confidence_score))\
                .join(Conversation).join(User)\
                .filter(
                    Conversation.start_time >= cutoff_date,
                    Message.message_type == 'bot',
                    Message.confidence_score.isnot(None)
                )
            if region != 'all':
                ai_acc_query = ai_acc_query.filter(User.region == region)

            avg_confidence = ai_acc_query.scalar()
            ai_accuracy = round((avg_confidence * 100) if avg_confidence else 0.0, 1)

            # User Satisfaction - based on feedback (with region filter)
            # Join directly with User using user_id from Feedback table
            feedback_query_base = Feedback.query.join(User, Feedback.user_id == User.id).filter(Feedback.timestamp >= cutoff_date)
            if region != 'all':
                feedback_query_base = feedback_query_base.filter(User.region == region)

            positive_feedback = feedback_query_base.filter(Feedback.helpful == True).count()
            total_feedback = feedback_query_base.filter(Feedback.helpful.isnot(None)).count()

            satisfaction_rate = round((positive_feedback / total_feedback * 100) if total_feedback > 0 else 0.0, 1)

            # Average rating from detailed feedback (with region filter)
            # Join directly with User using user_id from Feedback table
            rating_query = db.session.query(db.func.avg(Feedback.overall_rating))\
                .join(User, Feedback.user_id == User.id)\
                .filter(
                    Feedback.timestamp >= cutoff_date,
                    Feedback.overall_rating.isnot(None)
                )
            if region != 'all':
                rating_query = rating_query.filter(User.region == region)

            avg_rating = rating_query.scalar()
            user_satisfaction_score = round(avg_rating if avg_rating else 0.0, 1)

            # Satisfaction metrics
            satisfaction_data = AnalyticsRepository.get_satisfaction_metrics(days)

            # Error summary
            error_data = AnalyticsRepository.get_error_summary(days)

            # Country distribution
            country_dist_query = db.session.query(
                User.country,
                db.func.count(User.id).label('count')
            ).group_by(User.country).all()

            country_distribution = [
                {'country': c.country or 'Unknown', 'count': c.count}
                for c in country_dist_query
            ]

            # Regional distribution grouped by country
            regional_by_country_query = db.session.query(
                User.country,
                User.region,
                db.func.count(User.id).label('count')
            ).group_by(User.country, User.region).all()

            # Build nested structure: country -> regions
            regional_by_country = {}
            for r in regional_by_country_query:
                country = r.country or 'Unknown'
                region = r.region or 'Unknown'
                if country not in regional_by_country:
                    regional_by_country[country] = []
                regional_by_country[country].append({'region': region, 'count': r.count})

            # Also provide flat regional distribution for backwards compatibility
            regional_dist_query = db.session.query(
                User.region,
                db.func.count(User.id).label('count')
            ).group_by(User.region).all()

            regional_distribution = [
                {'region': r.region or 'Unknown', 'count': r.count}
                for r in regional_dist_query
            ]

            # Intent distribution - get from messages
            intent_dist_query = db.session.query(
                Message.intent_classification,
                db.func.count(Message.id).label('count')
            ).filter(
                Message.timestamp >= cutoff_date,
                Message.intent_classification.isnot(None)
            ).group_by(Message.intent_classification).all()

            intent_distribution = [
                {'intent': i.intent_classification or 'Unknown', 'count': i.count}
                for i in intent_dist_query
            ] if intent_dist_query else []

            # Sentiment analysis - get from messages
            sentiment_query = db.session.query(Message.sentiment_score).filter(
                Message.timestamp >= cutoff_date,
                Message.sentiment_score.isnot(None)
            ).all()

            positive_count = sum(1 for s in sentiment_query if s.sentiment_score and s.sentiment_score > 0.1)
            neutral_count = sum(1 for s in sentiment_query if s.sentiment_score and -0.1 <= s.sentiment_score <= 0.1)
            negative_count = sum(1 for s in sentiment_query if s.sentiment_score and s.sentiment_score < -0.1)
            avg_sentiment = sum(s.sentiment_score for s in sentiment_query if s.sentiment_score) / len(sentiment_query) if sentiment_query else 0

            sentiment_data_detailed = {
                'positive_count': positive_count,
                'neutral_count': neutral_count,
                'negative_count': negative_count,
                'average': avg_sentiment
            }

            # Hourly activity - messages by hour
            hourly_activity = [0] * 24
            hourly_query = db.session.query(
                db.func.extract('hour', Message.timestamp).label('hour'),
                db.func.count(Message.id).label('count')
            ).filter(Message.timestamp >= cutoff_date).group_by('hour').all()

            for hour_data in hourly_query:
                hour = int(hour_data.hour) if hour_data.hour is not None else 0
                if 0 <= hour < 24:
                    hourly_activity[hour] = hour_data.count

            # Crop trends - get from conversations
            # Query only specific columns to avoid loading mentioned_livestock which doesn't exist yet
            crop_counts = {}
            try:
                conversations = db.session.query(
                    Conversation.id,
                    Conversation.mentioned_crops
                ).filter(Conversation.start_time >= cutoff_date).all()

                for conv_id, mentioned_crops in conversations:
                    if mentioned_crops:
                        try:
                            crops = json.loads(mentioned_crops)
                            for crop in crops:
                                crop_name = crop.lower().capitalize()
                                crop_counts[crop_name] = crop_counts.get(crop_name, 0) + 1
                        except:
                            pass
            except Exception:
                pass  # If query fails, just return empty crop trends

            # Get top 10 crops
            crop_trends = [
                {'crop': crop, 'count': count}
                for crop, count in sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]

            # Confidence distribution - group confidence scores into buckets
            confidence_scores = db.session.query(Message.confidence_score).filter(
                Message.timestamp >= cutoff_date,
                Message.confidence_score.isnot(None)
            ).all()

            # Create distribution buckets (0.0-0.1, 0.1-0.2, ..., 0.9-1.0)
            confidence_distribution = []
            for i in range(10):
                bucket_start = i / 10
                bucket_end = (i + 1) / 10
                count = sum(1 for s in confidence_scores if s.confidence_score and bucket_start <= s.confidence_score < bucket_end)
                confidence_distribution.append({'score': (bucket_start + bucket_end) / 2, 'count': count})

            # User statistics (for charts and detailed analysis)
            user_statistics = {
                'total_users': total_users,
                'active_users_7d': active_users,
                'new_users_30d': new_users,
                'active_users_30d': user_query.filter(User.last_active >= cutoff_date).count(),
                'user_growth_rate': round((new_users / total_users * 100) if total_users > 0 else 0, 1)
            }

            # Conversation statistics
            # Calculate average conversation duration
            # Query only specific columns to avoid loading mentioned_livestock which doesn't exist yet
            duration_data = db.session.query(
                Conversation.start_time,
                Conversation.end_time
            ).join(User).filter(
                Conversation.start_time >= cutoff_date,
                Conversation.end_time.isnot(None)
            )
            if region != 'all':
                duration_data = duration_data.filter(User.region == region)

            conversations_with_duration = duration_data.all()

            if conversations_with_duration:
                total_duration = sum(
                    (end_time - start_time).total_seconds() / 60
                    for start_time, end_time in conversations_with_duration
                )
                avg_duration = total_duration / len(conversations_with_duration)
            else:
                avg_duration = 0

            conversation_statistics = {
                'total_conversations': total_conversations,
                'conversations_7d': Conversation.query.filter(
                    Conversation.start_time >= datetime.utcnow() - timedelta(days=7)
                ).count(),
                'avg_duration_minutes': round(avg_duration, 2),
                'avg_messages_per_conversation': round(
                    (total_messages / total_conversations) if total_conversations > 0 else 0, 2
                )
            }

            return {
                'overview': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'new_users': new_users,
                    'total_conversations': total_conversations,
                    'total_messages': total_messages,
                    'ai_accuracy': ai_accuracy,
                    'satisfaction_rate': satisfaction_rate,
                    'user_satisfaction_score': user_satisfaction_score,
                    'total_feedback_count': total_feedback,
                    'avg_messages_per_conversation': round(
                        (total_messages / total_conversations) if total_conversations > 0 else 0, 2
                    ),
                    'user_activity_rate': round(
                        (active_users / total_users * 100) if total_users > 0 else 0, 2
                    )
                },
                'user_statistics': user_statistics,
                'conversation_statistics': conversation_statistics,
                'country_distribution': country_distribution,
                'regional_distribution': regional_distribution,
                'regional_by_country': regional_by_country,
                'intent_distribution': intent_distribution,
                'sentiment': sentiment_data_detailed,
                'hourly_activity': hourly_activity,
                'crop_trends': crop_trends,
                'confidence_distribution': confidence_distribution,
                'satisfaction': satisfaction_data,
                'errors': error_data,
                'period_days': days
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get comprehensive analytics: {str(e)}")