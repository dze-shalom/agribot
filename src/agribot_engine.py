from data_coordinator import DataCoordinator
from agricultural_knowledge import AgriculturalKnowledgeBase
from nlp_models import EnhancedIntentClassifier, EnhancedEntityExtractor, ConversationalResponseGenerator
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import re
import random

# Rest of your code remains the same...

@dataclass
class ConversationContext:
    user_id: str
    user_name: str = "Friend"
    user_region: str = "centre"
    current_topic: str = ""
    mentioned_crops: List[str] = None
    conversation_history: List[Dict] = None
    session_start: datetime = None
    
    def __post_init__(self):
        if self.mentioned_crops is None:
            self.mentioned_crops = []
        if self.conversation_history is None:
            self.conversation_history = []
        if self.session_start is None:
            self.session_start = datetime.now()

class EnhancedAgriBotEngine:
    def __init__(self):
        self.data_coordinator = DataCoordinator()
        self.knowledge_base = AgriculturalKnowledgeBase()
        
        # Enhanced NLP components
        self.intent_classifier = EnhancedIntentClassifier()
        self.entity_extractor = EnhancedEntityExtractor()
        self.response_generator = ConversationalResponseGenerator(self.knowledge_base)
        
        # Supported regions and crops from data coordinator
        self.supported_regions = list(self.data_coordinator.nasa_service.regions.keys())
        self.supported_crops = self.data_coordinator.nasa_service.get_all_crops_list()
        
        # Conversation management
        self.contexts = {}  # Store conversation contexts by user_id
    
    def get_or_create_context(self, user_id: str, **kwargs) -> ConversationContext:
        """Get existing context or create new one"""
        if user_id not in self.contexts:
            self.contexts[user_id] = ConversationContext(user_id=user_id, **kwargs)
        return self.contexts[user_id]
    
    def process_conversational_question(self, question: str, user_id: str, user_name: str = "", user_region: str = "centre"):
        """Enhanced conversational processing with advanced NLP"""
        
        # Get or create conversation context
        context = self.get_or_create_context(user_id, user_name=user_name, user_region=user_region)
        
        # Add message to conversation history
        context.conversation_history.append({
            "timestamp": datetime.now(),
            "user_message": question,
            "message_type": "user"
        })
        
        # Generate response using enhanced NLP
        response_data = self.response_generator.generate_response(question, context)
        
        # Update context based on response
        self._update_context_from_response(context, response_data)
        
        # Add bot response to history
        context.conversation_history.append({
            "timestamp": datetime.now(),
            "bot_response": response_data['response'],
            "intent": response_data['intent'],
            "confidence": response_data['confidence'],
            "entities": response_data['entities'],
            "message_type": "bot"
        })
        
        return {
            'response': response_data['response'],
            'current_topic': context.current_topic,
            'mentioned_crops': context.mentioned_crops,
            'context': context,
            'intent': response_data['intent'],
            'confidence': response_data['confidence'],
            'sentiment': response_data['sentiment'],
            'entities': response_data['entities'],
            'follow_up_suggestions': response_data.get('follow_up_suggestions', [])
        }
    
    def _update_context_from_response(self, context: ConversationContext, response_data: Dict[str, Any]):
        """Update conversation context based on response data"""
        
        # Update current topic
        if response_data.get('intent') and response_data['intent'] != 'general':
            context.current_topic = response_data['intent']
        
        # Update mentioned crops
        entities = response_data.get('entities', {})
        if entities.get('crops'):
            for crop in entities['crops']:
                if crop not in context.mentioned_crops:
                    context.mentioned_crops.append(crop)
                    
        # Keep only last 5 crops to avoid memory bloat
        if len(context.mentioned_crops) > 5:
            context.mentioned_crops = context.mentioned_crops[-5:]
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive conversation summary"""
        if user_id not in self.contexts:
            return {'error': 'No conversation found'}
        
        context = self.contexts[user_id]
        
        # Analyze conversation patterns
        topics_discussed = {}
        total_messages = len([msg for msg in context.conversation_history if msg['message_type'] == 'user'])
        
        for msg in context.conversation_history:
            if msg['message_type'] == 'bot' and 'intent' in msg:
                intent = msg['intent']
                topics_discussed[intent] = topics_discussed.get(intent, 0) + 1
        
        return {
            'user_info': {
                'name': context.user_name,
                'region': context.user_region,
                'session_duration': str(datetime.now() - context.session_start)
            },
            'conversation_stats': {
                'total_messages': total_messages,
                'topics_discussed': topics_discussed,
                'current_topic': context.current_topic,
                'mentioned_crops': context.mentioned_crops
            },
            'engagement_metrics': {
                'avg_response_length': self._calculate_avg_response_length(context),
                'topic_diversity': len(topics_discussed),
                'crop_diversity': len(set(context.mentioned_crops))
            }
        }
    
    def _calculate_avg_response_length(self, context: ConversationContext) -> float:
        """Calculate average response length"""
        bot_responses = [msg for msg in context.conversation_history if msg['message_type'] == 'bot']
        if not bot_responses:
            return 0.0
        
        total_length = sum(len(msg['bot_response']) for msg in bot_responses)
        return total_length / len(bot_responses)
    
    def get_learning_insights(self, user_id: str) -> Dict[str, Any]:
        """Generate insights for improving responses"""
        if user_id not in self.contexts:
            return {'error': 'No conversation data'}
        
        context = self.contexts[user_id]
        insights = {
            'user_preferences': self._analyze_user_preferences(context),
            'knowledge_gaps': self._identify_knowledge_gaps(context),
            'response_patterns': self._analyze_response_patterns(context)
        }
        
        return insights
    
    def _analyze_user_preferences(self, context: ConversationContext) -> Dict[str, Any]:
        """Analyze user interaction preferences"""
        preferences = {
            'preferred_crops': {},
            'common_topics': {},
            'interaction_style': 'detailed'  # vs 'brief'
        }
        
        # Count crop mentions
        for crop in context.mentioned_crops:
            preferences['preferred_crops'][crop] = preferences['preferred_crops'].get(crop, 0) + 1
        
        # Count topics
        for msg in context.conversation_history:
            if msg.get('intent'):
                intent = msg['intent']
                preferences['common_topics'][intent] = preferences['common_topics'].get(intent, 0) + 1
        
        return preferences
    
    def _identify_knowledge_gaps(self, context: ConversationContext) -> List[str]:
        """Identify areas where knowledge base might be lacking"""
        gaps = []
        
        # Look for questions that got low confidence responses
        for msg in context.conversation_history:
            if msg.get('confidence', 1.0) < 0.5:
                gaps.append(f"Low confidence in handling: {msg.get('user_message', 'unknown')}")
        
        return gaps
    
    def _analyze_response_patterns(self, context: ConversationContext) -> Dict[str, Any]:
        """Analyze response effectiveness patterns"""
        patterns = {
            'avg_confidence': 0.0,
            'topic_transitions': [],
            'response_variety': 0.0
        }
        
        confidences = []
        topics = []
        
        for msg in context.conversation_history:
            if msg.get('confidence'):
                confidences.append(msg['confidence'])
            if msg.get('intent'):
                topics.append(msg['intent'])
        
        if confidences:
            patterns['avg_confidence'] = sum(confidences) / len(confidences)
        
        # Track topic transitions
        for i in range(1, len(topics)):
            if topics[i] != topics[i-1]:
                patterns['topic_transitions'].append(f"{topics[i-1]} -> {topics[i]}")
        
        return patterns

    # Keep backward compatibility methods
    def process_question(self, question, user_region='centre'):
        """Legacy method for backward compatibility"""
        temp_user_id = "legacy_user"
        result = self.process_conversational_question(question, temp_user_id, "User", user_region)
        return result['response']
    
    def classify_question(self, question):
        """Legacy method - now uses enhanced NLP"""
        intent_result = self.intent_classifier.classify_intent(question)
        return intent_result['intent']
    
    def extract_entities(self, question):
        """Legacy method - now uses enhanced NLP"""
        entities = self.entity_extractor.extract_all_entities(question)
        return {
            'crops': entities.get('crops', []),
            'regions': entities.get('regions', []),
            'diseases': entities.get('diseases', []),
            'pests': entities.get('pests', [])
        }

# Global instance for backward compatibility
AgriBotEngine = EnhancedAgriBotEngine