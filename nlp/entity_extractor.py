"""
Entity Extractor
Location: agribot/nlp/entity_extractor.py

Extracts agricultural entities like crops, diseases, pests, regions,
quantities, and time references from user input text.
"""

import re
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
from nlp.text_processor import TextProcessor, ProcessedText

@dataclass
class EntityMatch:
    """Data structure for entity match results"""
    text: str
    entity_type: str
    start_pos: int
    end_pos: int
    confidence: float
    normalized_form: str
    context: str

@dataclass
class EntityExtractionResult:
    """Complete entity extraction results"""
    entities: Dict[str, List[EntityMatch]]
    entity_count: int
    extraction_confidence: float
    processing_notes: List[str]

class EntityExtractor:
    """Agricultural domain entity extraction"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        
        # Comprehensive crop database with variations
        self.crop_entities = {
            'cereals': {
                'maize': ['maize', 'corn', 'maze', 'sweet corn', 'field corn'],
                'rice': ['rice', 'paddy', 'paddy rice', 'upland rice'],
                'millet': ['millet', 'pearl millet', 'finger millet'],
                'sorghum': ['sorghum', 'guinea corn', 'durra'],
                'wheat': ['wheat', 'bread wheat', 'durum wheat']
            },
            'root_tubers': {
                'cassava': ['cassava', 'casava', 'manioc', 'yuca', 'tapioca root'],
                'yam': ['yam', 'yams', 'white yam', 'yellow yam'],
                'sweet_potato': ['sweet potato', 'sweet potatoes', 'orange potato'],
                'irish_potato': ['irish potato', 'potato', 'potatoes', 'white potato'],
                'plantain': ['plantain', 'plantains', 'cooking banana', 'plantin'],
                'cocoyam': ['cocoyam', 'taro', 'dasheen']
            },
            'legumes': {
                'beans': ['beans', 'bean', 'common beans', 'kidney beans', 'black beans'],
                'cowpeas': ['cowpeas', 'black eyed peas', 'southern peas'],
                'groundnuts': ['groundnuts', 'groundnut', 'peanuts', 'peanut'],
                'soybeans': ['soybeans', 'soybean', 'soya beans']
            },
            'cash_crops': {
                'cocoa': ['cocoa', 'cacao', 'chocolate tree'],
                'coffee': ['coffee', 'coffe', 'arabica', 'robusta', 'coffee beans'],
                'cotton': ['cotton', 'cotton plant'],
                'oil_palm': ['oil palm', 'palm oil', 'oil palm tree'],
                'rubber': ['rubber', 'rubber tree', 'hevea'],
                'tea': ['tea', 'tea plant', 'tea leaves']
            },
            'vegetables': {
                'tomatoes': ['tomato', 'tomatoes', 'tomatos', 'tomatoe'],
                'pepper': ['pepper', 'peppers', 'chili', 'bell pepper', 'hot pepper'],
                'okra': ['okra', 'lady finger', 'gumbo'],
                'onion': ['onion', 'onions', 'bulb onion'],
                'garlic': ['garlic', 'garlic bulb'],
                'cabbage': ['cabbage', 'head cabbage'],
                'lettuce': ['lettuce', 'head lettuce', 'leaf lettuce'],
                'carrot': ['carrot', 'carrots'],
                'cucumber': ['cucumber', 'cucumbers'],
                'eggplant': ['eggplant', 'aubergine', 'garden egg']
            },
            'fruits': {
                'banana': ['banana', 'bananas'],
                'pineapple': ['pineapple', 'pineaple', 'ananas'],
                'mango': ['mango', 'mangoes'],
                'avocado': ['avocado', 'avocados', 'pear fruit'],
                'orange': ['orange', 'oranges', 'sweet orange'],
                'lemon': ['lemon', 'lemons'],
                'papaya': ['papaya', 'pawpaw', 'papaw']
            }
        }
        
        # Flatten crop dictionary for easier lookup
        self.all_crops = {}
        for category, crops in self.crop_entities.items():
            for canonical_name, variations in crops.items():
                for variation in variations:
                    self.all_crops[variation.lower()] = {
                        'canonical': canonical_name,
                        'category': category
                    }
        
        # Cameroon regions with variations
        self.region_entities = {
            'centre': ['centre', 'central', 'center', 'yaounde', 'yaoundé'],
            'littoral': ['littoral', 'douala', 'coastal', 'coast'],
            'west': ['west', 'western', 'bafoussam'],
            'northwest': ['northwest', 'north west', 'bamenda', 'nw', 'north-west'],
            'southwest': ['southwest', 'south west', 'buea', 'sw', 'south-west'],
            'east': ['east', 'eastern', 'bertoua'],
            'north': ['north', 'northern', 'garoua'],
            'far_north': ['far north', 'extreme north', 'maroua', 'far-north'],
            'adamawa': ['adamawa', 'adamaoua', 'ngaoundere', 'ngaoundéré'],
            'south': ['south', 'southern', 'ebolowa']
        }
        
        # Disease entities
        self.disease_entities = {
            'viral': ['virus', 'mosaic', 'streak', 'yellowing', 'curl'],
            'fungal': ['blight', 'rust', 'spot', 'mold', 'mildew', 'wilt', 'rot'],
            'bacterial': ['bacterial', 'canker', 'soft rot', 'fire blight']
        }
        
        # Pest entities
        self.pest_entities = {
            'insects': ['aphid', 'whitefly', 'thrips', 'mite', 'scale', 'mealybug'],
            'caterpillars': ['armyworm', 'fall armyworm', 'bollworm', 'cutworm', 'stem borer'],
            'beetles': ['weevil', 'flea beetle', 'colorado beetle'],
            'general': ['pest', 'bug', 'insect', 'worm', 'caterpillar']
        }
        
        # Quantity patterns with units
        self.quantity_patterns = [
            r'(\d+(?:\.\d+)?)\s*(kg|kilogram|kilograms|gram|grams|g)\b',
            r'(\d+(?:\.\d+)?)\s*(ton|tons|tonne|tonnes|mt)\b',
            r'(\d+(?:\.\d+)?)\s*(bag|bags|sack|sacks)\b',
            r'(\d+(?:\.\d+)?)\s*(hectare|hectares|ha|acre|acres)\b',
            r'(\d+(?:\.\d+)?)\s*(liter|liters|litre|litres|l)\b',
            r'(\d+(?:\.\d+)?)\s*(percent|%)\b',
            r'(\d+(?:\.\d+)?)\s*(cm|centimeter|centimeters|meter|meters|m)\b',
            r'(\d+(?:\.\d+)?)\s*(day|days|week|weeks|month|months|year|years)\b'
        ]
        
        # Time patterns
        self.time_patterns = [
            r'\b(today|tomorrow|yesterday)\b',
            r'\b(morning|afternoon|evening|night)\b',
            r'\b(this|next|last)\s+(week|month|year|season)\b',
            r'\b(rainy|dry|planting|growing|harvest)\s+season\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(\d{1,2})\s+(day|week|month)s?\s+(ago|from now)\b',
            r'\bin\s+(\d+)\s+(day|week|month|year)s?\b'
        ]
    
    def extract_entities(self, text: str, context: Dict = None) -> EntityExtractionResult:
        """Extract all entities from text"""
        if not text or not text.strip():
            return EntityExtractionResult(
                entities={},
                entity_count=0,
                extraction_confidence=0.0,
                processing_notes=['Empty input']
            )
        
        # Process text
        processed = self.text_processor.process_text(text)
        
        # Initialize results
        entities = defaultdict(list)
        processing_notes = []
        
        # Extract different entity types
        crop_entities = self._extract_crops(text, processed)
        region_entities = self._extract_regions(text, processed)
        disease_entities = self._extract_diseases(text, processed)
        pest_entities = self._extract_pests(text, processed)
        quantity_entities = self._extract_quantities(text, processed)
        time_entities = self._extract_time_references(text, processed)
        
        # Combine all entities
        entities['crops'] = crop_entities
        entities['regions'] = region_entities
        entities['diseases'] = disease_entities
        entities['pests'] = pest_entities
        entities['quantities'] = quantity_entities
        entities['time_references'] = time_entities
        
        # Calculate metrics
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        confidence = self._calculate_extraction_confidence(entities, processed)
        
        # Add processing notes
        if total_entities == 0:
            processing_notes.append('No entities detected')
        else:
            processing_notes.append(f'Extracted {total_entities} entities')
        
        if processed.language != 'english':
            processing_notes.append(f'Text detected as {processed.language}')
        
        return EntityExtractionResult(
            entities=dict(entities),
            entity_count=total_entities,
            extraction_confidence=confidence,
            processing_notes=processing_notes
        )
    
    def _extract_crops(self, original_text: str, processed: ProcessedText) -> List[EntityMatch]:
        """Extract crop mentions"""
        matches = []
        text_lower = original_text.lower()
        
        # Multi-word crop matching first
        multi_word_crops = [crop for crop in self.all_crops.keys() if len(crop.split()) > 1]
        multi_word_crops.sort(key=len, reverse=True)  # Longest first
        
        for crop_variation in multi_word_crops:
            pattern = r'\b' + re.escape(crop_variation) + r'\b'
            for match in re.finditer(pattern, text_lower):
                crop_data = self.all_crops[crop_variation]
                
                entity_match = EntityMatch(
                    text=match.group(),
                    entity_type='crop',
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.9,  # High confidence for exact match
                    normalized_form=crop_data['canonical'],
                    context=self._extract_context(original_text, match.start(), match.end())
                )
                matches.append(entity_match)
        
        # Single word crops (avoid overlaps with multi-word matches)
        used_positions = set()
        for match in matches:
            used_positions.update(range(match.start_pos, match.end_pos))
        
        single_word_crops = [crop for crop in self.all_crops.keys() if len(crop.split()) == 1]
        
        for crop_variation in single_word_crops:
            pattern = r'\b' + re.escape(crop_variation) + r'\b'
            for match in re.finditer(pattern, text_lower):
                # Check for overlap
                if any(pos in used_positions for pos in range(match.start(), match.end())):
                    continue
                
                crop_data = self.all_crops[crop_variation]
                
                entity_match = EntityMatch(
                    text=match.group(),
                    entity_type='crop',
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.8,
                    normalized_form=crop_data['canonical'],
                    context=self._extract_context(original_text, match.start(), match.end())
                )
                matches.append(entity_match)
        
        return matches
    
    def _extract_regions(self, original_text: str, processed: ProcessedText) -> List[EntityMatch]:
        """Extract region mentions"""
        matches = []
        text_lower = original_text.lower()
        
        for canonical_region, variations in self.region_entities.items():
            for variation in variations:
                pattern = r'\b' + re.escape(variation) + r'\b'
                for match in re.finditer(pattern, text_lower):
                    entity_match = EntityMatch(
                        text=match.group(),
                        entity_type='region',
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.9,
                        normalized_form=canonical_region,
                        context=self._extract_context(original_text, match.start(), match.end())
                    )
                    matches.append(entity_match)
        
        return matches
    
    def _extract_diseases(self, original_text: str, processed: ProcessedText) -> List[EntityMatch]:
        """Extract disease mentions"""
        matches = []
        text_lower = original_text.lower()
        
        for disease_type, diseases in self.disease_entities.items():
            for disease in diseases:
                pattern = r'\b' + re.escape(disease) + r'\w*\b'
                for match in re.finditer(pattern, text_lower):
                    # Calculate confidence based on context
                    confidence = 0.7
                    context = self._extract_context(original_text, match.start(), match.end())
                    
                    # Boost confidence if disease symptoms are mentioned nearby
                    symptom_words = ['yellow', 'brown', 'spot', 'wilt', 'rot', 'die']
                    if any(symptom in context.lower() for symptom in symptom_words):
                        confidence = 0.9
                    
                    entity_match = EntityMatch(
                        text=match.group(),
                        entity_type='disease',
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=confidence,
                        normalized_form=disease,
                        context=context
                    )
                    matches.append(entity_match)
        
        return matches
    
    def _extract_pests(self, original_text: str, processed: ProcessedText) -> List[EntityMatch]:
        """Extract pest mentions"""
        matches = []
        text_lower = original_text.lower()
        
        for pest_type, pests in self.pest_entities.items():
            for pest in pests:
                pattern = r'\b' + re.escape(pest) + r's?\b'
                for match in re.finditer(pattern, text_lower):
                    # Calculate confidence based on context
                    confidence = 0.7
                    context = self._extract_context(original_text, match.start(), match.end())
                    
                    # Boost confidence if damage words are mentioned nearby
                    damage_words = ['damage', 'eat', 'hole', 'attack', 'destroy']
                    if any(damage_word in context.lower() for damage_word in damage_words):
                        confidence = 0.9
                    
                    entity_match = EntityMatch(
                        text=match.group(),
                        entity_type='pest',
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=confidence,
                        normalized_form=pest,
                        context=context
                    )
                    matches.append(entity_match)
        
        return matches
    
    def _extract_quantities(self, original_text: str, processed: ProcessedText) -> List[EntityMatch]:
        """Extract quantity mentions"""
        matches = []
        text_lower = original_text.lower()
        
        for pattern in self.quantity_patterns:
            for match in re.finditer(pattern, text_lower):
                value, unit = match.groups()
                
                # Normalize unit
                normalized_unit = self._normalize_unit(unit)
                
                entity_match = EntityMatch(
                    text=match.group(),
                    entity_type='quantity',
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95,  # High confidence for numeric patterns
                    normalized_form=f"{value} {normalized_unit}",
                    context=self._extract_context(original_text, match.start(), match.end())
                )
                matches.append(entity_match)
        
        return matches
    
    def _extract_time_references(self, original_text: str, processed: ProcessedText) -> List[EntityMatch]:
        """Extract time references"""
        matches = []
        text_lower = original_text.lower()
        
        for pattern in self.time_patterns:
            for match in re.finditer(pattern, text_lower):
                entity_match = EntityMatch(
                    text=match.group(),
                    entity_type='time_reference',
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.8,
                    normalized_form=self._normalize_time_reference(match.group()),
                    context=self._extract_context(original_text, match.start(), match.end())
                )
                matches.append(entity_match)
        
        return matches
    
    def _extract_context(self, text: str, start_pos: int, end_pos: int, 
                        context_window: int = 30) -> str:
        """Extract context around entity match"""
        context_start = max(0, start_pos - context_window)
        context_end = min(len(text), end_pos + context_window)
        
        return text[context_start:context_end].strip()
    
    def _normalize_unit(self, unit: str) -> str:
        """Normalize measurement units"""
        unit_mappings = {
            'kg': 'kilograms', 'kilogram': 'kilograms', 'kilograms': 'kilograms',
            'g': 'grams', 'gram': 'grams', 'grams': 'grams',
            'ton': 'tonnes', 'tons': 'tonnes', 'tonne': 'tonnes', 'tonnes': 'tonnes',
            'ha': 'hectares', 'hectare': 'hectares', 'hectares': 'hectares',
            'l': 'liters', 'liter': 'liters', 'liters': 'liters',
            'litre': 'liters', 'litres': 'liters',
            'm': 'meters', 'meter': 'meters', 'meters': 'meters',
            'cm': 'centimeters', 'centimeter': 'centimeters',
            '%': 'percent', 'percent': 'percent'
        }
        
        return unit_mappings.get(unit.lower(), unit)
    
    def _normalize_time_reference(self, time_ref: str) -> str:
        """Normalize time references"""
        time_ref_lower = time_ref.lower().strip()
        
        # Simple normalizations
        if time_ref_lower in ['today', 'tomorrow', 'yesterday']:
            return time_ref_lower
        elif 'season' in time_ref_lower:
            return time_ref_lower
        elif any(month in time_ref_lower for month in ['january', 'february', 'march']):
            return time_ref_lower
        else:
            return time_ref_lower
    
    def _calculate_extraction_confidence(self, entities: Dict, processed: ProcessedText) -> float:
        """Calculate overall extraction confidence"""
        if not any(entities.values()):
            return 0.0
        
        total_confidence = 0.0
        total_entities = 0
        
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                total_confidence += entity.confidence
                total_entities += 1
        
        return round(total_confidence / total_entities, 3) if total_entities > 0 else 0.0
    
    def get_entity_summary(self, extraction_result: EntityExtractionResult) -> Dict[str, Any]:
        """Get summary of extracted entities"""
        summary = {
            'total_entities': extraction_result.entity_count,
            'confidence': extraction_result.extraction_confidence,
            'entity_breakdown': {}
        }
        
        for entity_type, entity_list in extraction_result.entities.items():
            if entity_list:
                unique_entities = list(set(e.normalized_form for e in entity_list))
                summary['entity_breakdown'][entity_type] = {
                    'count': len(entity_list),
                    'unique_entities': unique_entities,
                    'avg_confidence': round(
                        sum(e.confidence for e in entity_list) / len(entity_list), 3
                    )
                }
        
        return summary