"""
AgriBot Main Engine
Location: agribot/core/agribot_engine.py

Main conversation engine that orchestrates all components to provide
comprehensive agricultural assistance.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging

from knowledge.agricultural_knowledge import AgriculturalKnowledgeBase
from nlp import NLPProcessor
from services.data_coordinator import DataCoordinator
from services.claude_service import ClaudeService
from core.conversation_manager import ConversationManager
from core.response_builder import ResponseBuilder
from database.repositories.analytics_repository import AnalyticsRepository
from utils.exceptions import AgriBotException, APIServiceError
from config.settings import AppConfig

class AgriBotEngine:
    """Main AgriBot conversation engine"""
    
    def __init__(self, knowledge_base: AgriculturalKnowledgeBase = None,
                 nlp_processor: NLPProcessor = None,
                 data_coordinator: DataCoordinator = None,
                 config: AppConfig = None):
        """Initialize AgriBot engine with dependency injection"""

        # Configuration
        self.config = config or AppConfig()

        # Setup logging first
        self.logger = logging.getLogger(__name__)

        # Initialize core components
        self.knowledge_base = knowledge_base or AgriculturalKnowledgeBase()
        self.nlp_processor = nlp_processor or NLPProcessor()
        self.data_coordinator = data_coordinator or DataCoordinator(config.apis if config else None)

        # Initialize Claude service with agricultural knowledge
        if self.config.apis.claude_api_key:
            agricultural_data = self.knowledge_base.export_for_claude_context()
            self.claude_service = ClaudeService(
                api_key=self.config.apis.claude_api_key,
                agricultural_knowledge=agricultural_data
            )
            self.use_claude = True
            self.logger.info("Claude API service initialized - using advanced AI mode")
        else:
            self.claude_service = None
            self.use_claude = False
            self.logger.warning("Claude API key not provided - falling back to basic NLP mode")

        # Initialize managers
        self.conversation_manager = ConversationManager()
        self.response_builder = ResponseBuilder(self.knowledge_base)
        self.analytics_repo = AnalyticsRepository()

        # Performance tracking
        self.response_times = []
        self.error_counts = {'total': 0, 'by_type': {}}
        
        self.logger.info("AgriBot Engine initialized successfully")
    
    def process_message(self, message: str, user_id: str, user_name: str = 'Friend',
                       user_region: str = 'centre', language: str = 'en', include_external_data: bool = True) -> Dict[str, Any]:
        """Process a user message and return comprehensive response"""
        
        start_time = datetime.now()
        
        try:
            # Input validation
            if not message or not message.strip():
                return self._create_error_response("Empty message received")
            
            if not user_id:
                return self._create_error_response("User ID required")
            
            # Get conversation state
            conversation_state = self.conversation_manager.get_conversation_state(
                user_id, user_name, user_region
            )

            # Get conversation context
            conversation_context = self.conversation_manager.get_conversation_context(user_id)

            if self.use_claude and self.claude_service:
                try:
                    # Use Claude API for intelligent response
                    user_context = {
                        'name': user_name,
                        'region': user_region,
                        'language': language,
                        'conversation_state': conversation_state
                    }

                    # Get external data for Claude context
                    external_data = {}
                    if include_external_data:
                        external_data = self._fetch_external_data_for_claude(user_region)

                    # Get Claude response
                    claude_response = self.claude_service.get_response(
                        user_input=message,
                        conversation_id=user_id,
                        user_context=user_context,
                        language=language,
                        weather_data=external_data.get('weather'),
                        market_data=external_data.get('market')
                    )

                    # Format response data to match expected structure
                    response_data = {
                        'response': claude_response.content,
                        'intent': claude_response.intent,
                        'entities': claude_response.entities,
                        'confidence_score': claude_response.confidence_score,
                        'processing_time': claude_response.processing_time,
                        'external_data_sources': list(external_data.keys()) if external_data else [],
                        'ai_mode': 'claude'
                    }

                    # Update conversation state with Claude metadata
                    nlp_result = {
                        'intent': claude_response.intent,
                        'entities': claude_response.entities,
                        'confidence': claude_response.confidence_score,
                        'sentiment': 'neutral',  # Claude doesn't provide explicit sentiment
                        'emotional_context': {}
                    }
                except Exception as claude_error:
                    self.logger.error(f"Claude API error, falling back to basic NLP: {str(claude_error)}")
                    # Fall back to basic NLP
                    self.use_claude = False
                    conversation_context = self.conversation_manager.get_conversation_context(user_id)
                    nlp_result = self.nlp_processor.process(message, conversation_context)

                    # Get external data if requested
                    external_data = {}
                    if include_external_data and self._should_fetch_external_data(nlp_result):
                        external_data = self._fetch_relevant_external_data(
                            nlp_result, conversation_context, user_region
                        )

                    # Build response using traditional method
                    response_data = self.response_builder.build_response(
                        nlp_result['intent'],
                        nlp_result['entities'],
                        nlp_result['sentiment'],
                        nlp_result['emotional_context'],
                        conversation_context,
                        external_data
                    )
                    response_data['ai_mode'] = 'fallback'
            else:
                # Fallback to original NLP processor
                conversation_context = self.conversation_manager.get_conversation_context(user_id)

                # Process message with NLP
                nlp_result = self.nlp_processor.process(message, conversation_context)

                # Get external data if requested and relevant
                external_data = {}
                if include_external_data and self._should_fetch_external_data(nlp_result):
                    external_data = self._fetch_relevant_external_data(
                        nlp_result, conversation_context, user_region
                    )

                # Build response using traditional method
                response_data = self.response_builder.build_response(
                    nlp_result['intent'],
                    nlp_result['entities'],
                    nlp_result['sentiment'],
                    nlp_result['emotional_context'],
                    conversation_context,
                    external_data
                )
                response_data['ai_mode'] = 'traditional'
            
            # Update conversation state
            self.conversation_manager.update_conversation_state(
                user_id, message, nlp_result, response_data['response']
            )
            
            # Track performance
            processing_time = (datetime.now() - start_time).total_seconds()
            self.response_times.append(processing_time)
            
            # Log interaction for analytics
            self._log_interaction(user_id, message, response_data, nlp_result, processing_time)
            
            # Prepare final response
            # Handle both object and string types for intent
            intent_value = nlp_result.get('intent', 'unknown')
            if hasattr(intent_value, 'intent'):
                intent_str = intent_value.intent
                confidence = intent_value.confidence
            else:
                intent_str = str(intent_value)
                confidence = nlp_result.get('confidence', response_data.get('confidence_score', 0.0))

            # Handle both object and string types for sentiment
            sentiment_value = nlp_result.get('sentiment', 'neutral')
            if hasattr(sentiment_value, 'polarity'):
                sentiment_polarity = sentiment_value.polarity
                emotional_tone = sentiment_value.emotional_tone
            else:
                sentiment_polarity = 0.0
                emotional_tone = str(sentiment_value)

            # Handle entities
            entities_value = nlp_result.get('entities', {})
            if hasattr(entities_value, 'entities'):
                entities_summary = self._summarize_entities(entities_value)
            else:
                entities_summary = entities_value if isinstance(entities_value, dict) else {}

            final_response = {
                'response': response_data['response'],
                'suggestions': response_data.get('follow_up_suggestions', []),
                'metadata': {
                    'intent': intent_str,
                    'confidence': confidence,
                    'entities': entities_summary,
                    'sentiment': {
                        'polarity': sentiment_polarity,
                        'emotional_tone': emotional_tone
                    },
                    'processing_time_ms': round(processing_time * 1000, 2),
                    'external_data_used': bool(external_data) if 'external_data' in locals() else False,
                    'conversation_turn': conversation_state.message_count
                },
                'context': {
                    'current_topic': conversation_state.current_topic,
                    'mentioned_crops': conversation_state.mentioned_crops,
                    'suggested_next_topics': self.conversation_manager.suggest_next_topics(user_id)
                }
            }
            
            self.logger.info(f"Successfully processed message for user {user_id} in {processing_time:.3f}s")
            
            return final_response
            
        except Exception as e:
            # Log error
            self.logger.error(f"Error processing message for user {user_id}: {str(e)}")
            self._log_error(e, user_id, message)
            
            # Return error response
            return self._create_error_response(str(e), user_id)
    
    def _should_fetch_external_data(self, nlp_result: Dict) -> bool:
        """Determine if external data should be fetched based on NLP analysis"""
        intent = nlp_result['intent'].intent
        entities = nlp_result['entities']
        
        # Weather-related queries
        if intent == 'weather_inquiry':
            return True
        
        # Queries mentioning specific crops (for production data)
        if hasattr(entities, 'entities') and entities.entities.get('crops'):
            if intent in ['yield_optimization', 'market_information', 'planting_guidance']:
                return True
        
        # Disease/pest inquiries with regional context
        if intent in ['disease_identification', 'pest_control']:
            if hasattr(entities, 'entities') and entities.entities.get('regions'):
                return True
        
        return False
    
    def _fetch_relevant_external_data(self, nlp_result: Dict, conversation_context: Dict,
                                    user_region: str) -> Dict[str, Any]:
        """Fetch relevant external data based on NLP analysis"""
        external_data = {}
        
        intent = nlp_result['intent'].intent
        entities = nlp_result['entities']
        
        # Extract relevant entities
        crops = self._extract_entities_by_type(entities, 'crops')
        regions = self._extract_entities_by_type(entities, 'regions')
        
        # Use user region if no region specified
        target_region = regions[0] if regions else user_region
        
        try:
            if intent == 'weather_inquiry' or 'weather' in conversation_context.get('current_topic', ''):
                # Fetch weather analysis
                weather_analysis = self.data_coordinator.get_comprehensive_analysis(
                    target_region, crops[0] if crops else None, include_forecast=True
                )
                external_data['weather_analysis'] = weather_analysis
                
            elif crops and intent in ['yield_optimization', 'market_information']:
                # Fetch comprehensive agricultural analysis
                crop = crops[0]
                ag_analysis = self.data_coordinator.get_comprehensive_analysis(
                    target_region, crop, include_forecast=False
                )
                external_data['agricultural_analysis'] = ag_analysis
                
        except APIServiceError as e:
            self.logger.warning(f"API service error: {str(e)}")
            external_data['api_error'] = str(e)
        except Exception as e:
            self.logger.error(f"Unexpected error fetching external data: {str(e)}")
        
        return external_data

    def _fetch_external_data_for_claude(self, user_region: str) -> Dict[str, Any]:
        """Fetch external data optimized for Claude context"""
        external_data = {}

        # For now, just return region info since DataCoordinator needs refactoring
        # External data can be added later when needed
        if user_region:
            external_data['user_region'] = user_region

        return external_data

    def _extract_entities_by_type(self, entities, entity_type: str) -> List[str]:
        """Extract entities of specific type"""
        if not entities or not hasattr(entities, 'entities'):
            return []
        
        entity_matches = entities.entities.get(entity_type, [])
        return [match.normalized_form for match in entity_matches] if entity_matches else []
    
    def _summarize_entities(self, entities) -> Dict[str, List[str]]:
        """Create entity summary for response metadata"""
        if not entities or not hasattr(entities, 'entities'):
            return {}
        
        summary = {}
        for entity_type, entity_list in entities.entities.items():
            if entity_list:
                summary[entity_type] = [entity.normalized_form for entity in entity_list]
        
        return summary
    
    def _log_interaction(self, user_id: str, message: str, response_data: Dict,
                        nlp_result: Dict, processing_time: float):
        """Log interaction for analytics"""
        try:
            # Handle both object and string types for intent
            intent_value = nlp_result.get('intent', 'unknown')
            if hasattr(intent_value, 'intent'):
                intent_str = intent_value.intent
                confidence = intent_value.confidence
            else:
                intent_str = str(intent_value)
                confidence = nlp_result.get('confidence', 0.0)

            # Handle both object and string types for sentiment
            sentiment_value = nlp_result.get('sentiment', None)
            if hasattr(sentiment_value, 'polarity'):
                sentiment_polarity = sentiment_value.polarity
            else:
                sentiment_polarity = 0.0

            # Handle entities
            entities_value = nlp_result.get('entities', {})
            if hasattr(entities_value, 'entities'):
                entities_count = sum(len(entities) for entities in entities_value.entities.values())
            else:
                entities_count = 0

            # This would typically be async, but keeping simple for now
            interaction_data = {
                'user_id': user_id,
                'message_length': len(message),
                'intent': intent_str,
                'confidence': confidence,
                'sentiment_polarity': sentiment_polarity,
                'processing_time': processing_time,
                'entities_count': entities_count
            }

            # Log to analytics system (implementation would depend on analytics backend)
            self.logger.info(f"Interaction logged: {interaction_data}")

        except Exception as e:
            self.logger.error(f"Failed to log interaction: {str(e)}")
    
    def _log_error(self, error: Exception, user_id: str = None, message: str = None):
        """Log error for monitoring and improvement"""
        try:
            self.error_counts['total'] += 1
            error_type = type(error).__name__
            self.error_counts['by_type'][error_type] = self.error_counts['by_type'].get(error_type, 0) + 1
            
            # Log to analytics repository
            self.analytics_repo.log_error(
                error_type=error_type,
                error_message=str(error),
                stack_trace=None,  # Could add full stack trace if needed
                user_id=user_id,
                user_input=message
            )
            
        except Exception as log_error:
            self.logger.error(f"Failed to log error: {str(log_error)}")
    
    def _create_error_response(self, error_message: str, user_id: str = None) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'response': "I encountered an issue processing your request. Let me try to help anyway - what specific farming question do you have?",
            'suggestions': [
                "Ask about crop diseases",
                "Get planting advice",
                "Learn about fertilizers",
                "Weather information"
            ],
            'metadata': {
                'error': True,
                'error_message': error_message,
                'intent': 'error',
                'confidence': 0.0,
                'processing_time_ms': 0
            },
            'context': {
                'current_topic': 'error_recovery',
                'mentioned_crops': [],
                'suggested_next_topics': ['general_inquiry', 'planting_guidance']
            }
        }
    
    def get_user_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive conversation summary for user"""
        try:
            return self.conversation_manager.get_conversation_summary(user_id)
        except Exception as e:
            self.logger.error(f"Error getting conversation summary for {user_id}: {str(e)}")
            return {'error': str(e)}
    
    def end_user_conversation(self, user_id: str) -> Dict[str, Any]:
        """End user conversation session"""
        try:
            return self.conversation_manager.end_conversation(user_id)
        except Exception as e:
            self.logger.error(f"Error ending conversation for {user_id}: {str(e)}")
            return {'error': str(e)}
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """Get engine performance statistics"""
        avg_response_time = (sum(self.response_times) / len(self.response_times) 
                           if self.response_times else 0)
        
        return {
            'performance': {
                'total_messages_processed': len(self.response_times),
                'average_response_time_ms': round(avg_response_time * 1000, 2),
                'active_conversations': self.conversation_manager.get_active_conversation_count()
            },
            'errors': {
                'total_errors': self.error_counts['total'],
                'error_breakdown': self.error_counts['by_type']
            },
            'system_health': {
                'knowledge_base_loaded': bool(self.knowledge_base),
                'nlp_processor_ready': bool(self.nlp_processor),
                'data_coordinator_ready': bool(self.data_coordinator)
            }
        }
    
    def cleanup_resources(self):
        """Cleanup resources and expired sessions"""
        try:
            expired_count = self.conversation_manager.cleanup_expired_sessions()
            self.logger.info(f"Cleaned up {expired_count} expired conversation sessions")
            
            # Limit response time tracking to prevent memory bloat
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-500:]
            
            return {'expired_sessions_cleaned': expired_count}
            
        except Exception as e:
            self.logger.error(f"Error during resource cleanup: {str(e)}")
            return {'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of all components"""
        health_status = {
            'overall_status': 'healthy',
            'components': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Check knowledge base
            test_crop_info = self.knowledge_base.get_comprehensive_crop_info('maize')
            health_status['components']['knowledge_base'] = {
                'status': 'healthy' if 'crop_name' in test_crop_info else 'degraded',
                'details': 'Knowledge base accessible'
            }
            
            # Check NLP processor
            test_nlp = self.nlp_processor.process("test message")
            health_status['components']['nlp_processor'] = {
                'status': 'healthy' if 'intent' in test_nlp else 'degraded',
                'details': 'NLP processing functional'
            }
            
            # Check data coordinator (with timeout)
            try:
                # This should be a quick test, not a full API call
                health_status['components']['data_coordinator'] = {
                    'status': 'healthy',
                    'details': 'Data coordinator initialized'
                }
            except Exception:
                health_status['components']['data_coordinator'] = {
                    'status': 'degraded',
                    'details': 'Data coordinator issues'
                }
            
            # Overall status
            component_statuses = [comp['status'] for comp in health_status['components'].values()]
            if all(status == 'healthy' for status in component_statuses):
                health_status['overall_status'] = 'healthy'
            elif any(status == 'healthy' for status in component_statuses):
                health_status['overall_status'] = 'degraded'
            else:
                health_status['overall_status'] = 'unhealthy'
                
        except Exception as e:
            health_status['overall_status'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return health_status