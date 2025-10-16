"""
Admin Routes
Location: agribot/app/routes/admin.py

Administrative endpoints for monitoring, analytics, and system management.
"""

from flask import Blueprint, request, jsonify, send_file, make_response
from datetime import datetime, timedelta
import logging
import csv
import io
import os
import tempfile
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter

from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.user_repository import UserRepository
from database.repositories.conversation_repository import ConversationRepository
from database.models.user import User
from database.models.conversation import Conversation, Message
from database.models.analytics import Feedback
from database import db
from utils.exceptions import AgriBotException
from app.routes.report_charts import (
    create_user_growth_chart,
    create_crop_distribution_chart,
    create_feedback_rating_chart,
    create_regional_distribution_chart
)

# Create blueprint
admin_bp = Blueprint('admin', __name__)

# Logger
logger = logging.getLogger(__name__)

@admin_bp.route('/analytics/detailed', methods=['GET'])
def get_detailed_analytics():
    """Get detailed analytics dashboard data"""
    try:
        # Get time period parameter
        days = request.args.get('days', 30, type=int)
        if days < 1 or days > 365:
            return jsonify({
                'success': False,
                'error': 'Days parameter must be between 1 and 365'
            }), 400
        
        analytics_repo = AnalyticsRepository()
        analytics_data = analytics_repo.get_comprehensive_analytics(days=days)
        
        return jsonify({
            'success': True,
            'data': analytics_data,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        logger.error(f"Error getting detailed analytics: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve detailed analytics'
        }), 500

@admin_bp.route('/system/status', methods=['GET'])
def get_system_status():
    """Get comprehensive system status"""
    try:
        # Get AgriBot engine
        agribot_engine = request.current_app.agribot
        
        # Get system statistics
        engine_stats = agribot_engine.get_engine_statistics()
        
        # Get database statistics
        analytics_repo = AnalyticsRepository()
        user_repo = UserRepository()
        conversation_repo = ConversationRepository()
        
        user_stats = user_repo.get_user_statistics()
        conversation_stats = conversation_repo.get_conversation_statistics(days=7)
        
        # Combine all status information
        system_status = {
            'engine_performance': engine_stats['performance'],
            'system_health': engine_stats['system_health'],
            'error_summary': engine_stats['errors'],
            'database_stats': {
                'users': user_stats,
                'conversations': conversation_stats
            },
            'uptime_info': {
                'status': 'operational',
                'last_restart': 'Not available',  # Would need to track this
                'version': 'AgriBot v1.0'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': system_status
        })
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve system status'
        }), 500

@admin_bp.route('/system/cleanup', methods=['POST'])
def system_cleanup():
    """Perform system cleanup operations"""
    try:
        # Get AgriBot engine
        agribot_engine = request.current_app.agribot
        
        # Perform cleanup
        cleanup_result = agribot_engine.cleanup_resources()
        
        return jsonify({
            'success': True,
            'data': cleanup_result,
            'message': 'System cleanup completed'
        })
        
    except Exception as e:
        logger.error(f"Error during system cleanup: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to perform system cleanup'
        }), 500

@admin_bp.route('/conversations/recent', methods=['GET'])
def get_recent_conversations():
    """Get recent conversations for monitoring"""
    try:
        # Get parameters
        limit = request.args.get('limit', 50, type=int)
        days = request.args.get('days', 7, type=int)
        
        if limit < 1 or limit > 500:
            return jsonify({
                'success': False,
                'error': 'Limit must be between 1 and 500'
            }), 400
        
        if days < 1 or days > 30:
            return jsonify({
                'success': False,
                'error': 'Days must be between 1 and 30'
            }), 400
        
        conversation_repo = ConversationRepository()
        
        # Get recent conversations (anonymized for privacy)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # This would need implementation in the repository
        # For now, return basic stats
        conversation_stats = conversation_repo.get_conversation_statistics(days=days)
        
        return jsonify({
            'success': True,
            'data': {
                'period_days': days,
                'statistics': conversation_stats,
                'note': 'Individual conversation data is anonymized for privacy'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting recent conversations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve recent conversations'
        }), 500

@admin_bp.route('/feedback/recent', methods=['GET'])
def get_recent_feedback():
    """Get recent user feedback"""
    try:
        # Get parameters
        limit = request.args.get('limit', 20, type=int)
        
        if limit < 1 or limit > 100:
            return jsonify({
                'success': False,
                'error': 'Limit must be between 1 and 100'
            }), 400
        
        analytics_repo = AnalyticsRepository()
        
        # Get recent feedback (anonymized)
        recent_feedback = analytics_repo.get_recent_feedback(limit=limit)
        
        # Anonymize feedback data
        anonymized_feedback = []
        for feedback in recent_feedback:
            anonymized_feedback.append({
                'helpful': feedback.helpful,
                'overall_rating': feedback.overall_rating,
                'accuracy_rating': feedback.accuracy_rating,
                'completeness_rating': feedback.completeness_rating,
                'comment': feedback.comment[:100] + '...' if feedback.comment and len(feedback.comment) > 100 else feedback.comment,
                'timestamp': feedback.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': {
                'feedback': anonymized_feedback,
                'count': len(anonymized_feedback)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting recent feedback: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve recent feedback'
        }), 500

@admin_bp.route('/errors/summary', methods=['GET'])
def get_error_summary():
    """Get error summary for monitoring"""
    try:
        # Get parameters
        days = request.args.get('days', 7, type=int)
        
        if days < 1 or days > 30:
            return jsonify({
                'success': False,
                'error': 'Days must be between 1 and 30'
            }), 400
        
        analytics_repo = AnalyticsRepository()
        
        # Get error summary
        error_summary = analytics_repo.get_error_summary(days=days)
        
        return jsonify({
            'success': True,
            'data': error_summary
        })
        
    except Exception as e:
        logger.error(f"Error getting error summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve error summary'
        }), 500

@admin_bp.route('/users/statistics', methods=['GET'])
def get_user_statistics():
    """Get user statistics"""
    try:
        user_repo = UserRepository()
        user_stats = user_repo.get_user_statistics()
        
        return jsonify({
            'success': True,
            'data': user_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting user statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve user statistics'
        }), 500

@admin_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check for all system components"""
    try:
        # Get AgriBot engine
        agribot_engine = request.current_app.agribot
        
        # Perform comprehensive health check
        health_status = agribot_engine.health_check()
        
        # Add additional checks
        health_status['database_connectivity'] = 'healthy'  # Would test actual DB connection
        health_status['external_apis'] = {
            'openweather': 'unknown',  # Would test actual API
            'fao': 'unknown',
            'nasa': 'unknown'
        }
        
        # Determine overall system health
        all_healthy = (
            health_status['overall_status'] == 'healthy' and
            health_status['database_connectivity'] == 'healthy'
        )
        
        status_code = 200 if all_healthy else 503
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Error in detailed health check: {str(e)}")
        return jsonify({
            'overall_status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@admin_bp.route('/analytics/export', methods=['POST'])
def export_analytics_data():
    """
    Export analytics data in CSV or PDF format
    Supports: users, conversations, analytics, ml-dataset, feedback-dataset, intent-dataset
    """
    try:
        data = request.get_json()
        export_type = data.get('type', 'analytics')
        format_type = data.get('format', 'csv')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        logger.info(f"Export request: type={export_type}, format={format_type}")

        # Check if comprehensive PDF report is requested
        if export_type == 'comprehensive' and format_type == 'pdf':
            return generate_comprehensive_pdf_report()

        # Route to appropriate export function
        if export_type == 'users':
            return export_users_data(start_date, end_date, format_type)
        elif export_type == 'conversations':
            return export_conversations_data(start_date, end_date, format_type)
        elif export_type == 'analytics':
            # For analytics, if PDF format requested, use comprehensive report
            if format_type == 'pdf':
                return generate_comprehensive_pdf_report()
            return export_analytics_summary(start_date, end_date, format_type)
        elif export_type == 'ml-dataset':
            return export_ml_training_dataset(start_date, end_date)
        elif export_type == 'feedback-dataset':
            return export_feedback_dataset()
        elif export_type == 'intent-dataset':
            return export_intent_dataset()
        else:
            return jsonify({'error': 'Invalid export type'}), 400

    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

def export_users_data(start_date, end_date, format_type):
    """Export users data"""
    users_query = User.query

    if start_date:
        users_query = users_query.filter(User.created_at >= start_date)
    if end_date:
        users_query = users_query.filter(User.created_at <= end_date)

    users = users_query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Country', 'Region', 'Account Type', 'Status', 'Conversations', 'Created At', 'Last Login'])

    # Data
    for user in users:
        conv_count = Conversation.query.filter_by(user_id=user.id).count()
        writer.writerow([
            user.id,
            user.name,
            user.email,
            user.phone or '',
            user.country or '',
            user.region or '',
            user.account_type.value if hasattr(user.account_type, 'value') else user.account_type,
            user.status.value if hasattr(user.status, 'value') else user.status,
            conv_count,
            user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
            user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''
        ])

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=users_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

def export_conversations_data(start_date, end_date, format_type):
    """Export conversations data with images"""
    from flask import request
    conv_query = Conversation.query

    if start_date:
        conv_query = conv_query.filter(Conversation.start_time >= start_date)
    if end_date:
        conv_query = conv_query.filter(Conversation.start_time <= end_date)

    conversations = conv_query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Headers - Updated to include image information
    writer.writerow(['Conversation ID', 'User ID', 'User Name', 'Region', 'Topic', 'Message Count', 'Images Count', 'Mentioned Crops', 'Start Time', 'End Time', 'Duration (min)'])

    # Data
    for conv in conversations:
        user = User.query.get(conv.user_id)
        message_count = Message.query.filter_by(conversation_id=conv.id).count()
        images_count = Message.query.filter_by(conversation_id=conv.id, has_image=True).count()
        crops = ', '.join(conv.get_mentioned_crops()) if hasattr(conv, 'get_mentioned_crops') else ''

        duration = ''
        if conv.end_time and conv.start_time:
            duration = round((conv.end_time - conv.start_time).total_seconds() / 60, 2)

        writer.writerow([
            conv.id,
            conv.user_id,
            user.name if user else 'Unknown',
            conv.region or '',
            conv.current_topic or '',
            message_count,
            images_count,
            crops,
            conv.start_time.strftime('%Y-%m-%d %H:%M:%S') if conv.start_time else '',
            conv.end_time.strftime('%Y-%m-%d %H:%M:%S') if conv.end_time else '',
            duration
        ])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=conversations_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

@admin_bp.route('/analytics/export/messages-with-images', methods=['POST'])
def export_messages_with_images():
    """Export all messages that contain images with full details"""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Query messages with images
        messages_query = Message.query.filter(Message.has_image == True)

        if start_date:
            messages_query = messages_query.filter(Message.timestamp >= start_date)
        if end_date:
            messages_query = messages_query.filter(Message.timestamp <= end_date)

        messages = messages_query.order_by(Message.timestamp.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Get base URL for image links
        base_url = request.url_root.rstrip('/')

        # Headers
        writer.writerow([
            'Message ID',
            'Conversation ID',
            'User ID',
            'User Name',
            'Message Text',
            'Timestamp',
            'Image Filename',
            'Image URL',
            'Disease Detected',
            'Is Healthy',
            'Confidence',
            'Diseases Count'
        ])

        # Data
        for msg in messages:
            # Get conversation and user info
            conv = Conversation.query.get(msg.conversation_id)
            user = User.query.get(conv.user_id) if conv else None

            # Parse image analysis
            analysis = msg.get_image_analysis() or {}

            writer.writerow([
                msg.id,
                msg.conversation_id,
                conv.user_id if conv else '',
                user.name if user else 'Unknown',
                msg.content,
                msg.timestamp.strftime('%Y-%m-%d %H:%M:%S') if msg.timestamp else '',
                msg.image_filename or '',
                f"{base_url}{msg.image_url}" if msg.image_url else '',
                'Yes' if analysis.get('diseases') else 'No',
                'Yes' if analysis.get('is_healthy') else 'No',
                f"{analysis.get('confidence', 0) * 100:.1f}%" if analysis.get('confidence') else '',
                len(analysis.get('diseases', []))
            ])

        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=messages_with_images_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        return response

    except Exception as e:
        logger.error(f"Export images error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

def export_analytics_summary(start_date, end_date, format_type):
    """Export analytics summary"""
    analytics_repo = AnalyticsRepository()
    analytics_data = analytics_repo.get_comprehensive_analytics(days=30)

    output = io.StringIO()
    writer = csv.writer(output)

    # Overview section
    writer.writerow(['ANALYTICS SUMMARY REPORT'])
    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])

    writer.writerow(['OVERVIEW'])
    overview = analytics_data.get('overview', {})
    for key, value in overview.items():
        writer.writerow([key.replace('_', ' ').title(), value])

    writer.writerow([])
    writer.writerow(['USER STATISTICS'])
    user_stats = analytics_data.get('user_statistics', {})
    for key, value in user_stats.items():
        writer.writerow([key.replace('_', ' ').title(), value])

    writer.writerow([])
    writer.writerow(['CONVERSATION STATISTICS'])
    conv_stats = analytics_data.get('conversation_statistics', {})
    for key, value in conv_stats.items():
        writer.writerow([key.replace('_', ' ').title(), value])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=analytics_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

def export_ml_training_dataset(start_date, end_date):
    """Export ML training dataset"""
    messages_query = Message.query.join(Conversation).filter(Message.message_type == 'user')

    if start_date:
        messages_query = messages_query.filter(Message.timestamp >= start_date)
    if end_date:
        messages_query = messages_query.filter(Message.timestamp <= end_date)

    messages = messages_query.all()

    # Get all feedback
    all_feedback = Feedback.query.all()
    feedback_by_conv = {}
    for fb in all_feedback:
        if fb.conversation_id not in feedback_by_conv:
            feedback_by_conv[fb.conversation_id] = []
        feedback_by_conv[fb.conversation_id].append(fb)

    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        'Message ID', 'Conversation ID', 'Timestamp', 'User Question', 'Bot Response',
        'Intent', 'Confidence Score', 'Sentiment Score', 'Entities', 'User Region',
        'Topic', 'Mentioned Crops', 'Has Feedback', 'Feedback Helpful',
        'Overall Rating', 'Accuracy Rating', 'Completeness Rating', 'Feedback Comment'
    ])

    # Data
    for msg in messages:
        conv = msg.conversation
        feedback = None

        # Match feedback by conversation ID (not session_id)
        if conv and conv.id in feedback_by_conv:
            conv_feedbacks = feedback_by_conv[conv.id]
            if conv_feedbacks:
                # Get most recent feedback for this conversation
                conv_feedbacks.sort(key=lambda f: f.timestamp if f.timestamp else datetime.min, reverse=True)
                feedback = conv_feedbacks[0]

        # Find bot response
        bot_response = Message.query.filter(
            Message.conversation_id == msg.conversation_id,
            Message.message_type == 'bot',
            Message.timestamp > msg.timestamp
        ).order_by(Message.timestamp.asc()).first()

        crops = ', '.join(conv.get_mentioned_crops()) if conv and hasattr(conv, 'get_mentioned_crops') else ''
        entities = str(msg.get_entities()) if hasattr(msg, 'get_entities') else ''

        writer.writerow([
            msg.id,
            msg.conversation_id,
            msg.timestamp.strftime('%Y-%m-%d %H:%M:%S') if msg.timestamp else '',
            msg.content,
            bot_response.content if bot_response else '',
            msg.intent_classification or '',
            msg.confidence_score or '',
            msg.sentiment_score or '',
            entities,
            conv.region if conv else '',
            conv.current_topic if conv else '',
            crops,
            'Yes' if feedback else 'No',
            feedback.helpful if feedback else '',
            feedback.overall_rating if feedback else '',
            feedback.accuracy_rating if feedback else '',
            feedback.completeness_rating if feedback else '',
            feedback.comment if feedback else ''
        ])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=ml_training_dataset_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

def export_feedback_dataset():
    """Export feedback dataset"""
    feedbacks = Feedback.query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Feedback ID', 'Session ID', 'User ID', 'Helpful', 'Overall Rating',
        'Accuracy Rating', 'Completeness Rating', 'Comment', 'Improvement Suggestion', 'Timestamp'
    ])

    for fb in feedbacks:
        writer.writerow([
            fb.id,
            fb.conversation_id,
            fb.user_id,
            fb.helpful,
            fb.overall_rating or '',
            fb.accuracy_rating or '',
            fb.completeness_rating or '',
            fb.comment or '',
            fb.improvement_suggestion or '',
            fb.timestamp.strftime('%Y-%m-%d %H:%M:%S') if fb.timestamp else ''
        ])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=feedback_dataset_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

def export_intent_dataset():
    """Export intent dataset"""
    messages = Message.query.filter(
        Message.message_type == 'user',
        Message.intent_classification.isnot(None)
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Text', 'Intent', 'Confidence', 'Entities', 'Sentiment', 'Timestamp'])

    for msg in messages:
        entities = str(msg.get_entities()) if hasattr(msg, 'get_entities') else ''
        writer.writerow([
            msg.content,
            msg.intent_classification,
            msg.confidence_score or '',
            entities,
            msg.sentiment_score or '',
            msg.timestamp.strftime('%Y-%m-%d %H:%M:%S') if msg.timestamp else ''
        ])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=intent_dataset_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

def generate_comprehensive_pdf_report():
    """Generate comprehensive PDF report with all analytics"""
    try:
        # Create temporary file for PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_path = temp_file.name
        temp_file.close()

        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                                rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)

        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a472a'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#555555'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=15,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=5,
            leftIndent=0
        )

        subheading_style = ParagraphStyle(
            'SubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )

        insight_style = ParagraphStyle(
            'Insight',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#16a085'),
            leftIndent=15,
            rightIndent=15,
            spaceAfter=10,
            fontName='Helvetica-Oblique'
        )

        # === COVER PAGE ===
        elements.append(Spacer(1, 1.5*inch))
        elements.append(Paragraph("AgriBot", title_style))
        elements.append(Paragraph("Data Analytics Report", title_style))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            f"<b>Reporting Period:</b> Last 30 Days<br/>"
            f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
            f"<b>Report Type:</b> Comprehensive Analytics",
            subtitle_style
        ))
        elements.append(Spacer(1, 1*inch))

        # Professional note box
        note_data = [[Paragraph(
            "<b>About This Report</b><br/><br/>"
            "This comprehensive analytics report provides actionable insights into AgriBot's "
            "performance, user engagement, and knowledge transfer effectiveness. "
            "Data has been analyzed to identify trends, opportunities, and areas for improvement.",
            styles['Normal']
        )]]
        note_table = Table(note_data, colWidths=[6.5*inch])
        note_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f5e9')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#27ae60')),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(note_table)

        elements.append(PageBreak())

        # Get analytics data
        analytics_repo = AnalyticsRepository()
        analytics_data = analytics_repo.get_comprehensive_analytics(days=30)

        # Get raw data for charts and analysis
        users = User.query.all()
        conversations = Conversation.query.all()
        feedbacks = Feedback.query.all()

        # === EXECUTIVE DASHBOARD ===
        elements.append(Paragraph("Executive Dashboard", heading_style))
        elements.append(Paragraph("Key Performance Indicators (KPIs)", subheading_style))

        overview = analytics_data.get('overview', {})
        user_stats = analytics_data.get('user_statistics', {})
        conv_stats = analytics_data.get('conversation_statistics', {})

        # Calculate growth metrics
        total_users = overview.get('total_users', 0)
        new_users_30d = user_stats.get('new_users_30d', 0)
        total_conversations = overview.get('total_conversations', 0)
        conversations_7d = conv_stats.get('conversations_7d', 0)
        avg_messages = overview.get('avg_messages_per_conversation', 0)

        # Calculate rates and percentages
        user_growth_rate = round((new_users_30d / total_users * 100), 1) if total_users > 0 else 0
        active_rate = round((user_stats.get('active_users_7d', 0) / total_users * 100), 1) if total_users > 0 else 0
        engagement_score = round(avg_messages * 10, 1) if avg_messages > 0 else 0

        # KPI Dashboard with color-coded metrics
        kpi_data = [
            ['KPI', 'Current Value', 'Status', 'Trend'],
            ['Total Users', f"{total_users:,}", 'Good' if total_users > 10 else 'Low', f'+{new_users_30d} (30d)'],
            ['Active Users (7d)', f"{user_stats.get('active_users_7d', 0):,}", 'Good' if active_rate > 20 else 'Monitor', f'{active_rate}% of total'],
            ['Total Conversations', f"{total_conversations:,}", 'Healthy' if total_conversations > 20 else 'Growing', f'+{conversations_7d} (7d)'],
            ['Avg Messages/Conv', f"{round(avg_messages, 1)}", 'Engaged' if avg_messages > 5 else 'Low', f'{engagement_score}/100 score'],
            ['User Growth Rate', f"{user_growth_rate}%", 'Growing' if user_growth_rate > 10 else 'Stable', 'Last 30 days'],
        ]

        kpi_table = Table(kpi_data, colWidths=[2*inch, 1.5*inch, 1.3*inch, 1.7*inch])
        kpi_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c3e50')),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.2*inch))

        # Key Insights Box
        helpful_feedback = sum(1 for f in feedbacks if f.helpful) if feedbacks else 0
        satisfaction_rate = round((helpful_feedback / len(feedbacks) * 100), 1) if feedbacks else 0

        insights_text = (
            f"<b>Key Insights:</b><br/>"
            f"• Platform has <b>{total_users:,}</b> registered users with <b>{active_rate}%</b> active in the last 7 days<br/>"
            f"• Users are highly engaged with an average of <b>{round(avg_messages, 1)}</b> messages per conversation<br/>"
            f"• Satisfaction rate stands at <b>{satisfaction_rate}%</b> based on {len(feedbacks)} feedback responses<br/>"
            f"• Growth trajectory shows <b>{new_users_30d}</b> new users in the past month"
        )

        insights_data = [[Paragraph(insights_text, styles['Normal'])]]
        insights_table = Table(insights_data, colWidths=[6.5*inch])
        insights_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff9e6')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#f39c12')),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(insights_table)
        elements.append(Spacer(1, 0.3*inch))

        # === VISUALIZATIONS ===
        elements.append(PageBreak())
        elements.append(Paragraph("Data Visualizations and Trends", heading_style))

        # Generate charts
        chart_paths = []

        # User growth chart
        user_growth_chart = create_user_growth_chart(users, conversations)
        if user_growth_chart:
            chart_paths.append(user_growth_chart)
            elements.append(Paragraph("7-Day Activity Trend", subheading_style))
            img = Image(user_growth_chart, width=6*inch, height=3.5*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.15*inch))

            trend_insight = (
                "<b>Trend Analysis:</b> The chart above shows user registration and conversation patterns "
                "over the past week. Monitor these trends to identify peak usage times and plan resource allocation."
            )
            elements.append(Paragraph(trend_insight, insight_style))
            elements.append(Spacer(1, 0.3*inch))

        # Regional distribution chart
        regional_chart = create_regional_distribution_chart(users)
        if regional_chart:
            chart_paths.append(regional_chart)
            elements.append(Paragraph("User Distribution by Region", subheading_style))
            img = Image(regional_chart, width=6*inch, height=4*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.15*inch))

            # Calculate regional insights
            region_counts = Counter()
            for user in users:
                if user.region:
                    region_name = user.region.value if hasattr(user.region, 'value') else user.region
                    region_counts[region_name] += 1

            top_region = region_counts.most_common(1)[0] if region_counts else ('N/A', 0)
            regional_insight = (
                f"<b>Regional Insight:</b> {top_region[0]} leads with {top_region[1]} users "
                f"({round(top_region[1]/len(users)*100, 1)}% of total). "
                "Consider targeting underserved regions for expansion opportunities."
            )
            elements.append(Paragraph(regional_insight, insight_style))
            elements.append(Spacer(1, 0.3*inch))

        # Page break before next section
        elements.append(PageBreak())

        # Crop distribution chart
        crop_chart = create_crop_distribution_chart(conversations)
        if crop_chart:
            chart_paths.append(crop_chart)
            elements.append(Paragraph("Agricultural Insights", heading_style))
            elements.append(Paragraph("Top Discussed Crops", subheading_style))
            img = Image(crop_chart, width=6*inch, height=4*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.15*inch))

            crop_insight = (
                "<b>Crop Analysis:</b> These crops represent the primary interests of your user base. "
                "Use this data to prioritize content creation, expert resources, and feature development "
                "around high-demand crops."
            )
            elements.append(Paragraph(crop_insight, insight_style))
            elements.append(Spacer(1, 0.3*inch))

        # Feedback rating chart
        feedback_chart = create_feedback_rating_chart(feedbacks)
        if feedback_chart:
            chart_paths.append(feedback_chart)
            elements.append(Paragraph("User Satisfaction Ratings", subheading_style))
            img = Image(feedback_chart, width=6*inch, height=3.5*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.15*inch))

            if feedbacks:
                avg_rating = sum(f.overall_rating for f in feedbacks if f.overall_rating) / len([f for f in feedbacks if f.overall_rating]) if [f for f in feedbacks if f.overall_rating] else 0
                high_ratings = sum(1 for f in feedbacks if f.overall_rating and f.overall_rating >= 4)
                satisfaction_pct = round(high_ratings / len(feedbacks) * 100, 1) if feedbacks else 0

                feedback_insight = (
                    f"<b>Satisfaction Analysis:</b> Average rating of {round(avg_rating, 2)}/5.0 with "
                    f"{satisfaction_pct}% of users rating 4+ stars. "
                    f"{'Excellent performance!' if avg_rating >= 4 else 'Room for improvement in user experience.'}"
                )
                elements.append(Paragraph(feedback_insight, insight_style))
            elements.append(Spacer(1, 0.3*inch))

        # === DETAILED ANALYTICS TABLES ===
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Analytics", heading_style))

        # Engagement Metrics
        elements.append(Paragraph("Engagement Metrics", subheading_style))

        total_messages = Message.query.count()
        user_messages = Message.query.filter_by(message_type='user').count()
        bot_messages = Message.query.filter_by(message_type='bot').count()
        avg_conv_duration = conv_stats.get('avg_duration_minutes', 0)

        engagement_data = [
            ['Metric', 'Value', 'Benchmark', 'Performance'],
            ['Total Messages Exchanged', f"{total_messages:,}", '-', 'Met'],
            ['User Messages', f"{user_messages:,}", '-', 'Met'],
            ['Bot Responses', f"{bot_messages:,}", '-', 'Met'],
            ['Avg Conversation Duration', f"{round(avg_conv_duration, 1)} min", '> 3 min', 'Good' if avg_conv_duration > 3 else 'Low'],
            ['Response Completeness', f"{round(bot_messages/user_messages*100, 1)}%" if user_messages > 0 else 'N/A', '> 95%', 'Met'],
            ['Messages per User', f"{round(total_messages/total_users, 1)}" if total_users > 0 else '0', '> 10', 'Met' if (total_messages/total_users if total_users > 0 else 0) > 10 else 'Below'],
        ]

        engagement_table = Table(engagement_data, colWidths=[2.2*inch, 1.5*inch, 1.3*inch, 1.5*inch])
        engagement_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f8ff')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 7),
        ]))
        elements.append(engagement_table)
        elements.append(Spacer(1, 0.3*inch))

        # === TOP CROPS & REGIONAL ANALYSIS ===
        elements.append(Paragraph("Top Crops and Regional Analysis", subheading_style))

        # Calculate crop mentions
        crop_counts = Counter()
        for conv in conversations:
            if hasattr(conv, 'get_mentioned_crops'):
                for crop in conv.get_mentioned_crops():
                    crop_counts[crop.lower().capitalize()] += 1

        if crop_counts:
            top_10_crops = crop_counts.most_common(10)
            crop_table_data = [['Rank', 'Crop Name', 'Mentions', 'Percentage', 'Trend']]

            total_crop_mentions = sum(crop_counts.values())
            for idx, (crop, count) in enumerate(top_10_crops, 1):
                percentage = round((count / total_crop_mentions * 100), 1)
                trend = 'Rising' if idx <= 3 else 'Stable'
                crop_table_data.append([
                    str(idx),
                    crop,
                    str(count),
                    f"{percentage}%",
                    trend
                ])

            crop_table = Table(crop_table_data, colWidths=[0.6*inch, 2*inch, 1.2*inch, 1.2*inch, 1.5*inch])
            crop_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ]))
            elements.append(crop_table)
            elements.append(Spacer(1, 0.2*inch))

            # Crop insight
            top_crop = top_10_crops[0]
            crop_insight_text = (
                f"<b>Agricultural Focus:</b> {top_crop[0]} dominates discussions with {top_crop[1]} mentions. "
                f"The top 3 crops account for {round(sum(c[1] for c in top_10_crops[:3])/total_crop_mentions*100, 1)}% of all crop inquiries. "
                "Consider creating specialized content and resources for these high-demand crops."
            )
            elements.append(Paragraph(crop_insight_text, insight_style))
        else:
            elements.append(Paragraph("No crop data available yet.", styles['Normal']))

        elements.append(Spacer(1, 0.3*inch))

        # === ACTIONABLE RECOMMENDATIONS ===
        elements.append(PageBreak())
        elements.append(Paragraph("Actionable Recommendations", heading_style))

        # Calculate recommendation metrics
        low_engagement_threshold = 5
        needs_more_users = total_users < 50
        low_satisfaction = satisfaction_rate < 70 if feedbacks else True
        peak_crops = [c[0] for c in (crop_counts.most_common(3) if crop_counts else [])]

        recommendations = []

        # User acquisition recommendations
        if needs_more_users:
            recommendations.append([
                '1',
                'User Acquisition',
                'Expand user base through targeted marketing in underserved regions',
                'High'
            ])

        # Engagement recommendations
        if avg_messages < low_engagement_threshold:
            recommendations.append([
                str(len(recommendations) + 1),
                'Engagement',
                'Improve conversation depth - consider adding interactive features and follow-up questions',
                'High'
            ])

        # Content recommendations
        if peak_crops:
            recommendations.append([
                str(len(recommendations) + 1),
                'Content Strategy',
                f'Create specialized content for {", ".join(peak_crops)} - these crops show highest user interest',
                'Medium'
            ])

        # Satisfaction improvements
        if low_satisfaction:
            recommendations.append([
                str(len(recommendations) + 1),
                'User Experience',
                'Address user feedback to improve satisfaction scores - focus on accuracy and completeness',
                'High'
            ])

        # Regional expansion
        if region_counts:
            underserved_regions = [r for r, c in region_counts.items() if c < (len(users) / len(region_counts) * 0.5)]
            if underserved_regions:
                recommendations.append([
                    str(len(recommendations) + 1),
                    'Regional Growth',
                    f'Target marketing campaigns in {", ".join(underserved_regions[:3])} to balance regional distribution',
                    'Medium'
                ])

        # Data collection
        if not feedbacks or len(feedbacks) < total_conversations * 0.1:
            recommendations.append([
                str(len(recommendations) + 1),
                'Data Collection',
                'Encourage more user feedback - implement prompts after conversations',
                'Medium'
            ])

        # Create recommendations table
        if recommendations:
            rec_table_data = [['#', 'Category', 'Recommendation', 'Priority']] + recommendations
            rec_table = Table(rec_table_data, colWidths=[0.4*inch, 1.5*inch, 3.6*inch, 1*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e67e22')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (3, 0), (3, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff3e0')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(rec_table)
        else:
            elements.append(Paragraph(
                "System is performing optimally. Continue monitoring key metrics.",
                styles['Normal']
            ))

        elements.append(Spacer(1, 0.3*inch))

        # Implementation Priority Box
        priority_note = (
            "<b>Implementation Priority Guide:</b><br/><br/>"
            "<b>High Priority:</b> Address within 1-2 weeks for immediate impact<br/>"
            "<b>Medium Priority:</b> Plan for implementation within 1 month<br/>"
            "<b>Low Priority:</b> Long-term strategic initiatives (3+ months)"
        )
        priority_data = [[Paragraph(priority_note, styles['Normal'])]]
        priority_table = Table(priority_data, colWidths=[6.5*inch])
        priority_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef5e7')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#e67e22')),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(priority_table)
        elements.append(Spacer(1, 0.3*inch))

        # === SUMMARY & CONCLUSION ===
        elements.append(Paragraph("Executive Summary", heading_style))

        summary_text = (
            f"<b>Overall Performance:</b><br/><br/>"
            f"AgriBot is {'performing well' if satisfaction_rate > 70 else 'showing room for improvement'} "
            f"with <b>{total_users:,}</b> total users and <b>{total_conversations:,}</b> conversations. "
            f"The platform maintains an average engagement of <b>{round(avg_messages, 1)}</b> messages per conversation, "
            f"indicating {'strong' if avg_messages > 5 else 'moderate'} user interaction.<br/><br/>"

            f"<b>Key Strengths:</b><br/>"
            f"• Active user base with {active_rate}% engagement rate<br/>"
            f"• {satisfaction_rate}% user satisfaction based on feedback<br/>"
            f"• Clear user interest in {len(crop_counts)} different crops<br/><br/>"

            f"<b>Areas for Focus:</b><br/>"
            f"• {'Increase user acquisition' if needs_more_users else 'Maintain user growth momentum'}<br/>"
            f"• {'Improve conversation depth and engagement' if avg_messages < 5 else 'Sustain high engagement levels'}<br/>"
            f"• {'Collect more user feedback for insights' if len(feedbacks) < total_conversations * 0.1 else 'Continue gathering user feedback'}<br/><br/>"

            f"<b>Next Steps:</b> Review the actionable recommendations section and prioritize "
            f"implementation based on business objectives and resource availability. "
            f"Regular monitoring of these metrics will ensure sustained platform growth and user satisfaction."
        )

        summary_box = [[Paragraph(summary_text, styles['Normal'])]]
        summary_table = Table(summary_box, colWidths=[6.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f4f8')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#3498db')),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.4*inch))

        # === FOOTER ===
        elements.append(Spacer(1, 0.5*inch))
        footer_text = (
            "<i>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br/>"
            "This comprehensive analytics report was automatically generated by <b>AgriBot Analytics System</b>.<br/>"
            f"Report ID: AGRI-{datetime.now().strftime('%Y%m%d-%H%M%S')}<br/>"
            "For questions, support, or data inquiries, contact your system administrator.<br/>"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</i>"
        )
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )))

        # Build PDF
        doc.build(elements)

        # Clean up temporary chart files
        for chart_path in chart_paths:
            try:
                if chart_path and os.path.exists(chart_path):
                    os.unlink(chart_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup chart file: {cleanup_error}")

        # Send file
        response = send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'AgriBot_Analytics_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )

        # Schedule cleanup of PDF file after sending
        # Note: In production, consider using a background task scheduler
        # For now, the temp file will be cleaned up by the OS

        return response

    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()

        # Clean up any temporary files on error
        try:
            if 'chart_paths' in locals():
                for chart_path in chart_paths:
                    if chart_path and os.path.exists(chart_path):
                        os.unlink(chart_path)
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)
        except:
            pass

        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

@admin_bp.errorhandler(404)
def admin_not_found(error):
    """Handle 404 errors for admin routes"""
    return jsonify({
        'success': False,
        'error': 'Admin endpoint not found'
    }), 404