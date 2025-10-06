# app/routes/auth.py
"""
Authentication routes for AgriBot user management system
"""

from flask import Blueprint, request, jsonify, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta, timezone
import csv
import io
import logging
from database.models.user import User
from database.models.conversation import Conversation
from database.models.analytics import Analytics
from database.repositories.analytics_repository import AnalyticsRepository
from database import db
from utils.validators import validate_email, validate_password
from utils.exceptions import ValidationError
from services.cache.redis_cache import cache_user_session


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = logging.getLogger(__name__)

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        user = User.get_by_id(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 403

        # Handle both enum and string values
        account_type = user.account_type.value if hasattr(user.account_type, 'value') else user.account_type
        if account_type != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403

        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'region', 'account_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if not validate_password(data['password']):
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if email already exists
        if User.get_by_email(data['email']):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Validate region (now accepts any string)
        if not data.get('region') or not data['region'].strip():
            return jsonify({'error': 'Region is required'}), 400

        # Validate account type
        if data['account_type'] not in ['user', 'admin']:
            return jsonify({'error': 'Invalid account type'}), 400
        
        # Admin registration requires special approval (in production)
        if data['account_type'] == 'admin':
            # You might want to require admin approval or special token
            pass
        
        # Create new user
        user_data = {
            'name': data['name'].strip(),
            'email': data['email'].lower().strip(),
            'password_hash': generate_password_hash(data['password']),
            'phone': data.get('phone', '').strip(),
            'region': data['region'],
            'account_type': data['account_type'],
            'created_at': datetime.now(timezone.utc),
            'last_login': None
        }

        user = User.create(user_data)

        # Log registration event
        Analytics.log_event('user_registration', {
            'user_id': user.id,
            'account_type': user.account_type.value if hasattr(user.account_type, 'value') else user.account_type,
            'region': user.region.value if hasattr(user.region, 'value') else user.region
        }, user_id=user.id)
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user_id': user.id
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user login"""
    try:
        data = request.get_json()

        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        account_type = data.get('account_type', 'user')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Get user by email
        user = User.get_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        # Verify password
        if not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Check account type matches (handle both enum and string)
        user_account_type = user.account_type.value if hasattr(user.account_type, 'value') else user.account_type
        if user_account_type != account_type:
            return jsonify({'error': 'Invalid account type'}), 401

        # Check if account is active (handle both enum and string, default to active if no status)
        if hasattr(user, 'status'):
            user_status = user.status.value if hasattr(user.status, 'value') else user.status
            if user_status != 'active':
                return jsonify({'error': 'Account is not active'}), 401
        
        # Update last login
        User.update_last_login(user.id)
        
        # Create session
        session['user_id'] = user.id
        session['account_type'] = user.account_type.value
        session['login_time'] = datetime.now(timezone.utc).isoformat()
        
        # Cache session data for quick access
        try:
            cache_user_session(user.id, {
                'name': user.name,
                'email': user.email,
                'region': user.region,  # Now string
                'account_type': user.account_type.value
            })
        except:
            # Cache might fail if Redis is not available, continue anyway
            pass
        
        # Log login event
        try:
            Analytics.log_event('user_login', {
                'user_id': user.id,
                'account_type': user.account_type.value
            })
        except:
            # Analytics might fail, continue anyway
            pass

        # Determine redirect URL
        redirect_url = 'analytics.html' if user.account_type.value == 'admin' else 'chatbot.html'

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'account_type': user.account_type.value,
                'region': user.region,  # Now string
                'country': user.country  # New: Include country
            },
            'redirect_url': redirect_url
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        print(f"Exception in login: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Log out current user"""
    try:
        user_id = session.get('user_id')
        
        # Log logout event
        if user_id:
            Analytics.log_event('user_logout', {'user_id': user_id})
        
        # Clear session
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile"""
    try:
        user = User.get_by_id(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'country': user.country,  # New: Include country
                'region': user.region,  # Now string
                'account_type': user.account_type.value,
                'status': user.status.value,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        })
        
    except Exception as e:
        print(f"Profile error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to get profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        # Validate updateable fields
        allowed_fields = ['name', 'phone', 'region']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update user
        User.update(user_id, update_data)
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': 'Profile update failed'}), 500

# Admin-only routes
@auth_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (admin only)"""
    try:
        # Get query parameters for filtering
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        region = request.args.get('region')
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        users, total = User.get_all_paginated(
            page=page,
            per_page=per_page,
            region=region,
            status=status,
            search=search
        )
        
        users_data = []
        for user in users:
            # Get conversation count for each user
            conv_count = Conversation.count_by_user(user.id)

            # Handle Enum values properly
            region_val = user.region.value if hasattr(user.region, 'value') else user.region
            account_type_val = user.account_type.value if hasattr(user.account_type, 'value') else user.account_type
            status_val = user.status.value if hasattr(user.status, 'value') else user.status

            users_data.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'region': region_val,
                'account_type': account_type_val,
                'status': status_val,
                'conversation_count': conv_count,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to get users'}), 500

@auth_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user by admin"""
    try:
        data = request.get_json()
        
        # Admin can update more fields
        allowed_fields = ['name', 'email', 'phone', 'region', 'status', 'account_type']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                if field == 'email' and not validate_email(data[field]):
                    return jsonify({'error': 'Invalid email format'}), 400
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update user
        User.update(user_id, update_data)
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': 'User update failed'}), 500

@auth_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user by admin"""
    try:
        # Prevent self-deletion
        if user_id == session['user_id']:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        # Soft delete - mark as inactive instead of removing
        User.update(user_id, {'status': 'deleted'})
        
        # Log deletion event
        Analytics.log_event('user_deletion', {
            'deleted_user_id': user_id,
            'admin_user_id': session['user_id']
        })
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': 'User deletion failed'}), 500

@auth_bp.route('/admin/export/users', methods=['GET'])
@admin_required
def export_users():
    """Export users data as CSV"""
    try:
        # Get query parameters
        region = request.args.get('region')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        users = User.get_for_export(
            region=region,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = [
            'ID', 'Name', 'Email', 'Phone', 'Region', 'Account Type',
            'Status', 'Conversations', 'Created At', 'Last Login'
        ]
        writer.writerow(headers)
        
        # Write data
        for user in users:
            conv_count = Conversation.count_by_user(user.id)
            writer.writerow([
                user.id,
                user.name,
                user.email,
                user.phone or '',
                user.region,
                user.account_type,
                user.status,
                conv_count,
                user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''
            ])
        
        # Log export event
        Analytics.log_event('data_export', {
            'admin_user_id': session['user_id'],
            'export_type': 'users',
            'record_count': len(users)
        })
        
        return {
            'csv_data': output.getvalue(),
            'filename': f'users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            'record_count': len(users)
        }
        
    except Exception as e:
        return jsonify({'error': 'Export failed'}), 500

@auth_bp.route('/admin/analytics/overview', methods=['GET'])
@admin_required
def get_analytics_overview():
    """Get analytics overview for dashboard"""
    try:
        # Get date range and region filter
        days = request.args.get('days', 30, type=int)
        region = request.args.get('region', 'all')

        # Use the enhanced analytics repository with region filter
        analytics_data = AnalyticsRepository.get_comprehensive_analytics(days, region)

        return jsonify(analytics_data)

    except Exception as e:
        return jsonify({'error': 'Failed to get analytics overview', 'details': str(e)}), 500

@auth_bp.route('/admin/analytics/regional-distribution', methods=['GET'])
@admin_required
def get_regional_distribution():
    """Get regional distribution of users"""
    try:
        from sqlalchemy import func
        from database.models.user import User

        # Get regional distribution with user counts
        regional_data = db.session.query(
            User.region,
            func.count(User.id).label('count')
        ).group_by(User.region).all()

        distribution = {}
        for region, count in regional_data:
            if region:
                # Handle Enum values properly
                region_name = region.value if hasattr(region, 'value') else region
                distribution[region_name] = count

        return jsonify({
            'success': True,
            'distribution': distribution
        })

    except Exception as e:
        return jsonify({'error': 'Failed to get regional distribution', 'details': str(e)}), 500

@auth_bp.route('/admin/analytics/crop-inquiries', methods=['GET'])
@admin_required
def get_crop_inquiries():
    """Get crop inquiry statistics"""
    try:
        from sqlalchemy import func
        from database.models.conversation import Conversation, Message
        from database.models.user import User
        import json

        days = request.args.get('days', 7, type=int)
        region = request.args.get('region', 'all')
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Build base query with region filter
        conv_query = Conversation.query.join(User).filter(
            Conversation.start_time >= cutoff_date,
            Conversation.mentioned_crops.isnot(None)
        )
        if region != 'all':
            conv_query = conv_query.filter(User.region == region)

        # Get all conversations with mentioned crops
        conversations = conv_query.all()

        # Count crop mentions for current period
        crop_counts = {}
        for conv in conversations:
            crops = conv.get_mentioned_crops()
            for crop in crops:
                crop_name = crop.lower().capitalize()
                crop_counts[crop_name] = crop_counts.get(crop_name, 0) + 1

        # Get previous period data for trend calculation
        previous_cutoff = cutoff_date - timedelta(days=days)
        prev_conv_query = Conversation.query.join(User).filter(
            Conversation.start_time >= previous_cutoff,
            Conversation.start_time < cutoff_date,
            Conversation.mentioned_crops.isnot(None)
        )
        if region != 'all':
            prev_conv_query = prev_conv_query.filter(User.region == region)

        previous_conversations = prev_conv_query.all()

        previous_crop_counts = {}
        for conv in previous_conversations:
            crops = conv.get_mentioned_crops()
            for crop in crops:
                crop_name = crop.lower().capitalize()
                previous_crop_counts[crop_name] = previous_crop_counts.get(crop_name, 0) + 1

        # Sort by count and get top crops
        sorted_crops = sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        crop_data = []
        for crop, count in sorted_crops:
            # Calculate trend - compare with previous period
            previous_count = previous_crop_counts.get(crop, 0)
            if previous_count > 0:
                trend_percent = ((count - previous_count) / previous_count) * 100
                if trend_percent > 0:
                    trend = f'+{trend_percent:.0f}%'
                elif trend_percent < 0:
                    trend = f'{trend_percent:.0f}%'
                else:
                    trend = '0%'
            elif count > 0:
                trend = 'New'  # New crop that wasn't in previous period
            else:
                trend = '0%'

            crop_data.append({
                'crop': crop,
                'inquiries': count,
                'trend': trend
            })

        return jsonify({
            'success': True,
            'crops': crop_data
        })

    except Exception as e:
        return jsonify({'error': 'Failed to get crop inquiries', 'details': str(e)}), 500

@auth_bp.route('/admin/analytics/activity-trends', methods=['GET'])
@admin_required
def get_activity_trends():
    """Get user activity trends over time"""
    try:
        from sqlalchemy import func
        from database.models.user import User
        from database.models.conversation import Conversation

        days = request.args.get('days', 7, type=int)
        region = request.args.get('region', 'all')
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Generate date labels
        date_labels = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            date_labels.append(date.strftime('%a'))

        # Get new users per day
        new_users_data = []
        for i in range(days):
            start_date = datetime.utcnow() - timedelta(days=days-i)
            end_date = start_date + timedelta(days=1)

            user_query = User.query.filter(
                User.created_at >= start_date,
                User.created_at < end_date
            )
            if region != 'all':
                user_query = user_query.filter(User.region == region)

            new_users_data.append(user_query.count())

        # Get conversations per day
        conversations_data = []
        for i in range(days):
            start_date = datetime.utcnow() - timedelta(days=days-i)
            end_date = start_date + timedelta(days=1)

            conv_query = Conversation.query.join(User).filter(
                Conversation.start_time >= start_date,
                Conversation.start_time < end_date
            )
            if region != 'all':
                conv_query = conv_query.filter(User.region == region)

            conversations_data.append(conv_query.count())

        return jsonify({
            'success': True,
            'labels': date_labels,
            'new_users': new_users_data,
            'conversations': conversations_data
        })

    except Exception as e:
        return jsonify({'error': 'Failed to get activity trends', 'details': str(e)}), 500


@auth_bp.route('/admin/export/ml-dataset', methods=['GET'])
@admin_required
def export_ml_dataset():
    """
    Export comprehensive ML training dataset

    Returns conversation data with:
    - User questions
    - Bot responses
    - Intent classifications
    - Confidence scores
    - Entities extracted
    - Feedback ratings
    - Sentiment scores

    Perfect for training agricultural chatbot ML models
    """
    try:
        from database.models.conversation import Message
        from database.models.analytics import Feedback

        # Get query parameters
        format_type = request.args.get('format', 'json')  # json or csv
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        min_confidence = request.args.get('min_confidence', type=float)

        # Build query
        query = db.session.query(Message).join(Conversation)

        if start_date:
            query = query.filter(Message.timestamp >= datetime.fromisoformat(start_date))
        if end_date:
            # Include the entire end date by adding 23:59:59
            end_datetime = datetime.fromisoformat(end_date)
            # If no time component, set to end of day
            if end_datetime.hour == 0 and end_datetime.minute == 0 and end_datetime.second == 0:
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(Message.timestamp <= end_datetime)
        if min_confidence:
            query = query.filter(Message.confidence_score >= min_confidence)

        messages = query.order_by(Message.timestamp.asc()).all()

        # Debug: Count messages with images
        image_messages = [m for m in messages if m.has_image]
        logger.info(f"Total messages: {len(messages)}, Messages with images: {len(image_messages)}")
        if image_messages:
            logger.info(f"Image message IDs: {[m.id for m in image_messages]}")
            logger.info(f"Image message timestamps: {[m.timestamp.isoformat() for m in image_messages]}")

        # Pre-load all feedback organized by conversation AND by user
        all_feedback = Feedback.query.all()
        feedback_by_conv = {}
        feedback_by_user = {}
        for fb in all_feedback:
            # Group feedback by conversation_id (integer database ID)
            if fb.conversation_id not in feedback_by_conv:
                feedback_by_conv[fb.conversation_id] = []
            feedback_by_conv[fb.conversation_id].append(fb)

            # Also group by user_id as fallback
            if fb.user_id not in feedback_by_user:
                feedback_by_user[fb.user_id] = []
            feedback_by_user[fb.user_id].append(fb)

        # Build dataset
        dataset = []
        for msg in messages:
            # Get conversation context
            conv = msg.conversation

            # Get feedback for this conversation if available
            # Strategy 1: Try to match by conversation's database ID to feedback's conversation_id
            # Strategy 2: Fallback to matching by user_id
            feedback = None
            if conv and conv.id and conv.id in feedback_by_conv:
                # Get the most recent feedback for this conversation
                conv_feedbacks = feedback_by_conv[conv.id]
                if conv_feedbacks:
                    # Sort by timestamp and get the most recent
                    conv_feedbacks.sort(key=lambda f: f.timestamp if f.timestamp else datetime.min, reverse=True)
                    feedback = conv_feedbacks[0]
            elif conv and conv.user_id and conv.user_id in feedback_by_user:
                # Fallback: Get feedback by user_id if session_id doesn't match
                user_feedbacks = feedback_by_user[conv.user_id]
                if user_feedbacks:
                    # Find feedback closest in time to this message
                    user_feedbacks.sort(key=lambda f: abs((f.timestamp - msg.timestamp).total_seconds()) if f.timestamp else float('inf'))
                    feedback = user_feedbacks[0]

            # Get paired user-bot exchanges
            if msg.message_type == 'user':
                # Find the bot's response
                bot_response = Message.query.filter(
                    Message.conversation_id == msg.conversation_id,
                    Message.message_type == 'bot',
                    Message.timestamp > msg.timestamp
                ).order_by(Message.timestamp.asc()).first()

                # Get image analysis if present
                image_analysis = msg.get_image_analysis() if msg.has_image else None

                # Get base URL for image links
                base_url = request.url_root.rstrip('/') if request else 'http://localhost:5000'

                dataset_entry = {
                    'conversation_id': msg.conversation_id,
                    'message_id': msg.id,
                    'timestamp': msg.timestamp.isoformat(),
                    'user_question': msg.content,
                    'bot_response': bot_response.content if bot_response else None,
                    'intent': msg.intent_classification,
                    'confidence_score': msg.confidence_score,
                    'sentiment_score': msg.sentiment_score,
                    'entities': msg.get_entities(),
                    'user_region': conv.region if conv else None,
                    'conversation_topic': conv.current_topic if conv else None,
                    'mentioned_crops': list(conv.get_mentioned_crops()) if conv and conv.get_mentioned_crops() else [],
                    # Image fields - NEW
                    'has_image': 'Yes' if msg.has_image else 'No',
                    'image_filename': msg.image_filename if msg.has_image else '',
                    'image_url': f"{base_url}{msg.image_url}" if msg.has_image and msg.image_url else '',
                    'image_disease_detected': 'Yes' if (image_analysis and image_analysis.get('diseases')) else 'No',
                    'image_is_healthy': 'Yes' if (image_analysis and image_analysis.get('is_healthy')) else 'No',
                    'image_confidence': f"{image_analysis.get('confidence', 0) * 100:.1f}%" if image_analysis else '',
                    'image_diseases_count': len(image_analysis.get('diseases', [])) if image_analysis else 0,
                    'image_analysis_json': str(image_analysis) if image_analysis else '',
                    # Feedback fields - will be empty for messages without feedback
                    'has_feedback': 'Yes' if feedback else 'No',
                    'feedback_helpful': feedback.helpful if feedback else '',
                    'feedback_overall_rating': feedback.overall_rating if feedback else '',
                    'feedback_accuracy_rating': feedback.accuracy_rating if feedback else '',
                    'feedback_completeness_rating': feedback.completeness_rating if feedback else '',
                    'feedback_comment': feedback.comment if feedback else '',
                    'feedback_improvement_suggestion': feedback.improvement_suggestion if feedback else ''
                }
                dataset.append(dataset_entry)

        # Format response
        if format_type == 'csv':
            # Convert to CSV
            output = io.StringIO()
            if dataset:
                writer = csv.DictWriter(output, fieldnames=dataset[0].keys())
                writer.writeheader()
                for row in dataset:
                    # Flatten nested structures for CSV
                    row_copy = row.copy()
                    row_copy['entities'] = str(row_copy['entities'])
                    row_copy['mentioned_crops'] = ','.join(row_copy['mentioned_crops']) if row_copy['mentioned_crops'] else ''
                    writer.writerow(row_copy)
            else:
                # Return empty CSV with message
                output.write("# No data found for the selected date range\n")
                output.write("# Try expanding your date range or removing filters\n")

            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment;filename=agribot_ml_dataset_{datetime.now().strftime("%Y%m%d")}.csv'}
            )
        else:
            # Return JSON
            return jsonify({
                'success': True,
                'dataset_size': len(dataset),
                'export_date': datetime.now(timezone.utc).isoformat(),
                'data': dataset,
                'metadata': {
                    'total_conversations': Conversation.query.count(),
                    'total_messages': Message.query.count(),
                    'feedback_count': Feedback.query.count(),
                    'date_range': {
                        'start': start_date or 'all',
                        'end': end_date or 'all'
                    }
                }
            })

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"ML dataset export error: {str(e)}\n{error_trace}")
        return jsonify({'error': 'Failed to export ML dataset', 'details': str(e), 'trace': error_trace}), 500


@auth_bp.route('/admin/export/feedback-dataset', methods=['GET'])
@admin_required
def export_feedback_dataset():
    """
    Export feedback data for supervised learning

    Returns labeled data showing which responses were helpful/unhelpful
    Perfect for training response quality classifiers
    """
    try:
        from database.models.analytics import Feedback
        from database.models.conversation import Message

        feedbacks = Feedback.query.all()

        dataset = []
        for fb in feedbacks:
            # Export feedback data directly
            # Note: conversation_id in feedback is session_id from frontend
            dataset.append({
                'feedback_id': fb.id,
                'session_id': fb.conversation_id,  # This is the frontend session ID
                'user_id': fb.user_id,
                'helpful': fb.helpful,
                'overall_rating': fb.overall_rating,
                'accuracy_rating': fb.accuracy_rating,
                'completeness_rating': fb.completeness_rating,
                'comment': fb.comment,
                'improvement_suggestion': fb.improvement_suggestion,
                'timestamp': fb.timestamp.isoformat() if fb.timestamp else None
            })

        # Get format type
        format_type = request.args.get('format', 'json')

        if format_type == 'csv':
            # Convert to CSV
            import io
            import csv

            output = io.StringIO()
            if dataset:
                writer = csv.DictWriter(output, fieldnames=dataset[0].keys())
                writer.writeheader()
                writer.writerows(dataset)

            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=feedback_dataset_{datetime.now().strftime("%Y%m%d")}.csv'
            return response

        return jsonify({
            'success': True,
            'dataset_size': len(dataset),
            'data': dataset
        })

    except Exception as e:
        return jsonify({'error': 'Failed to export feedback dataset', 'details': str(e)}), 500


@auth_bp.route('/admin/export/intent-dataset', methods=['GET'])
@admin_required
def export_intent_dataset():
    """
    Export intent classification dataset

    Returns user messages with their classified intents
    Perfect for training intent classification models
    """
    try:
        from database.models.conversation import Message

        # Get only user messages with intent classifications
        messages = Message.query.filter(
            Message.message_type == 'user',
            Message.intent_classification.isnot(None)
        ).all()

        dataset = []
        for msg in messages:
            dataset.append({
                'text': msg.content,
                'intent': msg.intent_classification,
                'confidence': msg.confidence_score,
                'entities': msg.get_entities(),
                'sentiment': msg.sentiment_score,
                'timestamp': msg.timestamp.isoformat()
            })

        return jsonify({
            'success': True,
            'dataset_size': len(dataset),
            'intents': list(set(msg.intent_classification for msg in messages if msg.intent_classification)),
            'data': dataset
        })

    except Exception as e:
        return jsonify({'error': 'Failed to export intent dataset', 'details': str(e)}), 500

@auth_bp.route('/admin/knowledge-transfer', methods=['GET'])
@admin_required
def get_knowledge_transfer():
    """Get knowledge transfer and user journey analytics"""
    try:
        from database.models.analytics import Feedback
        from collections import Counter

        # Total interactions
        total_conversations = Conversation.query.count()
        total_users = User.query.filter_by(account_type='user').count()

        # User journey stages
        new_users = User.query.filter(User.created_at >= datetime.now(timezone.utc) - timedelta(days=30)).count()
        returning_users = total_users - new_users

        # Knowledge categories (topics discussed)
        all_conversations = Conversation.query.all()
        topics = [conv.current_topic for conv in all_conversations if conv.current_topic]
        topic_distribution = Counter(topics).most_common(10)

        # Regional knowledge spread
        regions = [conv.region for conv in all_conversations if conv.region]
        regional_adoption = Counter(regions).most_common()

        # Learning progression (users with multiple conversations = learning)
        user_conversation_counts = db.session.query(
            Conversation.user_id,
            db.func.count(Conversation.id).label('conv_count')
        ).group_by(Conversation.user_id).all()

        beginners = sum(1 for _, count in user_conversation_counts if count == 1)
        learners = sum(1 for _, count in user_conversation_counts if 2 <= count <= 5)
        experts = sum(1 for _, count in user_conversation_counts if count > 5)

        # Knowledge satisfaction (feedback on learning)
        feedbacks = Feedback.query.all()
        avg_knowledge_rating = sum(f.completeness_rating for f in feedbacks if f.completeness_rating) / len(feedbacks) if feedbacks else 0

        # Most requested knowledge areas (crops)
        all_crops = []
        for conv in all_conversations:
            if hasattr(conv, 'get_mentioned_crops'):
                all_crops.extend(conv.get_mentioned_crops())
        crop_demand = Counter(all_crops).most_common(15)

        return jsonify({
            'success': True,
            'overview': {
                'total_interactions': total_conversations,
                'total_learners': total_users,
                'new_learners_30d': new_users,
                'returning_learners': returning_users,
                'avg_knowledge_satisfaction': round(avg_knowledge_rating, 2)
            },
            'learning_progression': {
                'beginners': beginners,
                'active_learners': learners,
                'advanced_users': experts
            },
            'knowledge_topics': [{'topic': topic, 'count': count} for topic, count in topic_distribution],
            'regional_reach': [{'region': region, 'users': count} for region, count in regional_adoption],
            'crop_knowledge_demand': [{'crop': crop, 'requests': count} for crop, count in crop_demand]
        })

    except Exception as e:
        import traceback
        print(f"[ERROR] Knowledge transfer endpoint:\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to load knowledge transfer data', 'details': str(e)}), 500

@auth_bp.route('/admin/analytics/detailed', methods=['GET'])
@admin_required
def get_detailed_analytics():
    """Get detailed analytics for Analytics tab"""
    logger.info("Analytics detailed endpoint called")
    try:
        from database.models.conversation import Message
        from database.models.analytics import Feedback
        from sqlalchemy import func
        from collections import Counter

        logger.info("Starting analytics queries")

        # Intent distribution
        intents = db.session.query(
            Message.intent_classification,
            func.count(Message.id).label('count')
        ).filter(Message.intent_classification.isnot(None)).group_by(Message.intent_classification).all()

        intent_data = [{'intent': i[0], 'count': i[1]} for i in intents]

        # Hourly activity (messages per hour of day)
        # Use database-agnostic approach
        try:
            # Try PostgreSQL EXTRACT function
            hourly_activity = db.session.query(
                func.extract('hour', Message.timestamp).label('hour'),
                func.count(Message.id).label('count')
            ).group_by('hour').all()
        except:
            # Fallback to SQLite strftime
            hourly_activity = db.session.query(
                func.strftime('%H', Message.timestamp).label('hour'),
                func.count(Message.id).label('count')
            ).group_by('hour').all()

        hourly_data = {int(h[0]): h[1] for h in hourly_activity if h[0]}
        hourly_formatted = [hourly_data.get(h, 0) for h in range(24)]

        # Regional distribution
        regional = db.session.query(
            Conversation.region,
            func.count(Conversation.id).label('count')
        ).filter(Conversation.region.isnot(None)).group_by(Conversation.region).all()

        regional_data = [{'region': r[0], 'count': r[1]} for r in regional]

        # Crop mentions over time (last 30 days)
        crop_mentions = {}
        # Query only mentioned_crops column to avoid loading mentioned_livestock which doesn't exist yet
        import json
        conversations_with_crops = db.session.query(Conversation.mentioned_crops).filter(Conversation.mentioned_crops.isnot(None)).all()
        for (mentioned_crops_json,) in conversations_with_crops:
            if mentioned_crops_json:
                try:
                    crops = json.loads(mentioned_crops_json)
                    for crop in crops:
                        crop_mentions[crop] = crop_mentions.get(crop, 0) + 1
                except:
                    pass

        crop_trends = [{'crop': k, 'mentions': v} for k, v in sorted(crop_mentions.items(), key=lambda x: x[1], reverse=True)[:10]]

        # Response quality metrics
        try:
            # Try with ROUND function (works in PostgreSQL and SQLite)
            confidence_distribution = db.session.query(
                func.round(Message.confidence_score, 1).label('confidence'),
                func.count(Message.id).label('count')
            ).filter(Message.confidence_score.isnot(None)).group_by('confidence').all()
            confidence_data = [{'score': float(c[0]), 'count': c[1]} for c in confidence_distribution if c[0]]
        except:
            # Fallback: just get all confidence scores without rounding
            confidence_distribution = db.session.query(
                Message.confidence_score,
                func.count(Message.id).label('count')
            ).filter(Message.confidence_score.isnot(None)).group_by(Message.confidence_score).all()
            confidence_data = [{'score': float(c[0]), 'count': c[1]} for c in confidence_distribution if c[0]]

        # Sentiment distribution
        sentiment_stats = db.session.query(
            func.avg(Message.sentiment_score).label('avg_sentiment'),
            func.count(Message.id).filter(Message.sentiment_score > 0).label('positive'),
            func.count(Message.id).filter(Message.sentiment_score < 0).label('negative'),
            func.count(Message.id).filter(Message.sentiment_score == 0).label('neutral')
        ).first()

        return jsonify({
            'success': True,
            'intent_distribution': intent_data,
            'hourly_activity': hourly_formatted,
            'regional_distribution': regional_data,
            'crop_trends': crop_trends,
            'confidence_distribution': confidence_data,
            'sentiment': {
                'average': float(sentiment_stats[0]) if sentiment_stats[0] else 0,
                'positive_count': sentiment_stats[1],
                'negative_count': sentiment_stats[2],
                'neutral_count': sentiment_stats[3]
            }
        })

    except Exception as e:
        import traceback
        logger.error(f"Error in analytics detailed: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to fetch detailed analytics', 'details': str(e)}), 500

@auth_bp.route('/admin/recent-activity', methods=['GET'])
@admin_required
def get_recent_activity():
    """Get recent system activity for the activity feed"""
    try:
        from database.models.analytics import Feedback
        from datetime import datetime, timedelta

        activities = []

        # Recent user registrations (last 10)
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        for user in recent_users:
            activities.append({
                'type': 'user_registration',
                'title': 'New User Registered',
                'description': f'{user.name} joined AgriBot',
                'timestamp': user.created_at.isoformat() if user.created_at else datetime.now().isoformat()
            })

        # Recent conversations (last 5)
        recent_convs = Conversation.query.order_by(Conversation.start_time.desc()).limit(5).all()
        for conv in recent_convs:
            user = User.query.get(conv.user_id)
            activities.append({
                'type': 'conversation',
                'title': 'New Conversation',
                'description': f'{user.name if user else "User"} started a conversation',
                'timestamp': conv.start_time.isoformat() if conv.start_time else datetime.now().isoformat()
            })

        # Recent feedback (last 5)
        recent_feedback = Feedback.query.order_by(Feedback.timestamp.desc()).limit(5).all()
        for fb in recent_feedback:
            rating_text = f"{fb.overall_rating}/5 stars" if fb.overall_rating else "feedback"
            activities.append({
                'type': 'feedback',
                'title': 'Feedback Received',
                'description': f'User submitted {rating_text}',
                'timestamp': fb.timestamp.isoformat() if fb.timestamp else datetime.now().isoformat()
            })

        # Sort all activities by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)

        # Return top 15 most recent
        return jsonify({
            'success': True,
            'activities': activities[:15]
        })

    except Exception as e:
        print(f"Error fetching recent activity: {str(e)}")
        return jsonify({'error': 'Failed to fetch activity', 'details': str(e)}), 500

@auth_bp.route('/temp-check-admin', methods=['GET'])
def temp_check_admin():
    """TEMPORARY: Check if admin exists"""
    try:
        email = request.args.get('email', 'shalom.dze-kum@aims-cameroon.org')
        user = User.query.filter_by(email=email).first()

        if user:
            # Get account type safely
            account_type = user.account_type.value if hasattr(user.account_type, 'value') else user.account_type

            # Get status safely
            status = 'unknown'
            if hasattr(user, 'status'):
                status = user.status.value if hasattr(user.status, 'value') else user.status

            return jsonify({
                'exists': True,
                'name': user.name,
                'email': user.email,
                'account_type': account_type,
                'status': status,
                'has_password': bool(user.password_hash),
                'password_hash_length': len(user.password_hash) if user.password_hash else 0
            })
        else:
            return jsonify({'exists': False, 'message': f'No user found with email: {email}'})
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@auth_bp.route('/temp-test-login', methods=['POST'])
def temp_test_login():
    """TEMPORARY: Debug login process step by step"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        account_type = data.get('account_type', 'user')

        debug_info = {
            'step': '',
            'email': email,
            'account_type_requested': account_type
        }

        # Step 1: Find user
        debug_info['step'] = 'Finding user'
        user = User.query.filter_by(email=email).first()

        if not user:
            debug_info['result'] = 'User not found'
            return jsonify(debug_info), 404

        debug_info['user_found'] = True
        debug_info['user_id'] = user.id
        debug_info['user_name'] = user.name

        # Step 2: Check password
        debug_info['step'] = 'Checking password'
        debug_info['has_password_hash'] = bool(user.password_hash)
        password_valid = check_password_hash(user.password_hash, password)
        debug_info['password_valid'] = password_valid

        if not password_valid:
            debug_info['result'] = 'Invalid password'
            return jsonify(debug_info), 401

        # Step 3: Check account type
        debug_info['step'] = 'Checking account type'
        user_account_type = user.account_type.value if hasattr(user.account_type, 'value') else user.account_type
        debug_info['user_account_type'] = user_account_type
        debug_info['account_type_match'] = (user_account_type == account_type)

        if user_account_type != account_type:
            debug_info['result'] = 'Account type mismatch'
            return jsonify(debug_info), 401

        # Step 4: Check status
        debug_info['step'] = 'Checking status'
        if hasattr(user, 'status'):
            user_status = user.status.value if hasattr(user.status, 'value') else user.status
            debug_info['user_status'] = user_status
            debug_info['status_active'] = (user_status == 'active')

            if user_status != 'active':
                debug_info['result'] = 'Account not active'
                return jsonify(debug_info), 401
        else:
            debug_info['user_status'] = 'no status field'

        debug_info['result'] = 'All checks passed - login should work'
        return jsonify(debug_info), 200

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@auth_bp.route('/temp-create-admin-now', methods=['GET'])
def temp_create_admin_now():
    """EMERGENCY: Create admin account instantly via URL"""
    try:
        # Get params from URL
        email = request.args.get('email')
        password = request.args.get('password')
        name = request.args.get('name', 'Admin')
        secret = request.args.get('secret')

        # Security check
        if secret != 'AGRIBOT_TEMP_RESET_2024':
            return jsonify({'error': 'Invalid secret key'}), 403

        if not email or not password:
            return jsonify({'error': 'Email and password required in URL params'}), 400

        # Check if exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({'error': f'User {email} already exists!', 'user_id': existing.id}), 400

        # Create admin
        from database.models.user import AccountType
        admin = User(
            name=name,
            email=email,
            phone=None,
            country='Cameroon',
            region='centre',
            account_type=AccountType.ADMIN,
            password_hash=generate_password_hash(password),
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(admin)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Admin created successfully!',
            'user': {
                'id': admin.id,
                'name': admin.name,
                'email': admin.email,
                'account_type': admin.account_type.value if hasattr(admin.account_type, 'value') else admin.account_type
            }
        })

    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@auth_bp.route('/temp-reset-password', methods=['POST'])
def temp_reset_password():
    """
    TEMPORARY endpoint to reset or create admin account
    TODO: REMOVE THIS ENDPOINT AFTER USE FOR SECURITY
    """
    try:
        data = request.get_json()
        email = data.get('email')
        new_password = data.get('new_password')
        name = data.get('name', 'Admin')
        secret_key = data.get('secret_key')

        # Simple security check - require a secret key
        if secret_key != 'AGRIBOT_TEMP_RESET_2024':
            return jsonify({'error': 'Invalid secret key'}), 403

        if not email or not new_password:
            return jsonify({'error': 'Email and new password required'}), 400

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if user:
            # User exists - reset password
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            action = 'reset'
        else:
            # User doesn't exist - create new admin
            from database.models.user import AccountType
            user = User(
                name=name,
                email=email,
                phone=None,
                country='Cameroon',
                region='centre',
                account_type=AccountType.ADMIN,
                password_hash=generate_password_hash(new_password),
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(user)
            db.session.commit()
            action = 'created'

        logger.info(f"Admin account {action} for user: {email}")

        return jsonify({
            'success': True,
            'action': action,
            'message': f'Admin account {action} successfully!',
            'user': {
                'name': user.name,
                'email': user.email,
                'account_type': user.account_type.value if hasattr(user.account_type, 'value') else user.account_type
            }
        })

    except Exception as e:
        logger.error(f"Error managing admin account: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to manage admin account', 'details': str(e)}), 500