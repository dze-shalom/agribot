"""
Sensor Data API Routes
Location: agribot/app/routes/sensors.py

API endpoints for IoT sensor data interpretation and analysis
"""

from flask import Blueprint, request, jsonify, current_app
from app.routes.auth import login_required
from services.sensor_interpreter import SensorInterpreter
from services.claude_service import ClaudeService
import logging

logger = logging.getLogger(__name__)

sensors_bp = Blueprint('sensors', __name__, url_prefix='/api/sensors')


@sensors_bp.route('/interpret', methods=['POST'])
@login_required
def interpret_sensor_data():
    """
    Interpret sensor readings and provide AI-powered insights

    Request body:
    {
        "fieldId": 1,
        "zoneId": 0,
        "temperature": 28.5,
        "humidity": 65.0,
        "soilMoisture": 450,
        "phValue": 680,
        "npkValue": 250,
        "waterLevel": 80,
        "batteryLevel": 75,
        "pumpStatus": false,
        "signalStrength": -65,
        "cropType": "maize",
        "language": "auto"
    }
    """
    try:
        sensor_data = request.json

        if not sensor_data:
            return jsonify({'error': 'No sensor data provided'}), 400

        # Get parameters
        crop_type = sensor_data.get('cropType', 'default')
        language = sensor_data.get('language', 'auto')
        use_ai = sensor_data.get('useAI', True)

        # Get Claude service if available
        claude_service = None
        if use_ai and hasattr(current_app, 'agribot'):
            try:
                # Try to access Claude service from agribot engine
                claude_service = getattr(current_app.agribot, 'claude_service', None)
            except Exception as e:
                logger.warning(f"Claude service not available: {str(e)}")

        # Initialize sensor interpreter
        interpreter = SensorInterpreter(claude_service=claude_service)

        # Interpret sensor readings
        interpretation = interpreter.interpret_readings(
            sensor_data=sensor_data,
            crop_type=crop_type,
            language=language,
            use_ai=use_ai and claude_service is not None
        )

        return jsonify({
            'success': True,
            'data': interpretation
        })

    except Exception as e:
        logger.error(f"Error interpreting sensor data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sensors_bp.route('/analyze-trends', methods=['POST'])
@login_required
def analyze_trends():
    """
    Analyze trends in historical sensor data

    Request body:
    {
        "historicalData": [
            {
                "temperature": 28.5,
                "humidity": 65.0,
                "soilMoisture": 450,
                "timestamp": "2024-01-01 10:00:00"
            },
            ...
        ],
        "cropType": "maize",
        "language": "auto"
    }
    """
    try:
        data = request.json

        historical_data = data.get('historicalData', [])
        crop_type = data.get('cropType', 'default')
        language = data.get('language', 'auto')

        if not historical_data:
            return jsonify({'error': 'No historical data provided'}), 400

        # Get Claude service
        claude_service = None
        if hasattr(current_app, 'agribot'):
            claude_service = getattr(current_app.agribot, 'claude_service', None)

        # Initialize interpreter
        interpreter = SensorInterpreter(claude_service=claude_service)

        # Analyze trends
        trend_analysis = interpreter.interpret_trends(
            historical_data=historical_data,
            crop_type=crop_type,
            language=language
        )

        return jsonify({
            'success': True,
            'data': trend_analysis
        })

    except Exception as e:
        logger.error(f"Error analyzing trends: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sensors_bp.route('/chat/sensor-context', methods=['POST'])
@login_required
def chat_with_sensor_context():
    """
    Chat with AgriBot with automatic sensor data context

    Request body:
    {
        "message": "Why is my soil so dry?",
        "sensorData": {
            "fieldId": 1,
            "zoneId": 0,
            "temperature": 35.0,
            "soilMoisture": 200,
            ...
        },
        "language": "auto"
    }
    """
    try:
        data = request.json

        user_message = data.get('message', '')
        sensor_data = data.get('sensorData', {})
        language = data.get('language', 'auto')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Build enhanced message with sensor context
        if sensor_data:
            enhanced_message = f"""{user_message}

**Current Sensor Readings:**
- Temperature: {sensor_data.get('temperature', 'N/A')}°C
- Humidity: {sensor_data.get('humidity', 'N/A')}%
- Soil Moisture: {sensor_data.get('soilMoisture', 'N/A')}
- pH: {sensor_data.get('phValue', 0) / 100.0:.2f if sensor_data.get('phValue') else 'N/A'}
- Battery: {sensor_data.get('batteryLevel', 'N/A')}%
"""
        else:
            enhanced_message = user_message

        # Get AgriBot response
        if hasattr(current_app, 'agribot'):
            from flask import session

            response = current_app.agribot.process_message(
                user_input=enhanced_message,
                user_id=session.get('user_id'),
                language=language
            )

            return jsonify({
                'success': True,
                'response': response
            })
        else:
            return jsonify({
                'success': False,
                'error': 'AgriBot engine not available'
            }), 503

    except Exception as e:
        logger.error(f"Error in sensor chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sensors_bp.route('/quick-check', methods=['POST'])
@login_required
def quick_check():
    """
    Quick health check for sensor readings
    Returns simple status without full AI analysis

    Request body:
    {
        "temperature": 28.5,
        "humidity": 65.0,
        "soilMoisture": 450,
        "phValue": 680,
        "batteryLevel": 75
    }
    """
    try:
        sensor_data = request.json

        # Initialize interpreter without Claude for quick check
        interpreter = SensorInterpreter(claude_service=None)

        # Get basic assessment
        alerts = interpreter._generate_alerts(sensor_data, 'default')
        status = interpreter._assess_overall_status(sensor_data, 'default')

        return jsonify({
            'success': True,
            'status': status,
            'alerts': alerts,
            'alertCount': len(alerts)
        })

    except Exception as e:
        logger.error(f"Error in quick check: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sensors_bp.route('/recommendations', methods=['POST'])
@login_required
def get_recommendations():
    """
    Get specific recommendations for sensor readings

    Request body:
    {
        "sensorData": {...},
        "cropType": "maize",
        "language": "en"
    }
    """
    try:
        data = request.json

        sensor_data = data.get('sensorData', {})
        crop_type = data.get('cropType', 'default')
        language = data.get('language', 'en')

        # Initialize interpreter
        interpreter = SensorInterpreter(claude_service=None)

        # Get recommendations
        recommendations = interpreter._get_basic_recommendations(
            sensor_data, crop_type, language
        )

        return jsonify({
            'success': True,
            'recommendations': recommendations
        })

    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sensors_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for sensor service"""
    return jsonify({
        'status': 'healthy',
        'service': 'sensor-interpreter',
        'ai_available': hasattr(current_app, 'agribot') and
                        getattr(current_app.agribot, 'claude_service', None) is not None
    })
