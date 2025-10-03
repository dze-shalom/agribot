"""
Intent Classifier
Location: agribot/nlp/intent_classifier.py

Classifies user intents for agricultural queries using rule-based patterns
and keyword matching specific to farming contexts.
"""

import re
from typing import Dict, List, Tuple, Any
from collections import defaultdict, Counter
from dataclasses import dataclass
from nlp.text_processor import TextProcessor, ProcessedText

@dataclass
class IntentResult:
    """Data structure for intent classification results"""
    intent: str
    confidence: float
    secondary_intents: List[Tuple[str, float]]
    matched_patterns: List[str]
    context_clues: Dict[str, List[str]]

class IntentClassifier:
    """Rule-based intent classifier for agricultural domain"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        
        # Define intent patterns with weights
        self.intent_patterns = {
            'greeting': {
                'keywords': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings'],
                'patterns': [
                    r'\b(hello|hi|hey)\b',
                    r'good\s+(morning|afternoon|evening)',
                    r'\b(greetings?|howdy)\b'
                ],
                'weight': 1.0
            },
            'thanks': {
                'keywords': ['thank you', 'thanks', 'thank u', 'thx', 'appreciate', 'grateful'],
                'patterns': [
                    r'\bthank\s*(you|u)\b',
                    r'\bthanks?\b',
                    r'\bappreciate\b',
                    r'\b(grateful|much obliged)\b'
                ],
                'weight': 1.0
            },
            'goodbye': {
                'keywords': ['bye', 'goodbye', 'see you', 'farewell', 'take care'],
                'patterns': [
                    r'\b(bye|goodbye)\b',
                    r'see\s+you',
                    r'\bfarewell\b',
                    r'take\s+care'
                ],
                'weight': 1.0
            },
            'disease_identification': {
                'keywords': ['disease', 'sick', 'dying', 'problem', 'spots', 'yellowing', 'wilting', 'rotting'],
                'patterns': [
                    r'\b(disease|sick|dying)\b',
                    r'\b(yellow|brown|black|white)\s+(spots?|leaves?)\b',
                    r'\b(wilt|rot|decay)\w*\b',
                    r'what.*(wrong|problem|issue)',
                    r'(leaves?|plant).*(turn|turning).*(yellow|brown)'
                ],
                'weight': 1.2,
                'context_indicators': ['symptoms', 'visual_problems', 'plant_health']
            },
            'pest_control': {
                'keywords': ['pest', 'insects', 'bugs', 'worms', 'caterpillar', 'aphid', 'control', 'damage'],
                'patterns': [
                    r'\b(pest|bug|insect)s?\b',
                    r'\b(worm|caterpillar|aphid|whitefly)s?\b',
                    r'\b(damage|attack|infestation)\b',
                    r'holes?\s+in\s+(leaves?|plant)',
                    r'eat\w*\s+(leaves?|plant)'
                ],
                'weight': 1.2,
                'context_indicators': ['pest_damage', 'insect_problems', 'crop_protection']
            },
            'fertilizer_advice': {
                'keywords': ['fertilizer', 'fertiliser', 'nutrition', 'nutrients', 'npk', 'manure', 'compost'],
                'patterns': [
                    r'\b(fertiliz|fertilis)\w*\b',
                    r'\b(nutrition|nutrients?|npk)\b',
                    r'\b(manure|compost|organic)\b',
                    r'what.*fertilizer',
                    r'(nitrogen|phosphorus|potassium)'
                ],
                'weight': 1.1,
                'context_indicators': ['soil_nutrition', 'crop_feeding', 'growth_enhancement']
            },
            'planting_guidance': {
                'keywords': ['plant', 'planting', 'sow', 'sowing', 'grow', 'cultivation', 'procedures'],
                'patterns': [
                    r'\b(plant|grow|cultivat)\w*\b',
                    r'\b(sow|sowing|seed)\w*\b',
                    r'how.*plant',
                    r'when.*plant',
                    r'procedures?\s+for',
                    r'steps?\s+(to|for).*grow'
                ],
                'weight': 1.1,
                'context_indicators': ['crop_establishment', 'farming_methods', 'agricultural_procedures']
            },
            'harvest_timing': {
                'keywords': ['harvest', 'harvesting', 'ready', 'maturity', 'ripe', 'picking'],
                'patterns': [
                    r'\bharvest\w*\b',
                    r'\b(ready|ripe|mature)\b',
                    r'when.*(harvest|pick|collect)',
                    r'time.*harvest',
                    r'\bmaturity\b'
                ],
                'weight': 1.0,
                'context_indicators': ['crop_maturity', 'harvest_planning', 'post_harvest']
            },
            'yield_optimization': {
                'keywords': ['yield', 'production', 'maximize', 'increase', 'improve', 'boost', 'more', 'higher'],
                'patterns': [
                    r'\byield\b',
                    r'\b(production|productivity)\b',
                    r'\b(maximize|increase|improve|boost)\b',
                    r'(more|higher|better).*(yield|production)',
                    r'how.*increase'
                ],
                'weight': 1.0,
                'context_indicators': ['productivity_improvement', 'farm_efficiency', 'crop_management']
            },
            'weather_inquiry': {
                'keywords': ['weather', 'rain', 'temperature', 'climate', 'forecast', 'season'],
                'patterns': [
                    r'\bweather\b',
                    r'\b(rain|rainfall|precipitation)\b',
                    r'\b(temperature|climate)\b',
                    r'\b(season|seasonal)\b',
                    r'weather.*affect'
                ],
                'weight': 1.0,
                'context_indicators': ['climate_conditions', 'seasonal_planning', 'weather_impact']
            },
            'market_information': {
                'keywords': ['price', 'market', 'sell', 'buy', 'cost', 'profit', 'money', 'income'],
                'patterns': [
                    r'\b(price|cost|market)\b',
                    r'\b(sell|buy|trade)\b',
                    r'\b(profit|income|money)\b',
                    r'how much.*sell',
                    r'market.*price'
                ],
                'weight': 1.0,
                'context_indicators': ['economics', 'marketing', 'financial_planning']
            },
            'general_inquiry': {
                'keywords': ['how', 'what', 'why', 'when', 'where', 'can', 'should', 'tell me'],
                'patterns': [
                    r'\b(how|what|why|when|where)\b',
                    r'\b(can|should|could|would)\b',
                    r'tell\s+me',
                    r'explain',
                    r'information\s+about'
                ],
                'weight': 0.8,
                'context_indicators': ['information_seeking', 'general_questions']
            }
        }
        
        # Intent confidence thresholds
        self.confidence_thresholds = {
            'high': 0.7,
            'medium': 0.4,
            'low': 0.2
        }
    
    def classify_intent(self, text: str, context: Dict = None) -> IntentResult:
        """Classify the intent of input text"""
        if not text or not text.strip():
            return IntentResult(
                intent='unknown',
                confidence=0.0,
                secondary_intents=[],
                matched_patterns=[],
                context_clues={}
            )
        
        # Process text
        processed = self.text_processor.process_text(text)
        
        # Score all intents
        intent_scores = self._score_intents(processed, context)
        
        # Get primary and secondary intents
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        if not sorted_intents or sorted_intents[0][1]['score'] == 0:
            return IntentResult(
                intent='unknown',
                confidence=0.0,
                secondary_intents=[],
                matched_patterns=[],
                context_clues={}
            )
        
        primary_intent, primary_data = sorted_intents[0]
        
        # Calculate confidence based on score and pattern matches
        confidence = self._calculate_confidence(primary_data['score'], len(primary_data['matched_patterns']))
        
        # Get secondary intents
        secondary_intents = []
        for intent, data in sorted_intents[1:4]:  # Top 3 secondary
            if data['score'] > 0:
                sec_confidence = self._calculate_confidence(data['score'], len(data['matched_patterns']))
                if sec_confidence > self.confidence_thresholds['low']:
                    secondary_intents.append((intent, sec_confidence))
        
        return IntentResult(
            intent=primary_intent,
            confidence=confidence,
            secondary_intents=secondary_intents,
            matched_patterns=primary_data['matched_patterns'],
            context_clues=self._extract_context_clues(processed, primary_intent)
        )
    
    def _score_intents(self, processed_text: ProcessedText, context: Dict = None) -> Dict[str, Dict]:
        """Score all intents against processed text"""
        scores = {}
        text_lower = processed_text.cleaned.lower()
        tokens = processed_text.normalized_tokens
        
        for intent, patterns in self.intent_patterns.items():
            score_data = {
                'score': 0.0,
                'matched_patterns': [],
                'keyword_matches': [],
                'pattern_matches': []
            }
            
            # Keyword matching
            for keyword in patterns['keywords']:
                if keyword.lower() in text_lower:
                    score_data['score'] += 1.0
                    score_data['keyword_matches'].append(keyword)
            
            # Pattern matching
            for pattern in patterns['patterns']:
                if re.search(pattern, text_lower):
                    score_data['score'] += 1.5  # Patterns weighted higher
                    score_data['pattern_matches'].append(pattern)
                    score_data['matched_patterns'].append(pattern)
            
            # Apply intent weight
            weight = patterns.get('weight', 1.0)
            score_data['score'] *= weight
            
            # Context boost
            if context:
                context_boost = self._calculate_context_boost(intent, context)
                score_data['score'] += context_boost
            
            # Token frequency boost
            token_boost = self._calculate_token_frequency_boost(intent, tokens)
            score_data['score'] += token_boost
            
            scores[intent] = score_data
        
        return scores
    
    def _calculate_confidence(self, score: float, pattern_matches: int) -> float:
        """Calculate confidence based on score and pattern matches"""
        # Base confidence from score
        base_confidence = min(score / 3.0, 1.0)  # Normalize to 0-1
        
        # Boost for pattern matches
        pattern_boost = min(pattern_matches * 0.1, 0.3)
        
        # Final confidence
        confidence = min(base_confidence + pattern_boost, 1.0)
        
        return round(confidence, 3)
    
    def _calculate_context_boost(self, intent: str, context: Dict) -> float:
        """Calculate context-based score boost"""
        boost = 0.0
        
        # Previous intent context
        if 'previous_intent' in context:
            prev_intent = context['previous_intent']
            
            # Intent continuation patterns
            continuation_patterns = {
                'disease_identification': ['pest_control', 'fertilizer_advice'],
                'pest_control': ['disease_identification', 'yield_optimization'],
                'planting_guidance': ['fertilizer_advice', 'harvest_timing'],
                'fertilizer_advice': ['yield_optimization', 'planting_guidance']
            }
            
            if intent in continuation_patterns.get(prev_intent, []):
                boost += 0.5
        
        # Crop context
        if 'mentioned_crops' in context and context['mentioned_crops']:
            if intent in ['disease_identification', 'pest_control', 'fertilizer_advice', 'planting_guidance']:
                boost += 0.3
        
        # Seasonal context
        if 'season' in context:
            seasonal_boosts = {
                'planting': ['planting_guidance', 'fertilizer_advice'],
                'growing': ['disease_identification', 'pest_control'],
                'harvest': ['harvest_timing', 'yield_optimization']
            }
            
            season = context['season']
            if intent in seasonal_boosts.get(season, []):
                boost += 0.2
        
        return boost
    
    def _calculate_token_frequency_boost(self, intent: str, tokens: List[str]) -> float:
        """Calculate boost based on token frequency for intent"""
        boost = 0.0
        
        # Count relevant tokens for each intent
        intent_tokens = {
            'disease_identification': ['disease', 'sick', 'problem', 'symptom', 'leaf', 'spot'],
            'pest_control': ['pest', 'insect', 'bug', 'damage', 'eat', 'hole'],
            'fertilizer_advice': ['fertilizer', 'nutrient', 'soil', 'feed', 'growth'],
            'planting_guidance': ['plant', 'seed', 'grow', 'cultivat', 'procedure'],
            'harvest_timing': ['harvest', 'ready', 'mature', 'pick', 'collect']
        }
        
        relevant_tokens = intent_tokens.get(intent, [])
        if relevant_tokens:
            matches = sum(1 for token in tokens if any(rt in token for rt in relevant_tokens))
            boost = matches * 0.1
        
        return min(boost, 0.5)  # Cap boost
    
    def _extract_context_clues(self, processed_text: ProcessedText, intent: str) -> Dict[str, List[str]]:
        """Extract context clues from text for the identified intent"""
        context_clues = defaultdict(list)
        tokens = processed_text.normalized_tokens
        
        # Crop mentions
        crop_indicators = ['maize', 'cassava', 'tomato', 'bean', 'rice', 'cocoa', 'coffee', 'plantain']
        for token in tokens:
            for crop in crop_indicators:
                if crop in token:
                    context_clues['crops'].append(crop)
        
        # Problem descriptions
        if intent in ['disease_identification', 'pest_control']:
            problem_words = ['yellow', 'brown', 'spot', 'hole', 'wilt', 'die', 'damage']
            for token in tokens:
                for problem in problem_words:
                    if problem in token:
                        context_clues['problems'].append(problem)
        
        # Time references
        time_words = ['when', 'time', 'season', 'month', 'week', 'day']
        for token in tokens:
            for time_word in time_words:
                if time_word in token:
                    context_clues['timing'].append(time_word)
        
        # Quantity references
        quantity_pattern = r'\d+\.?\d*'
        quantities = re.findall(quantity_pattern, processed_text.cleaned)
        if quantities:
            context_clues['quantities'] = quantities
            # Convert context_clues to regular dict
        return dict(context_clues)
    
    def get_intent_confidence_level(self, confidence: float) -> str:
        """Get confidence level description"""
        if confidence >= self.confidence_thresholds['high']:
            return 'high'
        elif confidence >= self.confidence_thresholds['medium']:
            return 'medium'
        elif confidence >= self.confidence_thresholds['low']:
            return 'low'
        else:
            return 'very_low'
    
    def analyze_intent_patterns(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze intent patterns across multiple texts"""
        intent_counts = Counter()
        confidence_levels = defaultdict(list)
        
        for text in texts:
            result = self.classify_intent(text)
            intent_counts[result.intent] += 1
            confidence_levels[result.intent].append(result.confidence)
        
        # Calculate average confidence per intent
        avg_confidence = {}
        for intent, confidences in confidence_levels.items():
            avg_confidence[intent] = sum(confidences) / len(confidences)
        
        return {
            'intent_distribution': dict(intent_counts),
            'average_confidence': avg_confidence,
            'total_texts_analyzed': len(texts),
            'most_common_intent': intent_counts.most_common(1)[0] if intent_counts else None
        }