"""
Chat Routes
Location: agribot/app/routes/chat.py

Flask routes for chat functionality and real-time conversation handling.
"""

from flask import Blueprint, request, jsonify, session, current_app, send_from_directory
from datetime import datetime
import uuid
import logging
import os

from core.agribot_engine import AgriBotEngine
from database.repositories.analytics_repository import AnalyticsRepository
from database.models.conversation import Conversation, Message
from database import db
from utils.exceptions import AgriBotException
from utils.validators import validate_chat_input
from services.plant_id_service import PlantIdService

# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Logger
logger = logging.getLogger(__name__)

@chat_bp.route('/message', methods=['POST'])
def process_message():
    """Process user message and return bot response"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate input
        validation_result = validate_chat_input(data)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['error']}), 400
        
        # Extract parameters
        message = data.get('message', '').strip()
        user_name = data.get('user_name', 'Friend')
        user_region = data.get('user_region', 'centre').lower()
        language = data.get('language', 'en')
        include_external_data = data.get('include_external_data', True)

        # Get or create user session
        # If logged in, use authenticated user_id, otherwise use session UUID
        if 'user_id' in session:
            # Logged in user - use their database ID
            user_id = session['user_id']
        else:
            # Anonymous user - create session UUID
            # Note: Conversations for anonymous users won't persist
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id

        # Get AgriBot engine from app context
        agribot_engine = current_app.agribot

        # Process message
        response_data = agribot_engine.process_message(
            message=message,
            user_id=user_id,
            user_name=user_name,
            user_region=user_region,
            language=language,
            include_external_data=include_external_data
        )
        
        # Return response
        return jsonify({
            'success': True,
            'data': response_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except AgriBotException as e:
        logger.error(f"AgriBot error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'agribot_error'
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred',
            'error_type': 'server_error'
        }), 500

@chat_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for conversation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No feedback data provided'}), 400

        # Get user session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No active session'}), 400

        # Extract feedback data
        helpful = data.get('helpful')  # Boolean
        overall_rating = data.get('overall_rating')  # 1-5
        accuracy_rating = data.get('accuracy_rating')  # 1-5
        completeness_rating = data.get('completeness_rating')  # 1-5
        comment = data.get('comment', '').strip()
        improvement_suggestion = data.get('improvement_suggestion', '').strip()
        conversation_id = data.get('conversation_id')

        # Validate conversation_id is an integer
        if conversation_id:
            # Check if it's a fake session ID (starts with 'session_')
            if isinstance(conversation_id, str) and conversation_id.startswith('session_'):
                return jsonify({'error': 'Invalid conversation ID - please send a message first'}), 400

            # Try to convert to integer
            try:
                conversation_id = int(conversation_id)
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid conversation ID format'}), 400
        
        # Validate ratings
        for rating_name, rating_value in [
            ('overall_rating', overall_rating),
            ('accuracy_rating', accuracy_rating), 
            ('completeness_rating', completeness_rating)
        ]:
            if rating_value is not None and (not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5):
                return jsonify({'error': f'{rating_name} must be between 1 and 5'}), 400
        
        # Store feedback
        analytics_repo = AnalyticsRepository()
        
        feedback = analytics_repo.add_feedback(
            conversation_id=conversation_id,
            user_id=user_id,
            helpful=helpful,
            overall_rating=overall_rating,
            accuracy_rating=accuracy_rating,
            completeness_rating=completeness_rating,
            comment=comment if comment else None,
            improvement_suggestion=improvement_suggestion if improvement_suggestion else None
        )
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback.id
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to submit feedback'
        }), 500

@chat_bp.route('/conversation/summary', methods=['GET'])
def get_conversation_summary():
    """Get summary of current conversation"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No active session'}), 400
        
        # Get AgriBot engine
        agribot_engine = current_app.agribot
        
        # Get conversation summary
        summary = agribot_engine.get_user_conversation_summary(user_id)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get conversation summary'
        }), 500

@chat_bp.route('/conversation/end', methods=['POST'])
def end_conversation():
    """End current conversation session"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No active session'}), 400

        # Get AgriBot engine
        agribot_engine = current_app.agribot

        # End conversation
        result = agribot_engine.end_user_conversation(user_id)

        # Clear session
        session.pop('user_id', None)

        return jsonify({
            'success': True,
            'data': result,
            'message': 'Conversation ended successfully'
        })

    except Exception as e:
        logger.error(f"Error ending conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to end conversation'
        }), 500

@chat_bp.route('/conversation/new', methods=['POST'])
def new_conversation():
    """Start a new conversation (user clicks 'New Chat' button)"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No active session'}), 400

        # Clear the current conversation from session
        # This forces creation of a new conversation on next message
        session.pop('conversation_id', None)

        # Also end the conversation in memory (ConversationManager)
        try:
            agribot_engine = current_app.agribot
            agribot_engine.conversation_manager._end_conversation_session(user_id)
        except:
            pass  # Ignore if conversation doesn't exist

        logger.info(f"New conversation started for user {user_id}")

        return jsonify({
            'success': True,
            'message': 'New conversation started. Your next message will create a fresh conversation.'
        })

    except Exception as e:
        logger.error(f"Error starting new conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to start new conversation'
        }), 500

@chat_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """Get follow-up suggestions for current conversation context"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            # Return default suggestions for new users
            suggestions = [
                "Ask about crop diseases",
                "Get planting advice",
                "Learn about fertilizers", 
                "Weather information for farming"
            ]
            return jsonify({
                'success': True,
                'data': {
                    'suggestions': suggestions,
                    'context': 'default'
                }
            })
        
        # Get AgriBot engine
        agribot_engine = current_app.agribot
        
        # Get conversation-specific suggestions
        conversation_manager = agribot_engine.conversation_manager
        suggested_topics = conversation_manager.suggest_next_topics(user_id)
        
        # Convert topics to user-friendly suggestions
        topic_to_suggestion = {
            'disease_identification': 'Help identify crop diseases',
            'pest_control': 'Learn about pest management',
            'fertilizer_advice': 'Get fertilizer recommendations',
            'planting_guidance': 'Planting procedures and timing',
            'harvest_timing': 'When and how to harvest',
            'yield_optimization': 'Tips to increase crop yields',
            'weather_inquiry': 'Weather advice for farming',
            'market_information': 'Market prices and selling tips'
        }
        
        suggestions = [topic_to_suggestion.get(topic, f"Learn about {topic}") 
                      for topic in suggested_topics]
        
        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions,
                'context': 'contextual'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get suggestions'
        }), 500

@chat_bp.route('/conversations/list', methods=['GET'])
def list_conversations():
    """Get list of user's conversation history"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No active session'}), 400

        from database.models.conversation import Conversation, Message
        from database import db

        # Get all conversations for user, ordered by most recent
        conversations = Conversation.query.filter_by(user_id=user_id)\
            .order_by(Conversation.start_time.desc())\
            .limit(50)\
            .all()

        # Format conversation data
        conversation_list = []
        for conv in conversations:
            # Get first user message as preview
            first_message = Message.query.filter_by(
                conversation_id=conv.id,
                message_type='user'
            ).first()

            preview = first_message.content[:50] + '...' if first_message and len(first_message.content) > 50 else (first_message.content if first_message else 'No messages')

            conversation_list.append({
                'id': conv.id,
                'title': conv.title,
                'preview': preview,
                'start_time': conv.start_time.isoformat(),
                'message_count': conv.message_count,
                'current_topic': conv.current_topic
            })

        return jsonify({
            'success': True,
            'data': {
                'conversations': conversation_list,
                'total': len(conversation_list)
            }
        })

    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve conversations'
        }), 500

@chat_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation with all messages"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No active session'}), 400

        from database.models.conversation import Conversation, Message
        from database import db

        # Get conversation and verify ownership
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()

        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404

        # Get all messages for this conversation
        messages = Message.query.filter_by(conversation_id=conversation_id)\
            .order_by(Message.timestamp.asc())\
            .all()

        # Format messages
        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg.id,
                'content': msg.content,
                'type': msg.message_type,
                'timestamp': msg.timestamp.isoformat(),
                'intent': msg.intent_classification,
                'confidence': msg.confidence_score
            })

        return jsonify({
            'success': True,
            'data': {
                'conversation': {
                    'id': conversation.id,
                    'title': conversation.title,
                    'start_time': conversation.start_time.isoformat(),
                    'current_topic': conversation.current_topic,
                    'message_count': conversation.message_count
                },
                'messages': message_list
            }
        })

    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve conversation'
        }), 500

@chat_bp.route('/conversations/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a specific conversation"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No active session'}), 400

        from database.models.conversation import Conversation
        from database import db

        # Get conversation and verify ownership
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()

        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404

        # Delete conversation (messages will cascade delete)
        db.session.delete(conversation)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Conversation deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to delete conversation'
        }), 500

@chat_bp.route('/message-with-image', methods=['POST'])
def message_with_image():
    """
    Send a message with an attached image for disease detection
    Requires both message text and image file
    """
    try:
        import os
        from werkzeug.utils import secure_filename
        from database.models.conversation import Conversation, Message
        from database.repositories.conversation_repository import ConversationRepository

        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Get message text (REQUIRED)
        message_text = request.form.get('message', '').strip()
        if not message_text:
            return jsonify({'error': 'Message text is required with image upload'}), 400

        # Validate file size (max 10MB)
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        if file_size > 10 * 1024 * 1024:
            return jsonify({'error': 'Image size must be less than 10MB'}), 400

        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400

        # Get user session
        user_id = session.get('user_id')
        if not user_id:
            session['user_id'] = str(uuid.uuid4())
            user_id = session['user_id']

        # Get user info
        user_name = request.form.get('user_name', 'Friend')
        user_region = request.form.get('user_region', 'centre')
        language = request.form.get('language', 'auto')

        # Create uploads directory if it doesn't exist
        upload_folder = os.path.join(os.getcwd(), 'uploads', 'plant_images')
        os.makedirs(upload_folder, exist_ok=True)

        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)

        # Save the file
        file.seek(0)
        file.save(file_path)
        logger.info(f"Image saved to {file_path}")

        # Read image data for analysis
        with open(file_path, 'rb') as f:
            image_data = f.read()

        # Initialize Plant.id service
        plant_service = PlantIdService()

        # Analyze image
        logger.info(f"Analyzing plant image for user {user_id}")
        health_data = plant_service.identify_health(image_data, language=language)

        # Format response
        response_text = plant_service.format_response_text(health_data)

        # Get or create conversation (one per session until user clicks "New Chat")
        conversation_repo = ConversationRepository()
        conversation_id = session.get('conversation_id')
        conversation = None

        if conversation_id:
            conversation = conversation_repo.get_by_id(conversation_id)

        if not conversation:
            conversation = conversation_repo.create_conversation(
                user_id=user_id,
                region=user_region
            )
            session['conversation_id'] = conversation.id

        # Save user message with image
        user_message = Message(
            conversation_id=conversation.id,
            content=message_text,
            message_type='user',
            has_image=True,
            image_path=file_path,
            image_filename=filename,
            image_url=f'/uploads/plant_images/{unique_filename}',
            intent_classification='disease_identification'
        )

        # Save image analysis results
        user_message.set_image_analysis(health_data)

        from database import db
        db.session.add(user_message)
        db.session.commit()

        # Save bot response
        bot_message = Message(
            conversation_id=conversation.id,
            content=response_text,
            message_type='bot',
            confidence_score=health_data.get('confidence', 0.0)
        )
        db.session.add(bot_message)
        db.session.commit()

        # Update conversation
        conversation.message_count += 2
        db.session.commit()

        # Determine confidence
        confidence = health_data.get('confidence', 0.0)
        if health_data.get('fallback'):
            confidence = 0.5

        return jsonify({
            'success': True,
            'data': {
                'response': response_text,
                'conversation_id': conversation.id,
                'user_message_id': user_message.id,
                'bot_message_id': bot_message.id,
                'image_saved': True,
                'image_url': user_message.image_url,
                'metadata': {
                    'intent': 'disease_identification',
                    'confidence': confidence,
                    'image_received': True,
                    'is_healthy': health_data.get('is_healthy'),
                    'diseases_count': len(health_data.get('diseases', []))
                },
                'suggestions': health_data.get('suggestions', [])
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error processing image message: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to process image message'
        }), 500

@chat_bp.route('/analyze-image', methods=['POST'])
def analyze_image():
    """
    Analyze uploaded plant image for disease detection
    Now saves images to database for export functionality
    """
    try:
        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Validate file size (max 10MB)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > 10 * 1024 * 1024:
            return jsonify({'error': 'Image size must be less than 10MB'}), 400

        # Get user session
        user_id = session.get('user_id')
        if not user_id:
            session['user_id'] = str(uuid.uuid4())
            user_id = session['user_id']

        # Get user info and optional message
        language = request.form.get('language', 'auto')
        user_message_text = request.form.get('message', '').strip()

        # Get or create conversation (one per session until user clicks "New Chat")
        conversation_id = session.get('conversation_id')
        conversation = None
        if conversation_id:
            conversation = Conversation.query.get(conversation_id)

        if not conversation:
            conversation = Conversation(
                session_id=str(uuid.uuid4()),
                user_id=user_id,
                current_topic='disease_identification'
            )
            db.session.add(conversation)
            db.session.commit()
            session['conversation_id'] = conversation.id

        # Read image data
        image_data = file.read()
        filename = file.filename

        # Save image to filesystem
        upload_folder = os.path.join(os.getcwd(), 'uploads', 'plant_images')
        os.makedirs(upload_folder, exist_ok=True)

        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)

        # Write image to disk
        with open(file_path, 'wb') as f:
            f.write(image_data)

        # Initialize Plant.id service
        plant_service = PlantIdService()

        # Analyze image
        logger.info(f"Analyzing plant image for user {user_id}")
        health_data = plant_service.identify_health(image_data, language=language)

        # Format response
        response_text = plant_service.format_response_text(health_data)

        # Determine confidence
        confidence = health_data.get('confidence', 0.0)
        if health_data.get('fallback'):
            confidence = 0.5

        # Save user message WITH image to database
        # Use user's message text if provided, otherwise use default message
        message_content = user_message_text if user_message_text else "[Image uploaded for disease identification]"

        user_message = Message(
            conversation_id=conversation.id,
            content=message_content,
            message_type='user',
            has_image=True,
            image_path=file_path,
            image_filename=filename,
            image_url=f'/uploads/plant_images/{unique_filename}',
            intent_classification='disease_identification',
            confidence_score=confidence
        )
        user_message.set_image_analysis(health_data)
        db.session.add(user_message)

        # Save bot response
        bot_message = Message(
            conversation_id=conversation.id,
            content=response_text,
            message_type='bot',
            intent_classification='disease_identification',
            confidence_score=confidence
        )
        db.session.add(bot_message)

        db.session.commit()
        logger.info(f"Image saved to database: {unique_filename}")

        # IMPORTANT: Update Claude's conversation memory so it remembers this image analysis
        try:
            agribot_engine = current_app.agribot
            if hasattr(agribot_engine, 'claude_service') and agribot_engine.claude_service:
                # Update Claude's conversation context with the image analysis
                agribot_engine.claude_service._update_conversation_context(
                    str(conversation.id),
                    message_content,  # User's message about the image
                    f"I analyzed the plant image. {response_text}"  # Bot's analysis response
                )
                logger.info(f"Updated Claude conversation context for conversation {conversation.id}")
        except Exception as ctx_error:
            logger.warning(f"Failed to update Claude conversation context: {str(ctx_error)}")

        return jsonify({
            'success': True,
            'data': {
                'response': response_text,
                'metadata': {
                    'intent': 'disease_identification',
                    'confidence': confidence,
                    'image_received': True,
                    'is_healthy': health_data.get('is_healthy'),
                    'diseases_count': len(health_data.get('diseases', [])),
                    'image_saved': True,
                    'image_url': f'/uploads/plant_images/{unique_filename}'
                }
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze image'
        }), 500

@chat_bp.route('/message/stream', methods=['POST'])
def process_message_stream():
    """Process user message with streaming response (can be cancelled)"""
    try:
        from flask import Response, stream_with_context

        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        message = data.get('message', '').strip()
        user_name = data.get('user_name', 'Friend')
        user_region = data.get('user_region', 'centre').lower()
        language = data.get('language', 'en')

        if 'user_id' in session:
            user_id = session['user_id']
        else:
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id

        # Get AgriBot engine
        agribot_engine = current_app.agribot

        def generate():
            """Generator function for streaming response"""
            try:
                # Process with streaming
                response_stream = agribot_engine.process_message_stream(
                    message=message,
                    user_id=user_id,
                    user_name=user_name,
                    user_region=user_region,
                    language=language
                )

                # Stream chunks to client
                for chunk in response_stream:
                    yield f"data: {chunk}\n\n"

                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        logger.error(f"Streaming setup error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/health', methods=['GET'])
def chat_health():
    """Health check for chat functionality"""
    try:
        # Get AgriBot engine
        agribot_engine = current_app.agribot

        # Perform health check
        health_status = agribot_engine.health_check()

        # Determine HTTP status code
        status_code = 200
        if health_status['overall_status'] == 'degraded':
            status_code = 206  # Partial Content
        elif health_status['overall_status'] == 'unhealthy':
            status_code = 503  # Service Unavailable

        return jsonify(health_status), status_code

    except Exception as e:
        logger.error(f"Error in chat health check: {str(e)}")
        return jsonify({
            'overall_status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503