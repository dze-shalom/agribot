"""
Conversation Manager
Location: agribot/core/conversation_manager.py

Manages conversation context, state, and flow for agricultural discussions.
Maintains user context across multiple interactions.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from database.repositories.conversation_repository import ConversationRepository
from database.repositories.user_repository import UserRepository
from nlp import NLPProcessor
from utils.exceptions import AgriBotException

@dataclass
class ConversationState:
    """Current state of conversation"""
    user_id: str
    conversation_id: Optional[int] = None
    current_topic: str = 'general'
    mentioned_crops: List[str] = field(default_factory=list)
    mentioned_regions: List[str] = field(default_factory=list)
    mentioned_diseases: List[str] = field(default_factory=list)
    mentioned_pests: List[str] = field(default_factory=list)
    session_start: datetime = field(default_factory=datetime.now)
    last_intent: Optional[str] = None
    last_confidence: float = 0.0
    message_count: int = 0
    context_history: List[Dict] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)

class ConversationManager:
    """Manages conversation context and state"""
    
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.conversation_repo = ConversationRepository()
        self.user_repo = UserRepository()
        
        # Active conversation states (in-memory cache)
        self.active_conversations: Dict[str, ConversationState] = {}
        
        # Conversation flow patterns
        self.topic_transitions = {
            'greeting': ['planting_guidance', 'general_inquiry', 'disease_identification'],
            'disease_identification': ['pest_control', 'fertilizer_advice', 'harvest_timing'],
            'pest_control': ['disease_identification', 'yield_optimization'],
            'planting_guidance': ['fertilizer_advice', 'harvest_timing', 'yield_optimization'],
            'fertilizer_advice': ['yield_optimization', 'planting_guidance'],
            'harvest_timing': ['market_information', 'yield_optimization'],
            'weather_inquiry': ['planting_guidance', 'disease_identification', 'harvest_timing']
        }
        
        # Context retention settings
        self.max_context_history = 10
        self.session_timeout_minutes = 120
    
    def get_conversation_state(self, user_id: str, user_name: str = 'Friend',
                              user_region: str = 'centre') -> ConversationState:
        """Get or create conversation state for user - one conversation per session"""
        # Check if user has active conversation
        if user_id in self.active_conversations:
            state = self.active_conversations[user_id]

            # Check if session has timed out
            if self._is_session_expired(state):
                self._end_conversation_session(user_id)
                return self._create_new_conversation_state(user_id, user_name, user_region)

            return state
        else:
            return self._create_new_conversation_state(user_id, user_name, user_region)
    
    def update_conversation_state(self, user_id: str, user_message: str, 
                                nlp_result: Dict, bot_response: str) -> ConversationState:
        """Update conversation state after processing message"""
        state = self.active_conversations.get(user_id)
        if not state:
            raise AgriBotException(f"No active conversation found for user {user_id}")
        
        # Update message count
        state.message_count += 1
        
        # Update current topic based on intent
        intent = nlp_result.get('intent', {})
        if hasattr(intent, 'intent'):
            new_topic = intent.intent
            if new_topic != 'unknown':
                state.current_topic = new_topic
                state.last_intent = new_topic
                state.last_confidence = intent.confidence
        
        # Update mentioned entities
        entities = nlp_result.get('entities', {})
        if hasattr(entities, 'entities'):
            # Traditional NLP mode: entities is an object
            self._update_mentioned_entities(state, entities.entities)
        elif isinstance(entities, dict) and 'crops' in entities:
            # Claude mode: entities is a dict with crops array
            self._update_mentioned_entities_from_dict(state, entities)
        
        # Add to context history
        context_entry = {
            'timestamp': datetime.now(),
            'user_message': user_message,
            'bot_response': bot_response,
            'intent': state.last_intent,
            'confidence': state.last_confidence,
            'entities': self._extract_entity_summary(entities.entities) if hasattr(entities, 'entities') else {}
        }
        
        state.context_history.append(context_entry)
        
        # Limit context history size
        if len(state.context_history) > self.max_context_history:
            state.context_history = state.context_history[-self.max_context_history:]
        
        # Persist to database if conversation exists
        if state.conversation_id:
            self._persist_conversation_update(state, user_message, bot_response, nlp_result)
        
        return state
    
    def _create_new_conversation_state(self, user_id: str, user_name: str, 
                                     user_region: str) -> ConversationState:
        """Create new conversation state"""
        # Ensure user exists in database
        user = self.user_repo.get_or_create_user(user_id, user_name, user_region)
        
        # Create new conversation in database
        conversation = self.conversation_repo.create_conversation(user_id, user_region)
        
        # Create in-memory state
        state = ConversationState(
            user_id=user_id,
            conversation_id=conversation.id,
            current_topic='greeting'
        )
        
        # Load user preferences
        state.user_preferences = self._load_user_preferences(user)
        
        # Store in active conversations
        self.active_conversations[user_id] = state
        
        return state
    
    def _update_mentioned_entities(self, state: ConversationState, entities: Dict):
        """Update mentioned entities in conversation state"""
        # Update crops
        if 'crops' in entities:
            for crop_entity in entities['crops']:
                crop = crop_entity.normalized_form
                if crop not in state.mentioned_crops:
                    state.mentioned_crops.append(crop)
        
        # Update regions
        if 'regions' in entities:
            for region_entity in entities['regions']:
                region = region_entity.normalized_form
                if region not in state.mentioned_regions:
                    state.mentioned_regions.append(region)
        
        # Update diseases
        if 'diseases' in entities:
            for disease_entity in entities['diseases']:
                disease = disease_entity.normalized_form
                if disease not in state.mentioned_diseases:
                    state.mentioned_diseases.append(disease)
        
        # Update pests
        if 'pests' in entities:
            for pest_entity in entities['pests']:
                pest = pest_entity.normalized_form
                if pest not in state.mentioned_pests:
                    state.mentioned_pests.append(pest)
        
        # Limit entity lists to prevent memory bloat
        state.mentioned_crops = state.mentioned_crops[-5:]
        state.mentioned_regions = state.mentioned_regions[-3:]
        state.mentioned_diseases = state.mentioned_diseases[-5:]
        state.mentioned_pests = state.mentioned_pests[-5:]

    def _update_mentioned_entities_from_dict(self, state: ConversationState, entities: Dict):
        """Update mentioned entities from Claude mode dict format"""
        # Claude returns entities as: {'crops': ['maize', 'tomato'], ...}
        # Just strings, not objects with normalized_form

        # Update crops
        if 'crops' in entities and isinstance(entities['crops'], list):
            for crop in entities['crops']:
                crop_str = crop.lower() if isinstance(crop, str) else str(crop)
                if crop_str and crop_str not in state.mentioned_crops:
                    state.mentioned_crops.append(crop_str)

        # Limit entity lists to prevent memory bloat
        state.mentioned_crops = state.mentioned_crops[-5:]

    def _extract_entity_summary(self, entities: Dict) -> Dict[str, List[str]]:
        """Extract summary of entities for context storage"""
        summary = {}

        if hasattr(entities, 'items'):
            # If entities is a dictionary
            for entity_type, entity_list in entities.items():
                summary[entity_type] = [entity.normalized_form for entity in entity_list]
        else:
            # If entities is already processed or empty
            return {}

        return summary
    
    def _persist_conversation_update(self, state: ConversationState, user_message: str,
                                   bot_response: str, nlp_result: Dict):
        """Persist conversation update to database"""
        if not state.conversation_id:
            return

        # Extract data from nlp_result
        intent_data = nlp_result.get('intent', {})
        entities_data = nlp_result.get('entities', {})
        sentiment_data = nlp_result.get('sentiment', {})

        # Handle different confidence formats (object vs direct value)
        confidence_score = None
        if hasattr(intent_data, 'confidence'):
            # Traditional NLP mode: intent is an object with confidence
            confidence_score = intent_data.confidence
        elif 'confidence' in nlp_result:
            # Claude mode: confidence is a separate field in nlp_result
            confidence_score = nlp_result.get('confidence')

        # Handle intent (can be string or object)
        intent_str = None
        if hasattr(intent_data, 'intent'):
            intent_str = intent_data.intent
        elif isinstance(intent_data, str):
            intent_str = intent_data

        # Add user message
        user_msg = self.conversation_repo.add_message(
            state.conversation_id,
            user_message,
            'user',
            intent=intent_str,
            confidence=confidence_score,
            entities=getattr(entities_data, 'entities', {}) if hasattr(entities_data, 'entities') else {},
            sentiment=getattr(sentiment_data, 'polarity', None) if hasattr(sentiment_data, 'polarity') else None
        )

        # Add bot response with same confidence score
        bot_msg = self.conversation_repo.add_message(
            state.conversation_id,
            bot_response,
            'bot',
            intent=intent_str,
            confidence=confidence_score
        )
        
        # Update conversation context
        self.conversation_repo.update_conversation_context(
            state.conversation_id,
            state.current_topic,
            state.mentioned_crops
        )
    
    def _load_user_preferences(self, user) -> Dict[str, Any]:
        """Load user preferences from database"""
        return {
            'name': user.name,
            'region': user.region,
            'role': user.role,
            'total_conversations': user.total_conversations
        }
    
    def get_conversation_context(self, user_id: str) -> Dict[str, Any]:
        """Get conversation context for NLP processing"""
        state = self.active_conversations.get(user_id)
        if not state:
            return {}
        
        return {
            'current_topic': state.current_topic,
            'mentioned_crops': state.mentioned_crops,
            'mentioned_regions': state.mentioned_regions,
            'mentioned_diseases': state.mentioned_diseases,
            'mentioned_pests': state.mentioned_pests,
            'previous_intent': state.last_intent,
            'message_count': state.message_count,
            'session_duration': (datetime.now() - state.session_start).total_seconds(),
            'user_preferences': state.user_preferences
        }
    
    def suggest_next_topics(self, user_id: str) -> List[str]:
        """Suggest relevant next topics based on current conversation"""
        state = self.active_conversations.get(user_id)
        if not state:
            return ['planting_guidance', 'disease_identification', 'fertilizer_advice']
        
        current_topic = state.current_topic
        suggested_topics = self.topic_transitions.get(current_topic, [])
        
        # Filter based on mentioned entities
        if state.mentioned_crops:
            # If crops mentioned, prioritize crop-specific topics
            crop_relevant_topics = ['disease_identification', 'pest_control', 
                                  'fertilizer_advice', 'harvest_timing', 'yield_optimization']
            suggested_topics.extend([t for t in crop_relevant_topics if t not in suggested_topics])
        
        return suggested_topics[:3]  # Return top 3 suggestions
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive conversation summary"""
        state = self.active_conversations.get(user_id)
        if not state:
            return {'error': 'No active conversation found'}
        
        # Calculate conversation metrics
        duration = datetime.now() - state.session_start
        avg_confidence = (sum(entry.get('confidence', 0) for entry in state.context_history) / 
                         len(state.context_history)) if state.context_history else 0
        
        return {
            'user_id': user_id,
            'conversation_id': state.conversation_id,
            'session_info': {
                'duration_minutes': round(duration.total_seconds() / 60, 1),
                'message_count': state.message_count,
                'start_time': state.session_start.isoformat()
            },
            'topics_discussed': {
                'current_topic': state.current_topic,
                'topic_history': [entry.get('intent') for entry in state.context_history if entry.get('intent')]
            },
            'entities_mentioned': {
                'crops': state.mentioned_crops,
                'regions': state.mentioned_regions,
                'diseases': state.mentioned_diseases,
                'pests': state.mentioned_pests
            },
            'interaction_quality': {
                'average_confidence': round(avg_confidence, 2),
                'last_confidence': state.last_confidence
            },
            'suggested_next_topics': self.suggest_next_topics(user_id)
        }
    
    def end_conversation(self, user_id: str) -> Dict[str, Any]:
        """End conversation session"""
        state = self.active_conversations.get(user_id)
        if not state:
            return {'error': 'No active conversation found'}
        
        # Get final summary
        summary = self.get_conversation_summary(user_id)
        
        # End conversation in database
        if state.conversation_id:
            self.conversation_repo.end_conversation(state.conversation_id)
        
        # Update user conversation count
        self.user_repo.increment_user_conversations(user_id)
        
        # Remove from active conversations
        del self.active_conversations[user_id]
        
        return {
            'status': 'conversation_ended',
            'summary': summary
        }
    
    def _end_conversation_session(self, user_id: str):
        """Internal method to end expired session"""
        if user_id in self.active_conversations:
            state = self.active_conversations[user_id]
            if state.conversation_id:
                self.conversation_repo.end_conversation(state.conversation_id)
            del self.active_conversations[user_id]
    
    def _is_session_expired(self, state: ConversationState) -> bool:
        """Check if conversation session has expired"""
        time_elapsed = datetime.now() - state.session_start
        return time_elapsed.total_seconds() > (self.session_timeout_minutes * 60)
    
    def cleanup_expired_sessions(self):
        """Clean up expired conversation sessions"""
        expired_users = []
        
        for user_id, state in self.active_conversations.items():
            if self._is_session_expired(state):
                expired_users.append(user_id)
        
        for user_id in expired_users:
            self._end_conversation_session(user_id)
        
        return len(expired_users)
    
    def get_active_conversation_count(self) -> int:
        """Get count of active conversations"""
        return len(self.active_conversations)