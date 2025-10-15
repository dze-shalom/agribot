"""
Claude API Service
Location: agribot/services/claude_service.py

Wrapper service for Claude API integration with agricultural context.
Provides natural conversation capabilities powered by Anthropic's Claude.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

try:
    import anthropic
    from anthropic import Anthropic
    _HAS_ANTHROPIC = True
except Exception:
    anthropic = None
    Anthropic = None
    _HAS_ANTHROPIC = False

from utils.exceptions import AgriBotException


@dataclass
class ConversationMessage:
    """Represents a single message in conversation context"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime


@dataclass
class ClaudeResponse:
    """Structured response from Claude API"""
    content: str
    confidence_score: float
    intent: str
    entities: Dict[str, Any]
    conversation_id: str
    processing_time: float


class ClaudeService:
    """Service wrapper for Claude API with agricultural expertise"""

    def __init__(self, api_key: str, agricultural_knowledge: Dict[str, Any]):
        """Initialize Claude service with API key and agricultural context"""
        if not _HAS_ANTHROPIC:
            raise RuntimeError('Anthropic package not installed; ClaudeService unavailable')

        self.client = Anthropic(api_key=api_key)
        self.agricultural_knowledge = agricultural_knowledge
        self.logger = logging.getLogger(__name__)

        # Conversation context storage (in production, use Redis or database)
        self.conversation_contexts: Dict[str, List[ConversationMessage]] = {}

        # System prompt for agricultural expertise
        self.system_prompt = self._build_system_prompt()

    def _detect_language(self, text: str) -> str:
        """Detect language from user input using simple heuristics"""
        text_lower = text.lower()

        # Strong English indicators (common English-only words)
        english_words = ['good morning', 'good afternoon', 'good evening', 'hello', 'hi', 'hey',
                         'please', 'thank you', 'thanks', 'what', 'when', 'where', 'why', 'how']
        english_count = sum(1 for word in english_words if word in text_lower)

        # French indicators (strong French-only words)
        french_words = ['bonjour', 'bonsoir', 'qu\'est-ce', 'quelle', 'quel', 'merci',
                        'pouvez-vous', 'voudrais', 'récolte', 's\'il vous plaît']
        french_count = sum(1 for word in french_words if word in text_lower)

        # Pidgin indicators
        pidgin_words = ['wetin', 'na', 'don', 'dey', 'abeg', 'sef', 'no dey', 'make we']
        pidgin_count = sum(1 for word in pidgin_words if word in text_lower)

        # Determine language with priority: English > French > Pidgin
        if english_count >= 1:
            return 'en'
        elif french_count >= 1:
            return 'fr'
        elif pidgin_count >= 1:
            return 'pcm'
        else:
            return 'en'  # Default to English

    def _build_system_prompt(self, language: str = 'auto') -> str:
        """Build the system prompt with agricultural knowledge context and language preference"""

        if language == 'auto':
            language_instruction = """IMPORTANT LANGUAGE INSTRUCTION:
- Automatically detect the language the user is writing in
- If the user writes in English, respond in English
- If the user writes in French, respond in French (Français)
- If the user writes in Pidgin English (West African Pidgin), respond in Pidgin
- Match the user's language exactly - this is crucial for farmer understanding
- Be flexible and recognize common language patterns"""
        else:
            language_instructions = {
                'en': 'Respond in English.',
                'fr': 'Répondez en français. Utilisez un vocabulaire agricole approprié et clair.',
                'pcm': 'Respond in Pidgin English (West African Pidgin). Use simple, conversational language that farmers understand easily.'
            }
            language_instruction = language_instructions.get(language, language_instructions['en'])

        return f"""You are AgriBot, an expert agricultural advisor for farmers WORLDWIDE. You provide practical, actionable advice about farming, crops, weather, and agricultural practices for ANY country or region in the world.

LANGUAGE REQUIREMENT:
{language_instruction}

AGRICULTURAL KNOWLEDGE BASE (Primary - Cameroon):
{json.dumps(self.agricultural_knowledge, indent=2)}

IMPORTANT - WORLDWIDE COVERAGE:
- You have agricultural knowledge for ALL countries and regions globally
- The knowledge base above is for Cameroon, but you can advise farmers from ANY country
- Adapt your advice to the user's country, climate zone, and local conditions
- If asked about countries other than Cameroon, provide accurate advice based on that country's agricultural practices

GUIDELINES:
1. **Location-Specific vs General Advice:**
   - WORLDWIDE: Answer questions about ANY country (Nigeria, Kenya, India, USA, etc.)
   - If the question is GENERAL (e.g., "How do I plant maize?"), provide universal best practices
   - If the question is REGION-SPECIFIC (e.g., "What should I plant in my area?", "here"), use the user's specific location
   - For questions about specific countries, provide country-specific advice even if it's not Cameroon
   - Consider climate zones: tropical, temperate, arid, mediterranean, etc.

2. Always provide practical, actionable advice applicable to the user's location
3. Be conversational and encouraging - farmers need support and confidence worldwide
4. Include specific steps, timing, and measurements when giving advice
5. Acknowledge limitations and suggest local agricultural extension services for any country
6. Use metric measurements (or imperial if appropriate for the country)
7. Consider seasonal patterns and climate conditions for the specific region/country
8. Be culturally sensitive and respectful of farming traditions worldwide
9. Encourage sustainable and environmentally friendly practices globally
10. If weather data is provided, integrate it into your advice
11. IMPORTANT: Do NOT address the user by name in your responses
12. Keep responses concise and focused on the question asked
13. Remember previous messages in the conversation - maintain context awareness

RESPONSE FORMAT:
- Give direct, practical answers in the user's preferred language
- Use bullet points or numbered steps for clarity
- Include relevant warnings or precautions
- Suggest follow-up actions when appropriate
- Be encouraging and supportive in tone
- Do NOT use the user's name in responses
- Reference previous conversation context when relevant (e.g., "Based on the image you shared earlier...")

Remember: You're helping real farmers make important decisions about their crops and livelihood. Be accurate, helpful, and caring in your responses."""

    def get_response(
        self,
        user_input: str,
        conversation_id: str,
        user_context: Optional[Dict[str, Any]] = None,
        weather_data: Optional[Dict[str, Any]] = None,
        market_data: Optional[Dict[str, Any]] = None,
        language: str = 'auto',
        stream: bool = False
    ) -> ClaudeResponse:
        """
        Get intelligent response from Claude with full agricultural context

        Args:
            user_input: The user's question or message
            conversation_id: Unique identifier for conversation context
            user_context: User profile info (region, crops, etc.)
            weather_data: Current weather conditions if available
            market_data: Market prices if available
            language: Language preference ('auto' for auto-detection, or 'en', 'fr', 'pcm')

        Returns:
            ClaudeResponse with content and metadata
        """
        try:
            start_time = datetime.now()

            # Auto-detect language if set to 'auto'
            if language == 'auto':
                detected_language = self._detect_language(user_input)
                self.logger.info(f"Detected language: {detected_language} for input: {user_input[:50]}")
            else:
                detected_language = language

            # Build contextual prompt
            contextual_prompt = self._build_contextual_prompt(
                user_input, user_context, weather_data, market_data
            )

            # Get conversation history
            conversation_history = self._get_conversation_history(conversation_id)

            # Prepare messages for Claude
            messages = []

            # Add conversation history
            for msg in conversation_history[-6:]:  # Keep last 6 messages for context
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Add current user message
            messages.append({
                "role": "user",
                "content": contextual_prompt
            })

            # Build language-specific system prompt with detected language
            system_prompt = self._build_system_prompt(detected_language)

            # Call Claude API with streaming support if requested
            if stream:
                # Return streaming response (generator)
                return self.client.messages.stream(
                    model="claude-3-haiku-20240307",
                    max_tokens=1000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=messages
                )
            else:
                # Regular blocking response
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=messages
                )

                # Extract response content
                response_content = response.content[0].text

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Update conversation context
            self._update_conversation_context(conversation_id, user_input, response_content)

            # Extract intent and entities (basic classification)
            intent, entities = self._analyze_response_metadata(user_input, response_content)

            # Calculate confidence score (based on response length and specificity)
            confidence_score = self._calculate_confidence_score(response_content)

            self.logger.info(f"Claude response generated for conversation {conversation_id} in {processing_time:.2f}s")

            return ClaudeResponse(
                content=response_content,
                confidence_score=confidence_score,
                intent=intent,
                entities=entities,
                conversation_id=conversation_id,
                processing_time=processing_time
            )

        except anthropic.APIError as e:
            self.logger.error(f"Claude API error: {str(e)}")
            raise AgriBotException(f"AI service temporarily unavailable: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error in Claude service: {str(e)}")
            raise AgriBotException(f"Failed to generate response: {str(e)}")

    def _build_contextual_prompt(
        self,
        user_input: str,
        user_context: Optional[Dict[str, Any]] = None,
        weather_data: Optional[Dict[str, Any]] = None,
        market_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build enriched prompt with all available context"""

        prompt_parts = [f"USER QUESTION: {user_input}"]

        if user_context:
            context_info = []
            if user_context.get('region'):
                context_info.append(f"User's region: {user_context['region']}")
            # Note: Do NOT include user's name to avoid repetitive personalization

            if context_info:
                prompt_parts.append(f"USER CONTEXT: {', '.join(context_info)}")
                prompt_parts.append("IMPORTANT: Only use this region info if the question is location-specific (e.g., 'in my area', 'here', 'my region'). For general questions, provide broad information applicable to all regions.")

        if weather_data:
            weather_info = []
            if weather_data.get('temperature'):
                weather_info.append(f"Temperature: {weather_data['temperature']}°C")
            if weather_data.get('humidity'):
                weather_info.append(f"Humidity: {weather_data['humidity']}%")
            if weather_data.get('conditions'):
                weather_info.append(f"Conditions: {weather_data['conditions']}")
            if weather_data.get('rainfall'):
                weather_info.append(f"Recent rainfall: {weather_data['rainfall']}mm")

            if weather_info:
                prompt_parts.append(f"CURRENT WEATHER: {', '.join(weather_info)}")

        if market_data and market_data.get('prices'):
            market_info = []
            for crop, price in market_data['prices'].items():
                market_info.append(f"{crop}: {price} FCFA/kg")

            if market_info:
                prompt_parts.append(f"MARKET PRICES: {', '.join(market_info)}")

        return "\n\n".join(prompt_parts)

    def _get_conversation_history(self, conversation_id: str) -> List[ConversationMessage]:
        """Get conversation history for context"""
        return self.conversation_contexts.get(conversation_id, [])

    def _update_conversation_context(
        self,
        conversation_id: str,
        user_input: str,
        claude_response: str
    ):
        """Update conversation context with new messages"""
        if conversation_id not in self.conversation_contexts:
            self.conversation_contexts[conversation_id] = []

        context = self.conversation_contexts[conversation_id]

        # Add user message
        context.append(ConversationMessage(
            role="user",
            content=user_input,
            timestamp=datetime.now()
        ))

        # Add Claude response
        context.append(ConversationMessage(
            role="assistant",
            content=claude_response,
            timestamp=datetime.now()
        ))

        # Keep only last 20 messages to manage memory
        if len(context) > 20:
            self.conversation_contexts[conversation_id] = context[-20:]

    def _analyze_response_metadata(self, user_input: str, response: str) -> tuple[str, Dict[str, Any]]:
        """Basic intent and entity extraction from user input and response"""

        # Simple keyword-based intent classification
        user_lower = user_input.lower()

        if any(word in user_lower for word in ['plant', 'planting', 'sow', 'seed']):
            intent = 'planting_guidance'
        elif any(word in user_lower for word in ['harvest', 'harvesting', 'when to harvest']):
            intent = 'harvest_guidance'
        elif any(word in user_lower for word in ['weather', 'rain', 'temperature', 'climate']):
            intent = 'weather_inquiry'
        elif any(word in user_lower for word in ['price', 'market', 'sell', 'selling']):
            intent = 'market_inquiry'
        elif any(word in user_lower for word in ['pest', 'disease', 'insect', 'fungus']):
            intent = 'pest_disease_management'
        elif any(word in user_lower for word in ['fertilizer', 'nutrients', 'soil']):
            intent = 'soil_fertility'
        else:
            intent = 'general_agriculture'

        # Extract crop mentions
        crops = []
        crop_keywords = ['maize', 'corn', 'tomato', 'pepper', 'cassava', 'plantain', 'cocoa', 'coffee', 'rice', 'beans']
        for crop in crop_keywords:
            if crop in user_lower:
                crops.append(crop)

        entities = {
            'crops': crops,
            'response_length': len(response),
            'user_input_length': len(user_input)
        }

        return intent, entities

    def _calculate_confidence_score(self, response: str) -> float:
        """Calculate confidence score based on response characteristics"""

        # Basic scoring based on response quality indicators
        score = 0.5  # Base score

        # Longer, more detailed responses get higher scores
        if len(response) > 500:
            score += 0.2
        elif len(response) > 200:
            score += 0.1

        # Responses with specific steps or numbers get higher scores
        if any(indicator in response.lower() for indicator in ['step', 'kg', 'cm', 'days', 'weeks']):
            score += 0.15

        # Responses with warnings or cautions show thoughtfulness
        if any(word in response.lower() for word in ['caution', 'warning', 'careful', 'important']):
            score += 0.1

        # Cap at 1.0
        return min(score, 1.0)

    def clear_conversation_context(self, conversation_id: str):
        """Clear conversation context for a specific conversation"""
        if conversation_id in self.conversation_contexts:
            del self.conversation_contexts[conversation_id]
            self.logger.info(f"Cleared conversation context for {conversation_id}")

    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get summary statistics for a conversation"""
        context = self.conversation_contexts.get(conversation_id, [])

        user_messages = [msg for msg in context if msg.role == "user"]
        assistant_messages = [msg for msg in context if msg.role == "assistant"]

        return {
            'total_messages': len(context),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'conversation_start': context[0].timestamp if context else None,
            'last_activity': context[-1].timestamp if context else None,
            'average_response_length': sum(len(msg.content) for msg in assistant_messages) / len(assistant_messages) if assistant_messages else 0
        }