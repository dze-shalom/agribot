"""
Sentiment Analyzer
Location: agribot/nlp/sentiment_analyzer.py

Analyzes sentiment and emotional tone in agricultural queries to better
understand user state and provide appropriate responses.
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from collections import Counter
from nlp.text_processor import TextProcessor, ProcessedText

@dataclass
class SentimentScore:
    """Data structure for sentiment analysis results"""
    polarity: float  # -1.0 (negative) to +1.0 (positive)
    subjectivity: float  # 0.0 (objective) to 1.0 (subjective)
    emotional_tone: str  # primary emotional category
    confidence: float  # confidence in analysis
    emotional_indicators: List[str]  # words that influenced the score

@dataclass
class EmotionalContext:
    """Context information about user's emotional state"""
    urgency_level: str  # low, medium, high, critical
    frustration_indicators: List[str]
    concern_level: str  # minimal, moderate, high, severe
    help_seeking_intensity: str  # casual, moderate, urgent, desperate

class SentimentAnalyzer:
    """Agricultural domain-aware sentiment analysis"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        
        # Positive sentiment words (agricultural context)
        self.positive_words = {
            'general': ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                       'perfect', 'beautiful', 'healthy', 'strong', 'thriving'],
            'agricultural': ['growing', 'blooming', 'flourishing', 'productive', 'fertile',
                           'abundant', 'successful', 'improving', 'recovery', 'harvest']
        }
        
        # Negative sentiment words (agricultural context)
        self.negative_words = {
            'general': ['bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate',
                       'worst', 'failed', 'broken', 'destroyed'],
            'agricultural': ['dying', 'dead', 'diseased', 'infected', 'damaged', 'ruined',
                           'wilting', 'rotting', 'failed', 'pest', 'destroyed', 'loss']
        }
        
        # Emotional tone indicators
        self.emotional_tones = {
            'worry': ['worried', 'concerned', 'anxious', 'nervous', 'scared', 'afraid'],
            'frustration': ['frustrated', 'annoyed', 'angry', 'mad', 'irritated'],
            'desperation': ['desperate', 'helpless', 'hopeless', 'lost', 'confused'],
            'satisfaction': ['satisfied', 'happy', 'pleased', 'content', 'relieved'],
            'curiosity': ['curious', 'interested', 'wondering', 'learning'],
            'urgency': ['urgent', 'emergency', 'quickly', 'immediately', 'asap', 'help']
        }
        
        # Intensity modifiers
        self.intensifiers = {
            'high': ['very', 'extremely', 'incredibly', 'totally', 'completely', 'absolutely'],
            'medium': ['quite', 'rather', 'pretty', 'fairly', 'somewhat'],
            'low': ['a bit', 'slightly', 'little', 'kind of', 'sort of']
        }
        
        # Negation words
        self.negations = ['not', 'no', 'never', 'none', 'nothing', 'nowhere', 'neither',
                         'nobody', 'cannot', 'can\'t', 'won\'t', 'shouldn\'t', 'wouldn\'t',
                         'don\'t', 'doesn\'t', 'didn\'t', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t']
        
        # Agricultural problem severity indicators
        self.severity_indicators = {
            'mild': ['slight', 'small', 'little', 'minor', 'beginning'],
            'moderate': ['some', 'moderate', 'noticeable', 'concerning'],
            'severe': ['serious', 'major', 'severe', 'bad', 'terrible'],
            'critical': ['dying', 'dead', 'destroyed', 'ruined', 'emergency', 'urgent']
        }
    
    def analyze_sentiment(self, text: str, context: Dict = None) -> SentimentScore:
        """Analyze sentiment of input text"""
        if not text or not text.strip():
            return SentimentScore(
                polarity=0.0,
                subjectivity=0.0,
                emotional_tone='neutral',
                confidence=0.0,
                emotional_indicators=[]
            )
        
        # Process text
        processed = self.text_processor.process_text(text)
        
        # Calculate polarity score
        polarity, polarity_indicators = self._calculate_polarity(processed, text.lower())
        
        # Calculate subjectivity
        subjectivity = self._calculate_subjectivity(processed)
        
        # Determine primary emotional tone
        emotional_tone, emotion_confidence = self._determine_emotional_tone(processed, text.lower())
        
        # Overall confidence based on indicator strength
        confidence = self._calculate_confidence(polarity_indicators, emotion_confidence, len(processed.normalized_tokens))
        
        return SentimentScore(
            polarity=polarity,
            subjectivity=subjectivity,
            emotional_tone=emotional_tone,
            confidence=confidence,
            emotional_indicators=polarity_indicators
        )
    
    def analyze_emotional_context(self, text: str, sentiment: SentimentScore = None) -> EmotionalContext:
        """Analyze emotional context for better response adaptation"""
        if not sentiment:
            sentiment = self.analyze_sentiment(text)
        
        text_lower = text.lower()
        
        # Assess urgency level
        urgency = self._assess_urgency(text_lower, sentiment)
        
        # Identify frustration indicators
        frustration_indicators = self._identify_frustration_indicators(text_lower)
        
        # Assess concern level
        concern_level = self._assess_concern_level(text_lower, sentiment)
        
        # Assess help-seeking intensity
        help_seeking_intensity = self._assess_help_seeking_intensity(text_lower, sentiment)
        
        return EmotionalContext(
            urgency_level=urgency,
            frustration_indicators=frustration_indicators,
            concern_level=concern_level,
            help_seeking_intensity=help_seeking_intensity
        )
    
    def _calculate_polarity(self, processed: ProcessedText, text_lower: str) -> Tuple[float, List[str]]:
        """Calculate polarity score (-1 to +1)"""
        positive_score = 0
        negative_score = 0
        indicators = []
        tokens = processed.normalized_tokens
        
        # Check for negation context
        negated_context = self._get_negated_regions(text_lower)
        
        # Score positive words
        for category, words in self.positive_words.items():
            for word in words:
                if word in tokens:
                    # Check if word is in negated context
                    is_negated = self._is_word_negated(word, text_lower, negated_context)
                    
                    if is_negated:
                        negative_score += 1
                        indicators.append(f"negated_{word}")
                    else:
                        weight = 1.5 if category == 'agricultural' else 1.0
                        positive_score += weight
                        indicators.append(word)
        
        # Score negative words
        for category, words in self.negative_words.items():
            for word in words:
                if word in tokens:
                    # Check if word is in negated context
                    is_negated = self._is_word_negated(word, text_lower, negated_context)
                    
                    if is_negated:
                        positive_score += 1
                        indicators.append(f"negated_{word}")
                    else:
                        weight = 1.5 if category == 'agricultural' else 1.0
                        negative_score += weight
                        indicators.append(word)
        
        # Apply intensity modifiers
        intensity_multiplier = self._calculate_intensity_multiplier(text_lower)
        positive_score *= intensity_multiplier
        negative_score *= intensity_multiplier
        
        # Calculate final polarity
        total_score = positive_score + negative_score
        if total_score == 0:
            polarity = 0.0
        else:
            polarity = (positive_score - negative_score) / total_score
        
        # Clamp to [-1, 1]
        polarity = max(-1.0, min(1.0, polarity))
        
        return polarity, indicators
    
    def _calculate_subjectivity(self, processed: ProcessedText) -> float:
        """Calculate subjectivity score (0 to 1)"""
        subjective_indicators = 0
        objective_indicators = 0
        
        # Subjective words
        subjective_words = ['think', 'feel', 'believe', 'opinion', 'seems', 'appears',
                           'probably', 'maybe', 'might', 'could', 'should', 'would']
        
        # Objective words
        objective_words = ['is', 'are', 'was', 'were', 'has', 'have', 'will', 'did',
                          'fact', 'data', 'research', 'study', 'evidence']
        
        tokens = processed.normalized_tokens
        
        for token in tokens:
            if token in subjective_words:
                subjective_indicators += 1
            elif token in objective_words:
                objective_indicators += 1
        
        # Emotional words increase subjectivity
        for tone_words in self.emotional_tones.values():
            for word in tone_words:
                if word in tokens:
                    subjective_indicators += 0.5
        
        # Calculate subjectivity
        total_indicators = subjective_indicators + objective_indicators
        if total_indicators == 0:
            return 0.5  # Neutral subjectivity
        
        return min(1.0, subjective_indicators / total_indicators)
    
    def _determine_emotional_tone(self, processed: ProcessedText, text_lower: str) -> Tuple[str, float]:
        """Determine primary emotional tone"""
        emotion_scores = {}
        
        for emotion, words in self.emotional_tones.items():
            score = 0
            for word in words:
                if word in processed.normalized_tokens:
                    score += 1
                # Also check for partial matches in original text
                if word in text_lower:
                    score += 0.5
            emotion_scores[emotion] = score
        
        # Find dominant emotion
        if not emotion_scores or max(emotion_scores.values()) == 0:
            return 'neutral', 0.0
        
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = min(1.0, emotion_scores[dominant_emotion] / 3.0)
        
        return dominant_emotion, confidence
    
    def _calculate_confidence(self, indicators: List[str], emotion_confidence: float, token_count: int) -> float:
        """Calculate overall confidence in sentiment analysis"""
        # Base confidence from number of indicators
        indicator_confidence = min(1.0, len(indicators) / 5.0)
        
        # Text length factor (very short texts are less reliable)
        length_factor = min(1.0, token_count / 5.0)
        
        # Combine factors
        overall_confidence = (indicator_confidence + emotion_confidence + length_factor) / 3.0
        
        return round(overall_confidence, 3)
    
    def _get_negated_regions(self, text_lower: str) -> List[Tuple[int, int]]:
        """Find regions of text that are negated"""
        negated_regions = []
        
        for negation in self.negations:
            pattern = r'\b' + re.escape(negation) + r'\b'
            for match in re.finditer(pattern, text_lower):
                # Negation affects next 5 words
                start_pos = match.start()
                # Find end of negation scope (roughly 5 words or next punctuation)
                remaining_text = text_lower[match.end():]
                words_after = remaining_text.split()[:5]
                end_pos = match.end() + len(' '.join(words_after))
                
                negated_regions.append((start_pos, end_pos))
        
        return negated_regions
    
    def _is_word_negated(self, word: str, text_lower: str, negated_regions: List[Tuple[int, int]]) -> bool:
        """Check if a word appears in negated context"""
        word_positions = [m.start() for m in re.finditer(r'\b' + re.escape(word) + r'\b', text_lower)]
        
        for word_pos in word_positions:
            for neg_start, neg_end in negated_regions:
                if neg_start <= word_pos <= neg_end:
                    return True
        
        return False
    
    def _calculate_intensity_multiplier(self, text_lower: str) -> float:
        """Calculate intensity multiplier based on intensifier words"""
        multiplier = 1.0
        
        for intensity_level, words in self.intensifiers.items():
            for word in words:
                if word in text_lower:
                    if intensity_level == 'high':
                        multiplier *= 1.5
                    elif intensity_level == 'medium':
                        multiplier *= 1.2
                    # Low intensifiers actually reduce intensity
                    elif intensity_level == 'low':
                        multiplier *= 0.8
        
        return multiplier
    
    def _assess_urgency(self, text_lower: str, sentiment: SentimentScore) -> str:
        """Assess urgency level of the request"""
        urgency_indicators = {
            'critical': ['emergency', 'urgent', 'dying', 'dead', 'help me', 'asap', 'immediately'],
            'high': ['quickly', 'fast', 'soon', 'worried', 'concerned', 'serious'],
            'medium': ['need', 'should', 'important', 'problem'],
            'low': ['when', 'how', 'what', 'curious', 'wondering']
        }
        
        for level in ['critical', 'high', 'medium', 'low']:
            for indicator in urgency_indicators[level]:
                if indicator in text_lower:
                    return level
        
        # Also consider negative sentiment as indicator of urgency
        if sentiment.polarity < -0.5:
            return 'high'
        elif sentiment.polarity < -0.2:
            return 'medium'
        
        return 'low'
    
    def _identify_frustration_indicators(self, text_lower: str) -> List[str]:
        """Identify indicators of user frustration"""
        frustration_words = ['frustrated', 'annoyed', 'angry', 'mad', 'irritated',
                           'tried everything', 'nothing works', 'still', 'again', 
                           'keep', 'always', 'why does', 'what else']
        
        indicators = []
        for word in frustration_words:
            if word in text_lower:
                indicators.append(word)
        
        # Look for repetitive patterns
        if 'still' in text_lower and any(word in text_lower for word in ['problem', 'issue', 'not working']):
            indicators.append('persistent_problem')
        
        return indicators
    
    def _assess_concern_level(self, text_lower: str, sentiment: SentimentScore) -> str:
        """Assess user's level of concern"""
        # Check for severity indicators
        for level, indicators in self.severity_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    severity_map = {
                        'critical': 'severe',
                        'severe': 'severe',
                        'moderate': 'high',
                        'mild': 'moderate'
                    }
                    return severity_map.get(level, 'moderate')
        
        # Use sentiment as fallback
        if sentiment.polarity < -0.6:
            return 'severe'
        elif sentiment.polarity < -0.3:
            return 'high'
        elif sentiment.polarity < 0:
            return 'moderate'
        else:
            return 'minimal'
    
    def _assess_help_seeking_intensity(self, text_lower: str, sentiment: SentimentScore) -> str:
        """Assess intensity of help-seeking behavior"""
        desperate_indicators = ['please help', 'don\'t know what to do', 'desperate',
                              'need help badly', 'losing everything']
        urgent_indicators = ['need help', 'help me', 'what should i do', 'urgent']
        moderate_indicators = ['can you help', 'advice', 'suggestions', 'what to do']
        casual_indicators = ['curious about', 'wondering', 'information', 'tell me about']
        
        if any(indicator in text_lower for indicator in desperate_indicators):
            return 'desperate'
        elif any(indicator in text_lower for indicator in urgent_indicators):
            return 'urgent'
        elif any(indicator in text_lower for indicator in moderate_indicators):
            return 'moderate'
        elif any(indicator in text_lower for indicator in casual_indicators):
            return 'casual'
        
        # Use sentiment as fallback
        if sentiment.emotional_tone in ['desperation', 'urgency']:
            return 'urgent'
        elif sentiment.emotional_tone in ['worry', 'frustration']:
            return 'moderate'
        else:
            return 'casual'
    
    def get_response_adaptation_suggestions(self, sentiment: SentimentScore, 
                                          emotional_context: EmotionalContext) -> Dict[str, Any]:
        """Get suggestions for adapting response based on sentiment and emotion"""
        suggestions = {
            'tone_adjustment': 'neutral',
            'empathy_level': 'standard',
            'urgency_response': 'normal',
            'detail_level': 'standard',
            'encouragement_needed': False
        }
        
        # Tone adjustment
        if sentiment.polarity < -0.5:
            suggestions['tone_adjustment'] = 'supportive'
        elif sentiment.polarity > 0.5:
            suggestions['tone_adjustment'] = 'enthusiastic'
        
        # Empathy level
        if emotional_context.concern_level in ['severe', 'high']:
            suggestions['empathy_level'] = 'high'
        elif sentiment.emotional_tone in ['worry', 'frustration', 'desperation']:
            suggestions['empathy_level'] = 'elevated'
        
        # Urgency response
        if emotional_context.urgency_level in ['critical', 'high']:
            suggestions['urgency_response'] = 'immediate'
            suggestions['detail_level'] = 'concise'
        
        # Encouragement
        if sentiment.polarity < -0.3 or sentiment.emotional_tone in ['worry', 'desperation']:
            suggestions['encouragement_needed'] = True
        
        return suggestions