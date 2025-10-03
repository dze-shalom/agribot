import re
import random
from collections import defaultdict
from typing import Dict, List, Tuple, Any

class EnhancedIntentClassifier:
    """Advanced rule-based intent classifier without NLTK dependency"""
    
    def __init__(self):
        # Enhanced intent patterns with more sophisticated matching
        self.intent_patterns = {
            'greeting': {
                'keywords': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings', 'howdy'],
                'patterns': [r'\b(hello|hi|hey)\b', r'good\s+(morning|afternoon|evening)', r'\bgreetings?\b']
            },
            'thanks': {
                'keywords': ['thank you', 'thanks', 'thank u', 'thx', 'appreciate', 'grateful', 'much obliged'],
                'patterns': [r'\bthank\s*you\b', r'\bthanks?\b', r'\bappreciate\b', r'\bgrateful\b']
            },
            'praise': {
                'keywords': ['good job', 'well done', 'excellent', 'great', 'awesome', 'nice', 'perfect', 'helpful', 'amazing', 'wonderful', 'fantastic'],
                'patterns': [r'\bgood\s+job\b', r'\bwell\s+done\b', r'\bexcellent\b', r'\bgreat\b', r'\bawesome\b', r'\bamazing\b']
            },
            'acknowledgment': {
                'keywords': ['okay', 'ok', 'alright', 'yes', 'yeah', 'sure', 'i see', 'understood', 'got it', 'right'],
                'patterns': [r'\bokay?\b', r'\balright\b', r'\byes\b', r'\byeah\b', r'\bsure\b', r'\bgot\s+it\b']
            },
            'clarification': {
                'keywords': ['what do you mean', 'explain', 'clarify', 'i dont understand', 'what about', 'tell me more', 'can you elaborate'],
                'patterns': [r'what\s+do\s+you\s+mean', r'\bexplain\b', r'\bclarify\b', r'dont?\s+understand', r'tell\s+me\s+more']
            },
            'weather': {
                'keywords': ['weather', 'temperature', 'rain', 'rainfall', 'climate', 'forecast', 'hot', 'cold', 'sunny', 'cloudy', 'humid', 'dry', 'wet'],
                'patterns': [r'\bweather\b', r'\btemperature\b', r'\brain\w*\b', r'\bclimate\b', r'\bforecast\b']
            },
            'disease': {
                'keywords': ['disease', 'sick', 'dying', 'yellow', 'spots', 'blight', 'virus', 'fungus', 'infection', 'rot', 'wilt', 'brown', 'problem', 'issue'],
                'patterns': [r'\bdisease\b', r'\bsick\b', r'\bdying\b', r'\byellow\w*\b', r'\bspots?\b', r'\bblight\b', r'\bwilt\w*\b']
            },
            'fertilizer': {
                'keywords': ['fertilizer', 'fertiliser', 'manure', 'compost', 'npk', 'nutrients', 'feed', 'nutrition', 'organic', 'urea'],
                'patterns': [r'\bfertiliz\w*\b', r'\bmanure\b', r'\bcompost\b', r'\bnpk\b', r'\bnutrients?\b', r'\burea\b']
            },
            'planting': {
                'keywords': ['plant', 'planting', 'sow', 'sowing', 'seed', 'grow', 'cultivation', 'cultivate', 'procedures', 'how to plant', 'when to plant'],
                'patterns': [r'\bplant\w*\b', r'\bsow\w*\b', r'\bgrow\w*\b', r'\bcultivat\w*\b', r'how\s+to\s+\w*plant\b', r'procedures?\b']
            },
            'pest': {
                'keywords': ['pest', 'insects', 'caterpillar', 'worm', 'aphid', 'control', 'bug', 'termite', 'locust', 'damage', 'armyworm'],
                'patterns': [r'\bpests?\b', r'\binsects?\b', r'\bcaterpillars?\b', r'\bworms?\b', r'\baphids?\b', r'\bbugs?\b', r'\barmyworms?\b']
            },
            'harvest': {
                'keywords': ['harvest', 'harvesting', 'when to harvest', 'maturity', 'ready', 'picking', 'collection', 'ripe'],
                'patterns': [r'\bharvest\w*\b', r'\bmaturity\b', r'\bready\b', r'\bpicking\b', r'\bripe\b', r'when\s+to\s+harvest']
            },
            'yield': {
                'keywords': ['yield', 'production', 'maximize', 'increase', 'improve', 'boost', 'more', 'better', 'higher', 'productivity'],
                'patterns': [r'\byield\b', r'\bproduction\b', r'\bmaximize\b', r'\bincrease\b', r'\bimprove\b', r'\bboost\b']
            },
            'market': {
                'keywords': ['price', 'market', 'sell', 'cost', 'profit', 'money', 'buy', 'trade', 'business', 'income'],
                'patterns': [r'\bprice\b', r'\bmarket\b', r'\bsell\w*\b', r'\bcost\b', r'\bprofit\b', r'\bmoney\b', r'\bbusiness\b']
            }
        }
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Handle common typos and variations
        corrections = {
            'tomatoe': 'tomato',
            'tomatos': 'tomatoes',
            'casava': 'cassava',
            'maze': 'maize',
            'coffe': 'coffee',
            'pineaple': 'pineapple',
            'procedues': 'procedures',
            'tommatoes': 'tomatoes',
            'tommatoe': 'tomato'
        }
        
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def extract_sentiment(self, text: str) -> Dict[str, float]:
        """Simple sentiment analysis without NLTK"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'helpful', 'useful', 'thank', 'appreciate']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'useless', 'wrong', 'problem', 'issue', 'dying', 'sick']
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if any(pos in word for pos in positive_words))
        negative_count = sum(1 for word in words if any(neg in word for neg in negative_words))
        
        total_words = len(words)
        if total_words == 0:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}
        
        positive_score = positive_count / total_words
        negative_score = negative_count / total_words
        neutral_score = max(0.0, 1.0 - positive_score - negative_score)
        compound = positive_score - negative_score
        
        return {
            'positive': positive_score,
            'negative': negative_score,
            'neutral': neutral_score,
            'compound': compound
        }
    
    def classify_intent(self, text: str, context: Any = None) -> Dict[str, Any]:
        """Enhanced intent classification with context awareness"""
        text = self.preprocess_text(text)
        sentiment = self.extract_sentiment(text)
        
        # Score each intent
        intent_scores = defaultdict(float)
        
        for intent, patterns in self.intent_patterns.items():
            # Keyword matching
            for keyword in patterns['keywords']:
                if keyword in text:
                    intent_scores[intent] += 1.0
            
            # Pattern matching
            for pattern in patterns['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    intent_scores[intent] += 1.5
        
        # Handle very short responses
        if len(text.split()) <= 2:
            if text in ['ok', 'okay', 'yes', 'yeah', 'sure']:
                intent_scores['acknowledgment'] = 3.0
            elif text in ['thanks', 'thank you']:
                intent_scores['thanks'] = 3.0
        
        # Get best intent
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[best_intent] / 3.0, 1.0)
        else:
            best_intent = 'general'
            confidence = 0.1
        
        return {
            'intent': best_intent,
            'confidence': confidence,
            'sentiment': sentiment,
            'all_scores': dict(intent_scores)
        }

class EnhancedEntityExtractor:
    """Advanced entity extraction with fuzzy matching"""
    
    def __init__(self):
        # Comprehensive crop database with variations
        self.crop_variations = {
            'maize': ['maize', 'corn', 'maze', 'sweet corn'],
            'tomatoes': ['tomato', 'tomatos', 'tomatoe', 'tomatoes'],
            'pepper': ['pepper', 'peppers', 'chili', 'chilies', 'bell pepper', 'hot pepper'],
            'beans': ['bean', 'beans', 'legume', 'legumes', 'black beans', 'kidney beans'],
            'cassava': ['cassava', 'casava', 'manioc', 'yuca', 'tapioca'],
            'plantain': ['plantain', 'plantains', 'cooking banana'],
            'rice': ['rice', 'paddy', 'paddy rice'],
            'yam': ['yam', 'yams'],
            'cocoa': ['cocoa', 'cacao', 'chocolate tree'],
            'coffee': ['coffee', 'coffe', 'arabica', 'robusta'],
            'oil_palm': ['oil palm', 'palm oil', 'palm tree', 'elaeis'],
            'pineapple': ['pineapple', 'pineaple', 'ananas'],
            'banana': ['banana', 'bananas'],
            'sweet_potato': ['sweet potato', 'sweet potatoes', 'yam potato'],
            'irish_potato': ['irish potato', 'potato', 'potatoes', 'white potato'],
            'groundnuts': ['groundnut', 'groundnuts', 'peanut', 'peanuts'],
            'cotton': ['cotton'],
            'millet': ['millet', 'pearl millet'],
            'sorghum': ['sorghum', 'guinea corn'],
            'okra': ['okra', 'lady finger'],
            'onion': ['onion', 'onions'],
            'garlic': ['garlic'],
            'cabbage': ['cabbage'],
            'carrot': ['carrot', 'carrots'],
            'cucumber': ['cucumber', 'cucumbers'],
            'eggplant': ['eggplant', 'aubergine', 'garden egg'],
            'spinach': ['spinach']
        }
        
        # Cameroon regions with variations
        self.regions = {
            'centre': ['centre', 'central', 'center', 'yaounde', 'yaoundé'],
            'littoral': ['littoral', 'douala', 'coastal'],
            'west': ['west', 'western', 'bafoussam'],
            'northwest': ['northwest', 'north west', 'bamenda', 'nw'],
            'southwest': ['southwest', 'south west', 'buea', 'sw'],
            'east': ['east', 'eastern', 'bertoua'],
            'north': ['north', 'northern', 'garoua'],
            'far_north': ['far north', 'extreme north', 'maroua', 'far-north'],
            'adamawa': ['adamawa', 'adamaoua', 'ngaoundere', 'ngaoundéré'],
            'south': ['south', 'southern', 'ebolowa']
        }
        
        # Disease patterns
        self.diseases = [
            'blight', 'mosaic', 'streak', 'rot', 'wilt', 'spot', 'virus',
            'fungus', 'mildew', 'rust', 'canker', 'bacterial', 'yellowing'
        ]
        
        # Pest patterns
        self.pests = [
            'armyworm', 'fall armyworm', 'aphid', 'whitefly', 'caterpillar',
            'termite', 'locust', 'weevil', 'bollworm', 'stem borer', 'cutworm'
        ]
        
        # Time patterns
        self.time_patterns = [
            r'(\d+)\s*(day|week|month|year)s?',
            r'(today|tomorrow|yesterday)',
            r'(this|next|last)\s+(week|month|year|season)',
            r'(rainy|dry)\s+season',
            r'(morning|afternoon|evening|night)',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)'
        ]
        
        # Quantity patterns
        self.quantity_patterns = [
            r'(\d+(?:\.\d+)?)\s*(kg|kilogram|gram|g|ton|tonne|bag|sack|hectare|ha|liter|litre|l)',
            r'(\d+(?:\.\d+)?)\s*(percent|%)',
            r'(\d+)\s*(times?|x)'
        ]
    
    def fuzzy_match_crop(self, text: str) -> List[str]:
        """Fuzzy matching for crop names"""
        found_crops = []
        text_lower = text.lower()
        
        for canonical_crop, variations in self.crop_variations.items():
            for variation in variations:
                if variation in text_lower:
                    found_crops.append(canonical_crop)
                    break
        
        return list(set(found_crops))
    
    def extract_regions(self, text: str) -> List[str]:
        """Extract regions with fuzzy matching"""
        found_regions = []
        text_lower = text.lower()
        
        for canonical_region, variations in self.regions.items():
            for variation in variations:
                if variation in text_lower:
                    found_regions.append(canonical_region)
                    break
        
        return list(set(found_regions))
    
    def extract_diseases(self, text: str) -> List[str]:
        """Extract disease mentions"""
        found_diseases = []
        text_lower = text.lower()
        
        for disease in self.diseases:
            if disease in text_lower:
                found_diseases.append(disease)
        
        return found_diseases
    
    def extract_pests(self, text: str) -> List[str]:
        """Extract pest mentions"""
        found_pests = []
        text_lower = text.lower()
        
        for pest in self.pests:
            if pest in text_lower:
                found_pests.append(pest)
        
        return found_pests
    
    def extract_quantities(self, text: str) -> List[str]:
        """Extract quantities and measurements"""
        quantities = []
        
        for pattern in self.quantity_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    quantities.append(f"{match[0]} {match[1]}")
                else:
                    quantities.append(match)
        
        return quantities
    
    def extract_time_references(self, text: str) -> List[str]:
        """Extract time-related entities"""
        time_refs = []
        
        for pattern in self.time_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    time_refs.append(' '.join(match))
                else:
                    time_refs.append(match)
        
        return time_refs
    
    def extract_all_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract all entities from text"""
        return {
            'crops': self.fuzzy_match_crop(text),
            'regions': self.extract_regions(text),
            'diseases': self.extract_diseases(text),
            'pests': self.extract_pests(text),
            'quantities': self.extract_quantities(text),
            'time_references': self.extract_time_references(text)
        }

class ConversationalResponseGenerator:
    """Generate natural, contextual responses"""
    
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base
        self.intent_classifier = EnhancedIntentClassifier()
        self.entity_extractor = EnhancedEntityExtractor()
    
    def generate_response(self, user_input: str, context: Any) -> Dict[str, Any]:
        """Generate comprehensive response with NLP analysis"""
        
        # Analyze input
        intent_result = self.intent_classifier.classify_intent(user_input, context)
        entities = self.entity_extractor.extract_all_entities(user_input)
        
        # Generate response based on intent and entities
        response_data = self._generate_intent_based_response(
            user_input, intent_result, entities, context
        )
        
        return {
            'response': response_data['response'],
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'sentiment': intent_result['sentiment'],
            'entities': entities,
            'response_type': response_data.get('response_type', 'informational'),
            'follow_up_suggestions': response_data.get('follow_up_suggestions', [])
        }
    
    def _generate_intent_based_response(self, user_input: str, intent_result: Dict, entities: Dict, context: Any) -> Dict[str, Any]:
        """Generate response based on classified intent"""
        
        intent = intent_result['intent']
        confidence = intent_result['confidence']
        
        # Handle low confidence cases
        if confidence < 0.3:
            return self._generate_clarification_response(user_input, entities, context)
        
        # Route to appropriate response generator
        if intent == 'greeting':
            return self._generate_greeting_response(context)
        elif intent == 'thanks':
            return self._generate_thanks_response(context)
        elif intent == 'praise':
            return self._generate_praise_response(user_input, context)
        elif intent == 'acknowledgment':
            return self._generate_acknowledgment_response(context)
        elif intent == 'planting':
            return self._generate_planting_response(entities, context)
        elif intent == 'disease':
            return self._generate_disease_response(entities, context, user_input)
        elif intent == 'fertilizer':
            return self._generate_fertilizer_response(entities, context)
        elif intent == 'weather':
            return self._generate_weather_response(entities, context)
        else:
            return self._generate_general_response(user_input, entities, context)
    
    def _generate_greeting_response(self, context: Any) -> Dict[str, Any]:
        """Generate natural greeting response"""
        name = getattr(context, 'user_name', 'Friend')
        greetings = [
            f"Hello {name}! I'm AgriBot, your AI farming assistant. I'm here to help with any agricultural questions you have. What's on your mind today?",
            f"Hi there {name}! Great to meet you. I'm here to help with all your farming needs. What would you like to know?",
            f"Welcome {name}! I'm excited to help you with your agricultural journey. What farming topic interests you today?"
        ]
        
        return {
            'response': random.choice(greetings),
            'response_type': 'greeting',
            'follow_up_suggestions': [
                "Tell me about planting maize",
                "What diseases affect tomatoes?",
                "Best fertilizer for vegetables",
                "Weather forecast for farming"
            ]
        }
    
    def _generate_thanks_response(self, context: Any) -> Dict[str, Any]:
        """Generate thanks response"""
        name = getattr(context, 'user_name', 'Friend')
        responses = [
            f"You're very welcome, {name}! I'm here to help whenever you need farming advice.",
            "Happy to help! Feel free to ask if you have more questions about your crops.",
            "No problem at all! I'm always here for your agricultural questions."
        ]
        
        return {
            'response': random.choice(responses),
            'response_type': 'acknowledgment'
        }
    
    def _generate_praise_response(self, user_input: str, context: Any) -> Dict[str, Any]:
        """Generate response to praise"""
        name = getattr(context, 'user_name', 'Friend')
        responses = [
            f"Thank you, {name}! I'm glad I could provide useful information. What else would you like to know?",
            "I appreciate that! I'm here to support your farming success. Any other questions?",
            "Thanks! It makes me happy when I can provide helpful farming advice. What's your next question?"
        ]
        
        return {
            'response': random.choice(responses),
            'response_type': 'acknowledgment'
        }
    
    def _generate_acknowledgment_response(self, context: Any) -> Dict[str, Any]:
        """Handle simple acknowledgments"""
        responses = [
            "What else can I help you with today?",
            "Any other farming questions I can answer for you?",
            "Is there another topic you'd like to discuss about agriculture?"
        ]
        
        return {
            'response': random.choice(responses),
            'response_type': 'continuation_prompt'
        }
    
    def _generate_planting_response(self, entities: Dict, context: Any) -> Dict[str, Any]:
        """Generate detailed planting guidance"""
        crops = entities.get('crops', [])
        
        if not crops:
            return {
                'response': "I'd love to help you with planting! Which crop are you interested in growing? I can provide detailed guidance for maize, tomatoes, pepper, beans, cassava, and many others grown in Cameroon.",
                'response_type': 'clarification_request',
                'follow_up_suggestions': [
                    "Tell me about planting maize",
                    "How to plant tomatoes?", 
                    "Pepper planting guide",
                    "When to plant beans?"
                ]
            }
        
        crop = crops[0]
        
        # Get planting information
        planting_info = self.knowledge_base.get_planting_guide(crop)
        
        intros = [
            f"Let me guide you through growing {crop}!",
            f"Growing {crop} is definitely doable - here's how:",
            f"I'd be happy to help you with {crop} cultivation."
        ]
        
        response = f"{random.choice(intros)}\n\n"
        
        # Add specific guidance
        if 'planting_guide' in planting_info:
            guide = planting_info['planting_guide']
            
            if 'land_preparation' in guide:
                response += "**Land Preparation:**\n"
                for step in guide['land_preparation'][:3]:
                    response += f"• {step}\n"
                response += "\n"
            
            if 'planting' in guide:
                response += "**Planting Process:**\n"
                for step in guide['planting'][:3]:
                    response += f"• {step}\n"
                response += "\n"
        
        response += f"This should get you started with {crop}! Would you like more details about fertilizing, pest control, or caring for the plants after planting?"
        
        return {
            'response': response,
            'response_type': 'detailed_guidance',
            'follow_up_suggestions': [
                f"Fertilizer for {crop}",
                f"Common diseases in {crop}",
                f"When to harvest {crop}",
                "Soil preparation tips"
            ]
        }
    
    def _generate_disease_response(self, entities: Dict, context: Any, user_input: str) -> Dict[str, Any]:
        """Generate disease diagnosis and treatment advice"""
        crops = entities.get('crops', [])
        
        if not crops and hasattr(context, 'mentioned_crops') and context.mentioned_crops:
            crops = context.mentioned_crops[-1:]
        
        if not crops:
            return {
                'response': "I'd be happy to help identify the plant disease. Which crop is having problems? Also, can you describe what you're seeing - like leaf color changes, spots, wilting, or other symptoms?",
                'response_type': 'diagnostic_inquiry',
                'follow_up_suggestions': [
                    "My maize has yellow leaves",
                    "Tomato plants are wilting", 
                    "Brown spots on pepper leaves",
                    "Cassava leaves look diseased"
                ]
            }
        
        crop = crops[0]
        
        response = f"Let me help diagnose the issue with your {crop}.\n\n"
        
        # Get disease information
        disease_info = self.knowledge_base.get_disease_info(crop)
        
        if 'available_diseases' in disease_info:
            response += f"Common diseases affecting {crop} include:\n\n"
            diseases_list = disease_info['available_diseases'][:3]
            
            for i, disease in enumerate(diseases_list, 1):
                response += f"{i}. {disease.replace('_', ' ').title()}\n"
            
            response += f"\nTo give you more specific help, could you describe what you're seeing? Look for:\n"
            response += "• Changes in leaf color (yellow, brown, spotted)\n"
            response += "• Plant behavior (wilting, stunted growth)\n"
            response += "• Any visible damage or unusual marks"
        
        return {
            'response': response,
            'response_type': 'diagnostic_guidance',
            'follow_up_suggestions': [
                f"Prevention tips for {crop}",
                f"Organic treatments for {crop}",
                "How to apply fungicide",
                "Signs of plant recovery"
            ]
        }
    
    def _generate_fertilizer_response(self, entities: Dict, context: Any) -> Dict[str, Any]:
        """Generate fertilizer recommendations"""
        crops = entities.get('crops', [])
        
        if not crops:
            return {
                'response': "I'd be happy to help with fertilizer recommendations! Which crop are you planning to fertilize?",
                'response_type': 'clarification_request'
            }
        
        crop = crops[0]
        fert_info = self.knowledge_base.get_fertilizer_recommendation(crop)
        
        response = f"Here are the fertilizer recommendations for {crop}:\n\n"
        
        if 'fertilizer_program' in fert_info:
            program = fert_info['fertilizer_program']
            
            if 'basal_fertilizer' in program:
                basal = program['basal_fertilizer']
                response += f"**At Planting:** Use {basal.get('npk', 'NPK')} fertilizer at {basal.get('rate', 'recommended rate')}\n\n"
            
            if 'top_dressing' in program:
                top = program['top_dressing']
                response += f"**Top Dressing:** Apply {top.get('fertilizer', 'Urea')} at {top.get('rate', 'recommended rate')} around {top.get('timing', '4-6 weeks after planting')}\n\n"
        
        response += "Remember to consider your soil type and crop variety when applying fertilizers. Would you like specific application instructions or information about organic alternatives?"
        
        return {
            'response': response,
            'response_type': 'detailed_guidance',
            'follow_up_suggestions': [
                f"Organic fertilizer for {crop}",
                "Soil testing advice",
                "Fertilizer application timing",
                "Signs of nutrient deficiency"
            ]
        }
    
    def _generate_weather_response(self, entities: Dict, context: Any) -> Dict[str, Any]:
        """Generate weather-related farming advice"""
        region = getattr(context, 'user_region', 'centre')
        
        response = f"I can help you understand how weather affects farming in {region} region. "
        response += "What specific weather information do you need? Current conditions, seasonal planning, or weather-related farming advice?"
        
        return {
            'response': response,
            'response_type': 'weather_inquiry',
            'follow_up_suggestions': [
                "Current weather conditions",
                "Best planting seasons",
                "Weather-related crop diseases",
                "Irrigation planning advice"
            ]
        }
    
    def _generate_general_response(self, user_input: str, entities: Dict, context: Any) -> Dict[str, Any]:
        """Generate general agricultural response"""
        crops = entities.get('crops', [])
        
        if crops:
            crop = crops[0]
            return {
                'response': f"I can help you with {crop} farming! What specifically would you like to know? I can provide information about planting, diseases, fertilizers, pest control, and harvesting.",
                'response_type': 'topic_introduction',
                'follow_up_suggestions': [
                    f"How to plant {crop}",
                    f"Common diseases in {crop}",
                    f"Fertilizer for {crop}",
                    f"When to harvest {crop}"
                ]
            }
        else:
            return {
                'response': "I'm here to help with your farming questions! I can assist with crops, diseases, fertilizers, planting procedures, weather advice, and more. What would you like to know about?",
                'response_type': 'general_help',
                'follow_up_suggestions': [
                    "Planting guide for common crops",
                    "Disease identification help",
                    "Fertilizer recommendations", 
                    "Weather and farming advice"
                ]
            }
    
    def _generate_clarification_response(self, user_input: str, entities: Dict, context: Any) -> Dict[str, Any]:
        """Generate response when intent is unclear"""
        return {
            'response': "I want to help you with your farming question, but I need a bit more clarity. Are you asking about planting, diseases, fertilizers, or something else? Feel free to be more specific about what you'd like to know.",
            'response_type': 'clarification_request',
            'follow_up_suggestions': [
                "How to plant [crop name]",
                "Disease problems in [crop name]",
                "Fertilizer for [crop name]",
                "Weather advice for farming"
            ]
        }