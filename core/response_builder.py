"""
Response Builder
Location: agribot/core/response_builder.py

Builds contextual, natural responses for agricultural queries using
knowledge base, NLP analysis, and conversation context.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from knowledge.agricultural_knowledge import AgriculturalKnowledgeBase
from nlp.sentiment_analyzer import SentimentScore, EmotionalContext
from utils.exceptions import AgriBotException

class ResponseBuilder:
    """Builds natural, contextual responses for agricultural queries"""
    
    def __init__(self, knowledge_base: AgriculturalKnowledgeBase):
        self.knowledge_base = knowledge_base
        
        # Response templates organized by intent and context
        self.response_templates = {
            'greeting': {
                'first_time': [
                    "Hello {name}! I'm AgriBot, your AI farming assistant. I'm here to help with any agricultural questions you have. What would you like to know about farming today?",
                    "Welcome {name}! I specialize in agricultural guidance for farmers in Cameroon. How can I help you with your crops today?",
                    "Hi {name}! Ready to talk farming? I can help with everything from planting to harvest. What's on your mind?"
                ],
                'returning': [
                    "Welcome back {name}! Good to see you again. What farming topic can I help you with today?",
                    "Hello again {name}! How's your farming going? What would you like to discuss?",
                    "Hi {name}! Ready for another farming discussion? What can I help you with?"
                ]
            },
            'disease_identification': {
                'initial': [
                    "I can help identify what might be affecting your {crop}. Can you describe what you're seeing? Look for things like leaf color changes, spots, wilting, or other symptoms.",
                    "Let's figure out what's happening with your {crop}. What symptoms are you noticing? The more details you can provide, the better I can help.",
                    "Plant diseases can be concerning, but many are treatable. Tell me about the symptoms you're seeing on your {crop}."
                ],
                'specific_disease': [
                    "Based on your description, this sounds like it could be {disease}. Here's what you need to know:",
                    "The symptoms you're describing are typical of {disease}. Let me explain the treatment options:",
                    "This appears to be {disease}, which is {severity} in {crop}. Here's how to handle it:"
                ]
            },
            'fertilizer_advice': {
                'general': [
                    "For {crop} fertilization, timing and application are key. Here's what I recommend:",
                    "Let me guide you through the best fertilizer program for {crop}:",
                    "Proper nutrition is crucial for {crop} success. Here's the fertilizer approach I suggest:"
                ],
                'stage_specific': [
                    "At the {growth_stage} stage, your {crop} has specific nutritional needs. Here's what to apply:",
                    "This is the right time for {growth_stage} fertilization of {crop}. Here's the program:",
                    "Perfect timing for {growth_stage} feeding of your {crop}. Here's what to do:"
                ]
            },
            'planting_guidance': {
                'seasonal': [
                    "Great timing for planting {crop}! Since we're in the {season} season, here's your step-by-step guide:",
                    "You're asking about {crop} planting at the right time. For the {season} season, follow these steps:",
                    "{crop} is an excellent choice for this {season} season. Let me walk you through the process:"
                ],
                'general': [
                    "I'd love to help you grow {crop} successfully! Here's your complete planting guide:",
                    "Growing {crop} can be very rewarding. Let me guide you through the process:",
                    "{crop} is a great choice! Here's everything you need to know for successful planting:"
                ]
            }
        }
        
        # Response modifiers based on emotional context
        self.emotional_modifiers = {
            'high_concern': {
                'prefix': ["I understand this is concerning.", "I can see you're worried about this.", "This situation needs attention."],
                'tone': 'supportive'
            },
            'frustration': {
                'prefix': ["I know this can be frustrating.", "Let's solve this step by step.", "I'm here to help you through this."],
                'tone': 'patient'
            },
            'urgency': {
                'prefix': ["Let's address this quickly.", "This needs immediate attention.", "Here's what to do right away:"],
                'tone': 'direct'
            },
            'curiosity': {
                'prefix': ["Great question!", "I'm happy to explain.", "Let me share what I know about this."],
                'tone': 'educational'
            }
        }
        
        # Follow-up suggestion generators
        self.follow_up_generators = {
            'disease_identification': self._generate_disease_followups,
            'fertilizer_advice': self._generate_fertilizer_followups,
            'planting_guidance': self._generate_planting_followups,
            'pest_control': self._generate_pest_followups,
            'harvest_timing': self._generate_harvest_followups
        }
    
    def build_response(self, intent_result, entities, sentiment: SentimentScore,
                      emotional_context: EmotionalContext, conversation_context: Dict,
                      external_data: Dict = None) -> Dict[str, Any]:
        """Build comprehensive response based on all analysis results"""
        
        try:
            # Determine response strategy
            response_strategy = self._determine_response_strategy(
                intent_result, sentiment, emotional_context
            )
            
            # Build main response content
            main_response = self._build_main_response(
                intent_result, entities, conversation_context, external_data
            )
            
            # Apply emotional adaptations
            adapted_response = self._apply_emotional_adaptations(
                main_response, sentiment, emotional_context, response_strategy
            )
            
            # Generate follow-up suggestions
            follow_ups = self._generate_follow_up_suggestions(
                intent_result, entities, conversation_context
            )
            
            # Add encouraging elements if needed
            if response_strategy.get('add_encouragement', False):
                adapted_response = self._add_encouragement(adapted_response, entities)
            
            return {
                'response': adapted_response,
                'follow_up_suggestions': follow_ups,
                'response_metadata': {
                    'intent': intent_result.intent,
                    'confidence': intent_result.confidence,
                    'emotional_adaptation': response_strategy,
                    'entities_used': self._get_entities_used(entities),
                    'knowledge_sources': self._get_knowledge_sources_used(intent_result, entities)
                }
            }
            
        except Exception as e:
            # Fallback response for any errors
            print(f"RESPONSE BUILDER ERROR: {str(e)}")
            print(f"Intent: {getattr(intent_result, 'intent', 'unknown')}")
            print(f"Entities: {entities}")
            return {
                'response': self._build_fallback_response(intent_result, entities),
                'follow_up_suggestions': self._get_default_suggestions(),
                'response_metadata': {
                    'error': str(e),
                    'fallback_used': True
                }
            }
    
    def _determine_response_strategy(self, intent_result, sentiment: SentimentScore,
                                   emotional_context: EmotionalContext) -> Dict[str, Any]:
        """Determine how to adapt response based on emotional analysis"""
        strategy = {
            'tone': 'neutral',
            'empathy_level': 'standard',
            'detail_level': 'standard',
            'add_encouragement': False,
            'urgency_level': 'normal'
        }
        
        # Adjust based on sentiment
        if sentiment.polarity < -0.5:
            strategy['tone'] = 'supportive'
            strategy['empathy_level'] = 'high'
            strategy['add_encouragement'] = True
        elif sentiment.polarity > 0.5:
            strategy['tone'] = 'enthusiastic'
        
        # Adjust based on emotional context
        if emotional_context.urgency_level in ['high', 'critical']:
            strategy['urgency_level'] = 'high'
            strategy['detail_level'] = 'concise'
        
        if emotional_context.concern_level in ['high', 'severe']:
            strategy['empathy_level'] = 'high'
            strategy['add_encouragement'] = True
        
        if emotional_context.frustration_indicators:
            strategy['tone'] = 'patient'
            strategy['empathy_level'] = 'high'
        
        return strategy
    
    def _build_main_response(self, intent_result, entities, conversation_context: Dict,
                           external_data: Dict = None) -> str:
        """Build the main response content"""
        intent = intent_result.intent
        
        # Route to appropriate response builder
        if intent == 'greeting':
            return self._build_greeting_response(conversation_context)
        elif intent == 'disease_identification':
            return self._build_disease_response(entities, external_data)
        elif intent == 'pest_control':
            return self._build_pest_response(entities, external_data)
        elif intent == 'fertilizer_advice':
            return self._build_fertilizer_response(entities, conversation_context)
        elif intent == 'planting_guidance':
            return self._build_planting_response(entities, conversation_context)
        elif intent == 'harvest_timing':
            return self._build_harvest_response(entities, external_data)
        elif intent == 'yield_optimization':
            return self._build_yield_response(entities, conversation_context)
        elif intent == 'weather_inquiry':
            return self._build_weather_response(entities, external_data, conversation_context)
        elif intent == 'market_information':
            return self._build_market_response(entities, external_data)
        elif intent in ['thanks', 'goodbye']:
            return self._build_acknowledgment_response(intent, conversation_context)
        else:
            return self._build_general_response(entities, conversation_context)
    
    def _build_disease_response(self, entities, external_data: Dict = None) -> str:
        """Build response for disease identification queries"""
        crops = self._extract_entities_by_type(entities, 'crops')
        diseases = self._extract_entities_by_type(entities, 'diseases')
        
        if not crops:
            return ("I'd be happy to help identify plant diseases! Which crop is having problems? "
                   "Also, can you describe the symptoms you're seeing - like leaf color changes, "
                   "spots, wilting, or other signs?")
        
        crop = crops[0]
        response_parts = []
        
        if diseases:
            # Specific disease mentioned
            disease = diseases[0]
            disease_info = self.knowledge_base.get_disease_info(crop, disease)
            
            if 'error' not in disease_info:
                response_parts.append(f"You're asking about {disease} in {crop}. This is a significant concern.")
                response_parts.append(f"**Symptoms to look for:** {', '.join(disease_info['symptoms'][:3])}")
                response_parts.append(f"**Treatment options:** {', '.join(disease_info['treatment'][:3])}")
                response_parts.append(f"**Prevention:** {', '.join(disease_info['prevention'][:2])}")
            else:
                response_parts.append(f"I don't have specific information about {disease} in {crop}, but let me help with general disease management.")
                response_parts.append(self._get_general_disease_advice(crop))
        else:
            # General disease inquiry
            disease_info = self.knowledge_base.get_disease_info(crop)
            
            if 'error' not in disease_info:
                response_parts.append(f"I can help identify diseases in {crop}. Here are the most common ones to watch for:")
                
                diseases_list = disease_info.get('available_diseases', [])[:3]
                for i, disease in enumerate(diseases_list, 1):
                    disease_name = disease.replace('_', ' ').title()
                    response_parts.append(f"{i}. **{disease_name}**")
                
                response_parts.append("To give you more specific help, can you describe what you're seeing? "
                                    "Look for changes in leaf color, spots, wilting, or other symptoms.")
            else:
                response_parts.append(self._get_general_disease_advice(crop))
        
        return '\n\n'.join(response_parts)
    
    def _build_fertilizer_response(self, entities, conversation_context: Dict) -> str:
        """Build fertilizer recommendation response"""
        crops = self._extract_entities_by_type(entities, 'crops')
        
        if not crops:
            return ("I'd be happy to help with fertilizer recommendations! Which crop are you planning to fertilize? "
                   "I can provide specific programs for all major crops grown in Cameroon.")
        
        crop = crops[0]
        fertilizer_info = self.knowledge_base.get_fertilizer_recommendation(crop)
        
        response_parts = []
        response_parts.append(f"Here's the fertilizer program I recommend for {crop}:")
        
        if 'complete_program' in fertilizer_info:
            program = fertilizer_info['complete_program']
            
            # Basal application
            if 'basal_application' in program:
                basal = program['basal_application']
                response_parts.append(f"**At Planting:** {basal['fertilizer']} at {basal['rate']}")
                response_parts.append(f"*Application:* {basal['method']}")
            
            # Top dressing
            if 'top_dressing' in program:
                top = program['top_dressing']
                response_parts.append(f"**Top Dressing:** {top['fertilizer']} at {top['rate']}")
                response_parts.append(f"*Timing:* {top['timing']}")
                response_parts.append(f"*Method:* {top['method']}")
            
            # Organic options
            if 'organic_options' in program:
                response_parts.append("**Organic Alternatives:**")
                organic = program['organic_options']
                for option, details in organic.items():
                    response_parts.append(f"• {option.replace('_', ' ').title()}: {details}")
        
        else:
            # Fallback general advice
            general = fertilizer_info.get('general_recommendation', {})
            response_parts.append(general.get('base_recommendation', 'Apply balanced NPK based on soil test'))
            response_parts.append(general.get('organic_option', 'Use compost as organic alternative'))
        
        response_parts.append("Remember to consider your soil type and local conditions. Would you like specific application timing advice?")
        
        return '\n\n'.join(response_parts)
    
    def _build_planting_response(self, entities, conversation_context: Dict) -> str:
        """Build planting guidance response"""
        crops = self._extract_entities_by_type(entities, 'crops')
        
        if not crops:
            return ("I'd love to help you with planting guidance! Which crop are you interested in growing? "
                   "I have detailed planting procedures for all major crops in Cameroon.")
        
        crop = crops[0]
        planting_info = self.knowledge_base.get_planting_guide(crop)
        
        response_parts = []

        # Much more natural and conversational opening variations
        opening_variations = [
            f"Alright, let's talk about growing {crop}! Here's what works best:",
            f"Great choice asking about {crop}! I've helped many farmers with this one. Here's the approach that works:",
            f"Perfect timing! {crop} is actually one of my favorites to help with. Let me share what I know:",
            f"You want to plant {crop}? Excellent! Here's the method that gives farmers the best results:",
            f"I love helping with {crop} cultivation! Here's my step-by-step approach:",
            f"Absolutely! {crop} is definitely manageable. Here's how successful farmers do it:",
            f"Smart question about {crop}! Let me break down the process that works consistently:"
        ]
        response_parts.append(random.choice(opening_variations))
        
        if 'land_preparation' in planting_info:
            # Land preparation with natural headers
            if planting_info['land_preparation']:
                land_headers = ["**First, let's prep your land:**", "**Start with land preparation:**", "**Step 1 - Get your field ready:**"]
                response_parts.append(random.choice(land_headers))
                for step in planting_info['land_preparation'][:3]:
                    response_parts.append(f"• {step}")

            # Seed preparation with natural headers
            if planting_info.get('seed_preparation'):
                seed_headers = ["**Next, prepare your seeds:**", "**Now for the seeds:**", "**Step 2 - Seed preparation:**"]
                response_parts.append(random.choice(seed_headers))
                for step in planting_info['seed_preparation'][:2]:
                    response_parts.append(f"• {step}")

            # Planting process with natural headers
            if planting_info.get('planting_process'):
                plant_headers = ["**Time to plant:**", "**Now for the actual planting:**", "**Step 3 - Getting them in the ground:**"]
                response_parts.append(random.choice(plant_headers))
                for step in planting_info['planting_process'][:3]:
                    response_parts.append(f"• {step}")
            
            # Timing information
            if 'timing_guide' in planting_info:
                timing = planting_info['timing_guide']
                response_parts.append(f"**Best Timing:** {timing.get('optimal_harvest_time', 'Follow seasonal calendar')}")
        
        else:
            response_parts.append(planting_info.get('general_steps', 'Follow general planting principles'))
        
        # Vary the closing line to make responses feel more natural
        closing_variations = [
            "This should get you started successfully! Would you like more details about any specific step?",
            "Follow these steps and you'll have a great harvest! Any questions about a particular stage?",
            "That covers the main planting process! Need more specifics on any of these steps?",
            "This guide will help you plant successfully! What would you like to dive deeper into?",
            "These steps will set you up for success! Would you like details about any particular aspect?"
        ]
        response_parts.append(random.choice(closing_variations))
        return '\n\n'.join(response_parts)
    
    def _build_weather_response(self, entities, external_data: Dict, conversation_context: Dict) -> str:
        """Build weather-related agricultural response"""
        regions = self._extract_entities_by_type(entities, 'regions')
        crops = self._extract_entities_by_type(entities, 'crops')
        
        user_region = regions[0] if regions else conversation_context.get('user_preferences', {}).get('region', 'centre')
        
        response_parts = []
        
        # Use external weather data if available
        if external_data and 'weather_analysis' in external_data:
            weather_data = external_data['weather_analysis']

            if 'error' not in weather_data:
                response_parts.append(f"Here are the current agricultural conditions for {user_region} region:")

                current_conditions = weather_data.get('current_conditions', {})
                if current_conditions:
                    temp = current_conditions.get('temperature', 'N/A')
                    humidity = current_conditions.get('humidity', 'N/A')
                    response_parts.append(f"**Current Conditions:** {temp}°C, {humidity}% humidity")
                else:
                    # Fallback when no current conditions available
                    response_parts.append("**Current Status:** Weather monitoring in progress for agricultural planning")

                recommendations = weather_data.get('recommendations', [])
                if recommendations:
                    response_parts.append("**Agricultural Recommendations:**")
                    for rec in recommendations[:3]:
                        response_parts.append(f"• {rec}")
                else:
                    # Always provide some agricultural advice
                    response_parts.append("**General Agricultural Advice:**")
                    response_parts.append("• Monitor soil moisture levels regularly")
                    response_parts.append("• Adjust irrigation based on rainfall patterns")
                    response_parts.append("• Watch for weather changes affecting crop health")
            else:
                response_parts.append(f"I couldn't get current weather data for {user_region}, but I can provide general seasonal advice.")
        else:
            # Provide general weather guidance when no external data is available
            response_parts.append(f"I can provide general weather guidance for farming in {user_region} region:")
            response_parts.append("**General Weather Advice:**")
            response_parts.append("• Monitor daily rainfall patterns for irrigation planning")
            response_parts.append("• Watch for temperature changes that affect crop growth")
            response_parts.append("• Check humidity levels to prevent fungal diseases")
            response_parts.append("• Plan farm activities around weather forecasts")
        
        # Add crop-specific weather advice if crop mentioned
        if crops:
            crop = crops[0]
            response_parts.append(f"**For {crop} specifically:**")
            response_parts.append(f"Monitor weather conditions closely as they affect {crop} growth and disease pressure.")
            
            # Add seasonal advice
            response_parts.append(self._get_seasonal_weather_advice(crop, user_region))
        
        if not response_parts:
            response_parts.append(f"I can provide weather guidance for {user_region} region. What specific weather information do you need for farming?")
        
        return '\n\n'.join(response_parts)
    
    def _build_greeting_response(self, conversation_context: Dict) -> str:
        """Build greeting response"""
        user_name = conversation_context.get('user_preferences', {}).get('name', 'Friend')
        message_count = conversation_context.get('message_count', 0)
        
        if message_count == 0:
            template_type = 'first_time'
        else:
            template_type = 'returning'
        
        templates = self.response_templates['greeting'][template_type]
        template = random.choice(templates)
        
        return template.format(name=user_name)
    
    def _build_acknowledgment_response(self, intent: str, conversation_context: Dict) -> str:
        """Build acknowledgment responses for thanks/goodbye"""
        user_name = conversation_context.get('user_preferences', {}).get('name', 'Friend')
        
        if intent == 'thanks':
            responses = [
                f"You're very welcome, {user_name}! I'm here to help whenever you need farming advice.",
                "Happy to help! Feel free to ask if you have more questions about your crops.",
                "No problem at all! I'm always here for your agricultural questions."
            ]
        else:  # goodbye
            responses = [
                f"Goodbye {user_name}! Best of luck with your farming. Feel free to return anytime you need help.",
                "Take care! Remember, I'm always here when you need agricultural guidance.",
                f"Farewell {user_name}! Wishing you successful harvests. Come back anytime!"
            ]
        
        return random.choice(responses)
    
    def _build_general_response(self, entities, conversation_context: Dict) -> str:
        """Build general response when intent is unclear"""
        crops = self._extract_entities_by_type(entities, 'crops')
        
        if crops:
            crop = crops[0]
            return (f"I can help you with {crop} farming! What specifically would you like to know? "
                   f"I can provide guidance on planting, diseases, fertilizers, pest control, and harvesting.")
        else:
            return ("I'm here to help with your farming questions! I can assist with crops, diseases, "
                   "fertilizers, planting procedures, weather advice, and more. What would you like to know about?")
    
    def _apply_emotional_adaptations(self, response: str, sentiment: SentimentScore,
                                   emotional_context: EmotionalContext, strategy: Dict) -> str:
        """Apply emotional adaptations to response"""
        adapted_response = response
        
        # Add empathy prefix if needed
        if strategy['empathy_level'] == 'high':
            if emotional_context.concern_level in ['high', 'severe']:
                prefix = random.choice(self.emotional_modifiers['high_concern']['prefix'])
                adapted_response = f"{prefix} {adapted_response}"
            elif emotional_context.frustration_indicators:
                prefix = random.choice(self.emotional_modifiers['frustration']['prefix'])
                adapted_response = f"{prefix} {adapted_response}"
        
        # Add urgency indicator if needed
        if strategy['urgency_level'] == 'high':
            prefix = random.choice(self.emotional_modifiers['urgency']['prefix'])
            adapted_response = f"{prefix} {adapted_response}"
        
        # Modify tone for enthusiasm
        if strategy['tone'] == 'enthusiastic':
            adapted_response = adapted_response.replace("Here's", "Here's exactly")
            adapted_response = adapted_response.replace("I can help", "I'd be delighted to help")
        
        return adapted_response
    
    def _add_encouragement(self, response: str, entities) -> str:
        """Add encouraging elements to response"""
        crops = self._extract_entities_by_type(entities, 'crops')
        
        encouragements = [
            "Don't worry - most agricultural problems have good solutions!",
            "With proper care, your crops can recover and thrive.",
            "You're taking the right step by seeking guidance.",
            "Many farmers face similar challenges - you're not alone in this."
        ]
        
        if crops:
            crop = crops[0]
            encouragements.extend([
                f"{crop.title()} is a resilient crop with proper management.",
                f"I've helped many farmers successfully grow {crop}.",
                f"With the right approach, {crop} can be very rewarding to grow."
            ])
        
        encouragement = random.choice(encouragements)
        return f"{response}\n\n{encouragement}"
    
    def _generate_follow_up_suggestions(self, intent_result, entities, conversation_context: Dict) -> List[str]:
        """Generate contextual follow-up suggestions"""
        intent = intent_result.intent
        
        # Use specific generators if available
        if intent in self.follow_up_generators:
            return self.follow_up_generators[intent](entities, conversation_context)
        
        # Default suggestions based on entities
        crops = self._extract_entities_by_type(entities, 'crops')
        if crops:
            crop = crops[0]
            return [
                f"Tell me about diseases in {crop}",
                f"Fertilizer program for {crop}",
                f"When to harvest {crop}",
                f"Pest control for {crop}"
            ]
        
        return self._get_default_suggestions()
    
    def _generate_disease_followups(self, entities, conversation_context: Dict) -> List[str]:
        """Generate disease-related follow-up suggestions"""
        crops = self._extract_entities_by_type(entities, 'crops')
        
        if crops:
            crop = crops[0]
            return [
                f"Prevention tips for {crop} diseases",
                f"Organic treatments for {crop}",
                f"How to apply fungicides safely",
                f"Signs of {crop} recovery"
            ]
        
        return [
            "Disease prevention strategies",
            "Organic treatment options",
            "When to use fungicides",
            "Identifying plant recovery"
        ]
    
    def _generate_fertilizer_followups(self, entities, conversation_context: Dict) -> List[str]:
        """Generate fertilizer-related follow-up suggestions"""
        crops = self._extract_entities_by_type(entities, 'crops')
        
        if crops:
            crop = crops[0]
            return [
                f"Organic fertilizers for {crop}",
                f"Soil testing for {crop}",
                f"Fertilizer timing for {crop}",
                f"Signs of nutrient deficiency in {crop}"
            ]
        
        return [
            "Organic fertilizer options",
            "Soil testing advice",
            "Fertilizer application timing",
            "Nutrient deficiency signs"
        ]
    
    def _generate_planting_followups(self, entities, conversation_context: Dict) -> List[str]:
        """Generate planting-related follow-up suggestions"""
        crops = self._extract_entities_by_type(entities, 'crops')
        
        if crops:
            crop = crops[0]
            return [
                f"Best planting season for {crop}",
                f"Seed varieties of {crop}",
                f"Spacing requirements for {crop}",
                f"Post-planting care for {crop}"
            ]
        
        return [
            "Seasonal planting guide",
            "Seed selection tips",
            "Plant spacing advice",
            "Early crop care"
        ]
    
    def _generate_pest_followups(self, entities, conversation_context: Dict) -> List[str]:
        """Generate pest control follow-up suggestions"""
        crops = self._extract_entities_by_type(entities, 'crops')
        
        if crops:
            crop = crops[0]
            return [
                f"Natural pest control for {crop}",
                f"Pest monitoring in {crop}",
                f"Beneficial insects for {crop}",
                f"Pesticide safety for {crop}"
            ]
        
        return [
            "Natural pest control methods",
            "Pest monitoring techniques",
            "Beneficial insects guide",
            "Safe pesticide use"
        ]
    
    def _generate_harvest_followups(self, entities, conversation_context: Dict) -> List[str]:
        """Generate harvest-related follow-up suggestions"""
        crops = self._extract_entities_by_type(entities, 'crops')
        
        if crops:
            crop = crops[0]
            return [
                f"Storage methods for {crop}",
                f"Processing options for {crop}",
                f"Market prices for {crop}",
                f"Post-harvest handling of {crop}"
            ]
        
        return [
            "Crop storage techniques",
            "Value-added processing",
            "Market information",
            "Post-harvest best practices"
        ]
    
    def _extract_entities_by_type(self, entities, entity_type: str) -> List[str]:
        """Extract entities of specific type from entities result"""
        if not entities or not hasattr(entities, 'entities'):
            return []
        
        entity_matches = entities.entities.get(entity_type, [])
        return [match.normalized_form for match in entity_matches] if entity_matches else []
    
    def _get_entities_used(self, entities) -> List[str]:
        """Get summary of entities used in response building"""
        if not entities or not hasattr(entities, 'entities'):
            return []
        
        used_entities = []
        for entity_type, entity_list in entities.entities.items():
            if entity_list:
                used_entities.extend([f"{entity_type}:{entity.normalized_form}" for entity in entity_list])
        
        return used_entities
    
    def _get_knowledge_sources_used(self, intent_result, entities) -> List[str]:
        """Identify which knowledge sources were used"""
        sources = []
        
        if intent_result.intent in ['disease_identification', 'pest_control']:
            sources.append('disease_database')
        elif intent_result.intent == 'fertilizer_advice':
            sources.append('fertilizer_guide')
        elif intent_result.intent == 'planting_guidance':
            sources.append('planting_procedures')
        
        if self._extract_entities_by_type(entities, 'crops'):
            sources.append('crop_database')
        
        if self._extract_entities_by_type(entities, 'regions'):
            sources.append('regional_expertise')
        
        return sources
    
    def _build_fallback_response(self, intent_result, entities) -> str:
        """Build fallback response when main response building fails"""
        crops = self._extract_entities_by_type(entities, 'crops')

        if crops:
            crop = crops[0]
            # Multiple variations to prevent identical responses
            variations = [
                f"I can help you with {crop} farming! What specific aspect would you like to know about?",
                f"Great question about {crop}! I have lots of information on {crop} cultivation. What would you like to focus on?",
                f"I'd be happy to assist with {crop} farming. What particular area interests you most?",
                f"Let me help you with {crop}! I can provide guidance on various aspects of {crop} farming. What would you like to explore?",
                f"I understand you're asking about {crop}. I can help with general information about {crop} farming. What specific aspect interests you most?"
            ]
            return random.choice(variations)
        else:
            # Variations for general farming questions
            general_variations = [
                "I'm here to help with your farming question! Could you tell me more about what you'd like to know?",
                "Happy to assist with farming guidance! What specific topic can I help you with today?",
                "I want to help with your farming question. Could you provide a bit more detail about what you'd like to know? I can assist with crops, diseases, fertilizers, and more.",
                "Let me help you with that! What aspect of farming would you like to discuss? I cover crops, pest control, fertilizers, and much more.",
                "I'm ready to help with your agricultural question! What would you like to learn about today?"
            ]
            return random.choice(general_variations)
    
    def _get_default_suggestions(self) -> List[str]:
        """Get default follow-up suggestions"""
        return [
            "Ask about crop diseases",
            "Get fertilizer recommendations", 
            "Learn about planting procedures",
            "Weather advice for farming"
        ]
    
    def _get_general_disease_advice(self, crop: str) -> str:
        """Get general disease management advice"""
        return (f"For general {crop} disease management, focus on: proper spacing for air circulation, "
               f"avoiding overhead watering, using certified seeds, and monitoring plants regularly for early signs of problems.")
    
    def _get_seasonal_weather_advice(self, crop: str, region: str) -> str:
        """Get seasonal weather advice for crop and region"""
        return (f"For {crop} in {region} region, monitor rainfall patterns and temperature changes. "
               f"Adjust planting and management practices based on seasonal weather forecasts.")

    def _build_harvest_response(self, entities, conversation_context: Dict) -> str:
        """Build harvest timing and guidance response"""
        crops = self._extract_entities_by_type(entities, 'crops')

        if not crops:
            return ("I'd be happy to help with harvest timing! Which crop are you planning to harvest? "
                   "I can provide specific guidance on timing, techniques, and post-harvest handling.")

        crop = crops[0]
        harvest_info = self.knowledge_base.get_harvest_timing(crop)

        response_parts = []

        # Natural opening variations for harvest guidance
        opening_variations = [
            f"Perfect! Let me help you with {crop} harvesting:",
            f"Great question about {crop} harvest! Here's what you need to know:",
            f"Timing is crucial for {crop} harvest. Here's the complete guide:",
            f"I love helping with harvest planning! Here's everything about {crop} harvesting:",
            f"Excellent timing question! Here's how to harvest {crop} properly:"
        ]
        response_parts.append(random.choice(opening_variations))

        # Add harvest timing information
        if harvest_info and 'timing_signs' in harvest_info:
            timing_headers = ["**Signs it's ready:**", "**Look for these indicators:**", "**Harvest when you see:**"]
            response_parts.append(random.choice(timing_headers))
            for sign in harvest_info['timing_signs'][:3]:
                response_parts.append(f"• {sign}")

        # Add harvest techniques
        if harvest_info and 'harvest_method' in harvest_info:
            method_headers = ["**Best harvesting approach:**", "**How to harvest properly:**", "**Harvesting technique:**"]
            response_parts.append(random.choice(method_headers))
            for method in harvest_info['harvest_method'][:2]:
                response_parts.append(f"• {method}")

        # Default advice if no specific info available
        if not harvest_info:
            response_parts.extend([
                "**General harvest timing:**",
                f"• Check {crop} regularly for maturity signs",
                "• Harvest during cool morning hours when possible",
                "• Handle produce gently to avoid damage"
            ])

        # Natural closing variations
        closing_variations = [
            "This should help you harvest at the perfect time! Any questions about storage?",
            "Follow these signs and you'll get the best harvest! Need storage advice next?",
            "Proper timing makes all the difference! Would you like post-harvest handling tips?",
            "This timing guide will ensure quality harvest! Interested in storage methods?"
        ]
        response_parts.append(random.choice(closing_variations))

        return '\n\n'.join(response_parts)

    def _build_market_response(self, entities, conversation_context: Dict) -> str:
        """Build market information and pricing response"""
        crops = self._extract_entities_by_type(entities, 'crops')
        regions = self._extract_entities_by_type(entities, 'regions')

        response_parts = []

        # Natural opening variations for market questions
        opening_variations = [
            "Let me help you with market information!",
            "Good question about market conditions! Here's what I know:",
            "Smart to check market trends! Here's the current situation:",
            "Market planning is crucial! Let me share what I can:",
            "Great business thinking! Here's the market insight:"
        ]
        response_parts.append(random.choice(opening_variations))

        if crops:
            crop = crops[0]
            response_parts.append(f"**{crop.title()} Market Information:**")

            # General market advice for the crop
            market_tips = [
                f"• {crop.title()} prices typically vary by season and quality grade",
                f"• Local markets often offer better prices for fresh {crop}",
                f"• Consider direct sales to consumers for premium pricing",
                f"• Group selling with other farmers can improve bargaining power"
            ]
            response_parts.extend(market_tips[:3])

        if regions:
            region = regions[0]
            response_parts.append(f"**For {region} region specifically:**")
            response_parts.extend([
                f"• Check local market days in {region} for best opportunities",
                f"• Consider transportation costs to major markets from {region}",
                f"• Connect with agricultural cooperatives in your area"
            ])

        # General market advice
        response_parts.extend([
            "**General market tips:**",
            "• Monitor seasonal price patterns for your crops",
            "• Build relationships with regular buyers",
            "• Consider value-added processing for better margins",
            "• Keep records of prices and quality to track trends"
        ])

        # Natural closing
        closing_variations = [
            "I wish I had real-time pricing data to share! Try checking local agricultural offices for current rates.",
            "Market success takes planning and relationships! Would you like tips on finding buyers?",
            "These strategies should help maximize your returns! Any questions about market preparation?",
            "Building market knowledge takes time! Want advice on improving crop quality for better prices?"
        ]
        response_parts.append(random.choice(closing_variations))

        return '\n\n'.join(response_parts)