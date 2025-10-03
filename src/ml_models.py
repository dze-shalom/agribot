import re
from collections import defaultdict

class IntentClassifier:
    """Simple rule-based intent classifier for agricultural questions"""
    
    def __init__(self):
        self.intent_patterns = {
            'weather': [
                'weather', 'temperature', 'rain', 'rainfall', 'climate', 'forecast',
                'hot', 'cold', 'sunny', 'cloudy', 'humid', 'dry'
            ],
            'disease': [
                'disease', 'sick', 'dying', 'yellow', 'spots', 'blight', 'virus', 
                'fungus', 'infection', 'rot', 'wilt', 'brown', 'leaf'
            ],
            'fertilizer': [
                'fertilizer', 'fertiliser', 'manure', 'compost', 'npk', 'nutrients',
                'feed', 'nutrition', 'organic', 'urea'
            ],
            'planting': [
                'plant', 'planting', 'sow', 'sowing', 'seed', 'grow', 'cultivation',
                'how to plant', 'when to plant', 'spacing'
            ],
            'pest': [
                'pest', 'insects', 'caterpillar', 'worm', 'aphid', 'control',
                'bug', 'termite', 'locust', 'damage'
            ],
            'harvest': [
                'harvest', 'harvesting', 'when to harvest', 'maturity', 'ready',
                'picking', 'collection'
            ],
            'yield': [
                'yield', 'production', 'maximize', 'increase', 'improve', 'boost',
                'more', 'better', 'higher'
            ],
            'market': [
                'price', 'market', 'sell', 'cost', 'profit', 'money', 'buy',
                'trade', 'business'
            ],
            'care': [
                'care', 'maintain', 'calendar', 'schedule', 'when to', 'timing',
                'management', 'maintenance'
            ]
        }
    
    def classify(self, text):
        """Classify the intent of agricultural question"""
        text_lower = text.lower()
        intent_scores = defaultdict(int)
        
        # Score each intent based on keyword matches
        for intent, keywords in self.intent_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    intent_scores[intent] += 1
        
        # Get the highest scoring intent
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent] / len(text_lower.split())
            return {
                'intent': best_intent,
                'confidence': min(confidence * 2, 1.0),  # Scale confidence
                'all_scores': dict(intent_scores)
            }
        else:
            return {
                'intent': 'general',
                'confidence': 0.1,
                'all_scores': {}
            }

class EntityExtractor:
    """Extract agricultural entities from text"""
    
    def __init__(self):
        # Load crop names
        self.crops = [
            # Cereals
            'maize', 'corn', 'rice', 'millet', 'sorghum', 'wheat',
            # Root crops
            'cassava', 'yam', 'sweet potato', 'irish potato', 'plantain', 'cocoyam',
            # Legumes  
            'beans', 'groundnuts', 'peanuts', 'soybeans', 'cowpeas',
            # Cash crops
            'cocoa', 'coffee', 'cotton', 'oil palm', 'rubber', 'tea', 'sugar cane',
            # Vegetables
            'tomatoes', 'pepper', 'okra', 'onions', 'garlic', 'cabbage', 
            'lettuce', 'carrot', 'cucumber', 'eggplant', 'spinach',
            # Fruits
            'banana', 'pineapple', 'mango', 'avocado', 'orange', 'lemon', 'papaya'
        ]
        
        # Cameroon regions
        self.regions = [
            'centre', 'littoral', 'west', 'northwest', 'southwest',
            'east', 'north', 'far north', 'adamawa', 'south'
        ]
        
        # Common diseases
        self.diseases = [
            'blight', 'mosaic', 'streak', 'rot', 'wilt', 'spot', 'virus',
            'fungus', 'mildew', 'rust', 'canker'
        ]
        
        # Common pests
        self.pests = [
            'armyworm', 'fall armyworm', 'aphid', 'whitefly', 'caterpillar', 
            'termite', 'locust', 'weevil', 'bollworm'
        ]
    
    def extract(self, text):
        """Extract all entities from text"""
        text_lower = text.lower()
        
        entities = {
            'crops': [],
            'regions': [], 
            'diseases': [],
            'pests': [],
            'quantities': [],
            'time_periods': []
        }
        
        # Extract crops
        for crop in self.crops:
            if crop in text_lower:
                entities['crops'].append(crop)
        
        # Extract regions
        for region in self.regions:
            if region in text_lower:
                entities['regions'].append(region)
        
        # Extract diseases
        for disease in self.diseases:
            if disease in text_lower:
                entities['diseases'].append(disease)
        
        # Extract pests
        for pest in self.pests:
            if pest in text_lower:
                entities['pests'].append(pest)
        
        # Extract quantities (simple regex)
        quantity_pattern = r'(\d+(?:\.\d+)?)\s*(kg|tonnes?|hectares?|bags?|litres?)'
        quantities = re.findall(quantity_pattern, text_lower)
        entities['quantities'] = [f"{qty} {unit}" for qty, unit in quantities]
        
        # Extract time periods
        time_patterns = [
            'today', 'tomorrow', 'yesterday', 'this week', 'next week',
            'this month', 'next month', 'this year', 'rainy season', 'dry season'
        ]
        for time_period in time_patterns:
            if time_period in text_lower:
                entities['time_periods'].append(time_period)
        
        return entities

class ResponseGenerator:
    """Generate responses based on intent and entities"""
    
    def __init__(self, agribot_engine):
        self.agribot_engine = agribot_engine
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
    
    def generate_response(self, question, user_region='centre', user_role='farmer'):
        """Generate comprehensive response to agricultural question"""
        
        # Classify intent and extract entities
        intent_result = self.intent_classifier.classify(question)
        entities = self.entity_extractor.extract(question)
        
        # Add user context
        context = {
            'region': user_region,
            'role': user_role,
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'entities': entities
        }
        
        # Generate response using AgriBot engine
        response = self.agribot_engine.process_question(question, user_region)
        
        # Add metadata
        full_response = {
            'question': question,
            'answer': response,
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'entities_found': entities,
            'context': context,
            'suggestions': self.generate_suggestions(intent_result['intent'], entities)
        }
        
        return full_response
    
    def generate_suggestions(self, intent, entities):
        """Generate follow-up question suggestions"""
        suggestions = []
        
        crop = entities['crops'][0] if entities['crops'] else 'maize'
        
        if intent == 'disease':
            suggestions = [
                f"How do I prevent diseases in {crop}?",
                f"What are symptoms of blight in {crop}?",
                f"Natural treatments for {crop} diseases?"
            ]
        elif intent == 'fertilizer':
            suggestions = [
                f"When to apply fertilizer to {crop}?",
                f"Organic fertilizer options for {crop}?",
                f"How much fertilizer per hectare for {crop}?"
            ]
        elif intent == 'planting':
            suggestions = [
                f"Best time to plant {crop}?",
                f"Spacing for {crop} planting?",
                f"Soil preparation for {crop}?"
            ]
        elif intent == 'yield':
            suggestions = [
                f"Best varieties of {crop} for high yield?",
                f"Water requirements for {crop}?",
                f"Common mistakes in {crop} farming?"
            ]
        else:
            suggestions = [
                f"Planting guide for {crop}",
                f"Common diseases in {crop}",
                f"Fertilizer for {crop}",
                "Weather forecast for farming"
            ]
        
        return suggestions[:3]  # Return top 3 suggestions

# Test the ML models
if __name__ == "__main__":
    from agribot_engine import AgriBotEngine
    
    # Initialize components
    engine = AgriBotEngine()
    response_generator = ResponseGenerator(engine)
    
    print("Testing ML Models for AgriBot")
    print("=" * 50)
    
    # Test questions
    test_questions = [
        "What diseases are affecting my maize plants with yellow spots?",
        "How much fertilizer should I use for cassava in centre region?", 
        "When is the best time to plant tomatoes?",
        "My coffee plants are dying, what should I do?",
        "How can I increase yield of beans in west region?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Testing Question: {question}")
        print("-" * 40)
        
        result = response_generator.generate_response(question, 'centre', 'farmer')
        
        print(f"Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
        print(f"Entities: {result['entities_found']}")
        print(f"Answer preview: {result['answer'][:150]}...")
        print(f"Suggestions: {result['suggestions']}")
        
        print("="*50)