from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os
from agribot_engine import AgriBotEngine
from ml_models import ResponseGenerator

app = Flask(__name__)

agribot_engine = AgriBotEngine()
response_generator = ResponseGenerator(agribot_engine)

# Store data (in production, use a database)
conversations = []
feedback_data = []
user_sessions = {}

@app.route('/')
def home():
    """Main testing interface"""
    return render_template('chat_interface.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_region = data.get('region', 'centre')
        user_role = data.get('role', 'farmer')
        user_name = data.get('user_name', 'anonymous')
        
        if not message.strip():
            return jsonify({'error': 'Empty message'}), 400
        
        response = response_generator.generate_response(message, user_region, user_role)
        
        conversation = {
            'id': len(conversations) + 1,
            'timestamp': datetime.now().isoformat(),
            'user_name': user_name,
            'user_message': message,
            'bot_response': response['answer'],
            'intent': response['intent'],
            'confidence': response['confidence'],
            'entities': response['entities_found'],
            'user_region': user_region,
            'user_role': user_role,
            'suggestions': response['suggestions'],
            'feedback_received': False
        }
        
        conversations.append(conversation)
        
        return jsonify({
            'response': response['answer'],
            'intent': response['intent'],
            'confidence': response['confidence'],
            'suggestions': response['suggestions'],
            'conversation_id': conversation['id']
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit detailed user feedback"""
    try:
        data = request.get_json()
        
        feedback = {
            'id': len(feedback_data) + 1,
            'conversation_id': data.get('conversation_id'),
            'helpful': data.get('helpful'),
            'rating': data.get('rating', 0),
            'accuracy_rating': data.get('accuracy_rating', 0),
            'completeness_rating': data.get('completeness_rating', 0),
            'clarity_rating': data.get('clarity_rating', 0),
            'comment': data.get('comment', '').strip(),
            'improvement_suggestion': data.get('improvement_suggestion', '').strip(),
            'would_recommend': data.get('would_recommend', False),
            'timestamp': datetime.now().isoformat()
        }
        
        feedback_data.append(feedback)
        
        # Update conversation to mark feedback received
        for conv in conversations:
            if conv['id'] == feedback['conversation_id']:
                conv['feedback_received'] = True
                break
        
        return jsonify({'success': True, 'message': 'Thank you for your detailed feedback!'})
        
    except Exception as e:
        print(f"Feedback error: {e}")
        return jsonify({'error': 'Failed to save feedback'}), 500

@app.route('/api/analytics')
def get_analytics():
    """Get comprehensive analytics data"""
    total_conversations = len(conversations)
    total_feedback = len(feedback_data)
    
    # Calculate satisfaction metrics
    helpful_feedback = [f for f in feedback_data if f.get('helpful') == True]
    helpful_percentage = (len(helpful_feedback) / total_feedback * 100) if total_feedback > 0 else 0
    
    # Calculate average ratings
    ratings = [f['rating'] for f in feedback_data if f.get('rating', 0) > 0]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    accuracy_ratings = [f['accuracy_rating'] for f in feedback_data if f.get('accuracy_rating', 0) > 0]
    avg_accuracy = sum(accuracy_ratings) / len(accuracy_ratings) if accuracy_ratings else 0
    
    completeness_ratings = [f['completeness_rating'] for f in feedback_data if f.get('completeness_rating', 0) > 0]
    avg_completeness = sum(completeness_ratings) / len(completeness_ratings) if completeness_ratings else 0
    
    # Intent distribution
    intent_counts = {}
    confidence_by_intent = {}
    for conv in conversations:
        intent = conv['intent']
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
        if intent not in confidence_by_intent:
            confidence_by_intent[intent] = []
        confidence_by_intent[intent].append(conv['confidence'])
    
    # Calculate avg confidence per intent
    avg_confidence_by_intent = {}
    for intent, confidences in confidence_by_intent.items():
        avg_confidence_by_intent[intent] = sum(confidences) / len(confidences)
    
    # Region distribution
    region_counts = {}
    for conv in conversations:
        region = conv['user_region']
        region_counts[region] = region_counts.get(region, 0) + 1
    
    # Role distribution
    role_counts = {}
    for conv in conversations:
        role = conv['user_role']
        role_counts[role] = role_counts.get(role, 0) + 1
    
    # Feedback response rate
    feedback_rate = (total_feedback / total_conversations * 100) if total_conversations > 0 else 0
    
    # Recent feedback comments
    recent_feedback = sorted(feedback_data, key=lambda x: x['timestamp'], reverse=True)[:10]
    
    # Common issues (negative feedback)
    negative_feedback = [f for f in feedback_data if not f.get('helpful', True)]
    
    analytics = {
        'overview': {
            'total_conversations': total_conversations,
            'total_feedback': total_feedback,
            'feedback_response_rate': round(feedback_rate, 1),
            'helpful_percentage': round(helpful_percentage, 1),
            'average_rating': round(avg_rating, 1),
            'average_accuracy': round(avg_accuracy, 1),
            'average_completeness': round(avg_completeness, 1)
        },
        'intent_analysis': {
            'distribution': intent_counts,
            'confidence_by_intent': {k: round(v, 2) for k, v in avg_confidence_by_intent.items()}
        },
        'user_demographics': {
            'regions': region_counts,
            'roles': role_counts
        },
        'recent_feedback': recent_feedback,
        'improvement_areas': {
            'negative_feedback_count': len(negative_feedback),
            'common_issues': [f['comment'] for f in negative_feedback[-5:] if f.get('comment')]
        }
    }
    
    return jsonify(analytics)

@app.route('/api/export-data')
def export_data():
    """Export all data for analysis"""
    export_data = {
        'conversations': conversations,
        'feedback': feedback_data,
        'export_timestamp': datetime.now().isoformat(),
        'summary': {
            'total_conversations': len(conversations),
            'total_feedback': len(feedback_data),
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    return jsonify(export_data)

@app.route('/analytics')
def analytics_dashboard():
    """Analytics dashboard page"""
    return render_template('analytics.html')

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("Starting AgriBot Testing Platform with Feedback System...")
    print("Visit: http://localhost:5000")
    print("Analytics: http://localhost:5000/analytics")
    app.run(debug=True, port=5000)