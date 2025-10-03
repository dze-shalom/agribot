"""
NLP Package Initialization
Location: agribot/nlp/__init__.py

Provides natural language processing capabilities including text processing,
intent classification, entity extraction, and sentiment analysis.
"""

from .text_processor import TextProcessor, ProcessedText
from .intent_classifier import IntentClassifier, IntentResult
from .entity_extractor import EntityExtractor, EntityMatch, EntityExtractionResult
from .sentiment_analyzer import SentimentAnalyzer, SentimentScore, EmotionalContext

# Main NLP processor class that combines all components
class NLPProcessor:
    """Main NLP processor combining all NLP components"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def process(self, text: str, context: dict = None) -> dict:
        """Process text through all NLP components"""
        # Basic text processing
        processed_text = self.text_processor.process_text(text)
        
        # Intent classification
        intent_result = self.intent_classifier.classify_intent(text, context)
        
        # Entity extraction
        entities = self.entity_extractor.extract_entities(text, context)
        
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze_sentiment(text, context)
        emotional_context = self.sentiment_analyzer.analyze_emotional_context(text, sentiment)
        
        # Response adaptation suggestions
        response_suggestions = self.sentiment_analyzer.get_response_adaptation_suggestions(
            sentiment, emotional_context
        )
        
        return {
            'processed_text': processed_text,
            'intent': intent_result,
            'entities': entities,
            'sentiment': sentiment,
            'emotional_context': emotional_context,
            'response_suggestions': response_suggestions
        }

__all__ = [
    'TextProcessor',
    'ProcessedText',
    'IntentClassifier',
    'IntentResult', 
    'EntityExtractor',
    'EntityMatch',
    'EntityExtractionResult',
    'SentimentAnalyzer',
    'SentimentScore',
    'EmotionalContext',
    'NLPProcessor'
]