"""
Text Processing Module
Location: agribot/nlp/text_processor.py

Handles text preprocessing, cleaning, and normalization for agricultural
text input before intent classification and entity extraction.
"""

import re
import string
from typing import List, Dict, Set, Any
from dataclasses import dataclass

@dataclass
class ProcessedText:
    """Data structure for processed text results"""
    original: str
    cleaned: str
    tokens: List[str]
    normalized_tokens: List[str]
    language: str
    preprocessing_steps: List[str]

class TextProcessor:
    """Comprehensive text processing for agricultural domain"""
    
    def __init__(self):
        # Agricultural domain stop words (English and French common words)
        self.stop_words = {
            'english': {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                'to', 'was', 'will', 'with', 'i', 'you', 'my', 'me', 'we', 'can',
                'could', 'should', 'would', 'have', 'had', 'do', 'does', 'did'
            },
            'french': {
                'le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir',
                'que', 'pour', 'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne',
                'se', 'pas', 'tout', 'plus', 'par', 'grand', 'en', 'une', 'être'
            }
        }
        
        # Agricultural term corrections (common misspellings)
        self.spelling_corrections = {
            'casava': 'cassava',
            'maze': 'maize',
            'tomatoe': 'tomato',
            'tomatos': 'tomatoes',
            'pineaple': 'pineapple',
            'coffe': 'coffee',
            'bannana': 'banana',
            'ferterlizer': 'fertilizer',
            'fertalizer': 'fertilizer',
            'pestecide': 'pesticide',
            'insectecide': 'insecticide',
            'diesease': 'disease',
            'desease': 'disease',
            'yeild': 'yield',
            'plantin': 'plantain',
            'groundnut': 'groundnuts'
        }
        
        # Agricultural abbreviations and expansions
        self.abbreviations = {
            'npk': 'nitrogen phosphorus potassium',
            'fao': 'food and agriculture organization',
            'ipm': 'integrated pest management',
            'ha': 'hectare',
            'kg': 'kilogram',
            'cm': 'centimeter',
            'mm': 'millimeter',
            'ph': 'soil acidity level',
            'gmo': 'genetically modified organism'
        }
        
        # Language detection patterns
        self.language_patterns = {
            'french': ['je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 
                      'comment', 'pourquoi', 'quand', 'où', 'que', 'qui', 'avec'],
            'english': ['i', 'you', 'he', 'she', 'we', 'they', 'how', 'why', 
                       'when', 'where', 'what', 'who', 'with']
        }
    
    def process_text(self, text: str, preserve_original: bool = True) -> ProcessedText:
        """Comprehensive text processing pipeline"""
        if not text or not text.strip():
            return ProcessedText(
                original=text,
                cleaned="",
                tokens=[],
                normalized_tokens=[],
                language="unknown",
                preprocessing_steps=["empty_input"]
            )
        
        processing_steps = []
        processed = text.strip()
        
        # Step 1: Basic cleaning
        processed = self._basic_cleaning(processed)
        processing_steps.append("basic_cleaning")
        
        # Step 2: Language detection
        language = self._detect_language(processed)
        processing_steps.append(f"language_detection_{language}")
        
        # Step 3: Spelling correction
        processed = self._correct_spelling(processed)
        processing_steps.append("spelling_correction")
        
        # Step 4: Expand abbreviations
        processed = self._expand_abbreviations(processed)
        processing_steps.append("abbreviation_expansion")
        
        # Step 5: Tokenization
        tokens = self._tokenize(processed)
        processing_steps.append("tokenization")
        
        # Step 6: Normalization
        normalized_tokens = self._normalize_tokens(tokens, language)
        processing_steps.append("normalization")
        
        return ProcessedText(
            original=text if preserve_original else "",
            cleaned=processed,
            tokens=tokens,
            normalized_tokens=normalized_tokens,
            language=language,
            preprocessing_steps=processing_steps
        )
    
    def _basic_cleaning(self, text: str) -> str:
        """Basic text cleaning operations"""
        # Convert to lowercase for processing
        text = text.lower()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep agricultural punctuation
        # Keep periods, commas, question marks, and hyphens
        text = re.sub(r'[^\w\s\.\,\?\!\-\']', ' ', text)
        
        # Remove multiple punctuation marks
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[!]{2,}', '!', text)
        
        # Handle contractions (expand them)
        contractions = {
            "don't": "do not",
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        return text.strip()
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on common words"""
        words = text.lower().split()
        
        if len(words) < 2:
            return "unknown"
        
        french_score = 0
        english_score = 0
        
        for word in words:
            if word in self.language_patterns['french']:
                french_score += 1
            elif word in self.language_patterns['english']:
                english_score += 1
        
        if french_score > english_score:
            return "french"
        elif english_score > 0:
            return "english"
        else:
            # Default to English for agricultural context
            return "english"
    
    def _correct_spelling(self, text: str) -> str:
        """Correct common agricultural spelling mistakes"""
        words = text.split()
        corrected_words = []
        
        for word in words:
            # Remove punctuation for comparison
            clean_word = word.strip(string.punctuation)
            
            if clean_word in self.spelling_corrections:
                # Preserve original punctuation
                corrected = self.spelling_corrections[clean_word]
                if word != clean_word:
                    # Add back punctuation
                    punctuation = ''.join(c for c in word if c in string.punctuation)
                    corrected = corrected + punctuation
                corrected_words.append(corrected)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    def _expand_abbreviations(self, text: str) -> str:
        """Expand agricultural abbreviations"""
        for abbrev, expansion in self.abbreviations.items():
            # Handle both uppercase and lowercase
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
        
        return text
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Split on whitespace and punctuation, but keep important punctuation
        tokens = re.findall(r'\w+|[.!?]', text)
        
        # Filter out very short tokens (single characters except 'i' and 'a')
        filtered_tokens = []
        for token in tokens:
            if len(token) > 1 or token.lower() in ['a', 'i']:
                filtered_tokens.append(token)
        
        return filtered_tokens
    
    def _normalize_tokens(self, tokens: List[str], language: str) -> List[str]:
        """Normalize tokens by removing stop words and applying transformations"""
        stop_words = self.stop_words.get(language, self.stop_words['english'])
        
        normalized = []
        for token in tokens:
            # Skip punctuation
            if token in ['.', '!', '?']:
                continue
            
            # Convert to lowercase
            token_lower = token.lower()
            
            # Skip stop words
            if token_lower in stop_words:
                continue
            
            # Apply agricultural domain stemming (simplified)
            token_stemmed = self._simple_stem(token_lower)
            
            normalized.append(token_stemmed)
        
        return normalized
    
    def _simple_stem(self, word: str) -> str:
        """Simple stemming for agricultural terms"""
        # Common agricultural suffixes to remove
        suffixes = {
            'ing': 'plant',      # planting -> plant
            'ed': '',            # planted -> plant
            'er': '',            # farmer -> farm
            'est': '',           # biggest -> big
            'ly': '',            # quickly -> quick
            'tion': '',          # cultivation -> cultivat
            'ment': '',          # treatment -> treat
            'ness': '',          #ickness -> thick
            'ity': '',           # fertility -> fertil
            's': ''              # crops -> crop (handle plurals)
        }
        
        # Only stem if word is longer than 4 characters
        if len(word) <= 4:
            return word
        
        for suffix, replacement in suffixes.items():
            if word.endswith(suffix):
                stem = word[:-len(suffix)] + replacement
                # Ensure stem is at least 3 characters
                if len(stem) >= 3:
                    return stem
        
        return word
    
    def extract_keywords(self, processed_text: ProcessedText, 
                        min_length: int = 3) -> List[str]:
        """Extract keywords from processed text"""
        keywords = []
        
        for token in processed_text.normalized_tokens:
            if (len(token) >= min_length and 
                token not in self.stop_words['english'] and
                token not in self.stop_words['french']):
                keywords.append(token)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords
    
    def get_text_statistics(self, processed_text: ProcessedText) -> Dict[str, Any]:
        """Get statistical information about processed text"""
        original_words = len(processed_text.original.split()) if processed_text.original else 0
        
        return {
            'original_length': len(processed_text.original) if processed_text.original else 0,
            'cleaned_length': len(processed_text.cleaned),
            'original_words': original_words,
            'tokens_count': len(processed_text.tokens),
            'normalized_tokens_count': len(processed_text.normalized_tokens),
            'compression_ratio': round(
                len(processed_text.normalized_tokens) / original_words 
                if original_words > 0 else 0, 2
            ),
            'language': processed_text.language,
            'processing_steps': processed_text.preprocessing_steps
        }
    
    def is_agricultural_query(self, processed_text: ProcessedText) -> bool:
        """Determine if text is likely agricultural query"""
        agricultural_indicators = {
            'crop_words': ['crop', 'plant', 'grow', 'farm', 'cultivat', 'harvest'],
            'problem_words': ['disease', 'pest', 'problem', 'issue', 'damage', 'sick'],
            'practice_words': ['fertilizer', 'seed', 'soil', 'water', 'irrigation'],
            'specific_crops': ['maize', 'cassava', 'tomato', 'bean', 'rice', 'cocoa']
        }
        
        tokens = processed_text.normalized_tokens
        agricultural_score = 0
        
        for category, words in agricultural_indicators.items():
            for word in words:
                if word in tokens:
                    agricultural_score += 2 if category == 'specific_crops' else 1
        
        # Consider it agricultural if score is above threshold
        return agricultural_score >= 2
    
    def clean_for_display(self, text: str) -> str:
        """Clean text for display purposes without heavy processing"""
        if not text:
            return ""
        
        # Basic cleaning only
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        # Ensure proper ending punctuation
        if text and text[-1] not in ['.', '!', '?']:
            text += '.'
        
        return text

# Utility functions for text analysis
def calculate_text_similarity(text1: str, text2: str, processor: TextProcessor = None) -> float:
    """Calculate similarity between two texts based on token overlap"""
    if not processor:
        processor = TextProcessor()
    
    processed1 = processor.process_text(text1)
    processed2 = processor.process_text(text2)
    
    tokens1 = set(processed1.normalized_tokens)
    tokens2 = set(processed2.normalized_tokens)
    
    if not tokens1 and not tokens2:
        return 1.0
    if not tokens1 or not tokens2:
        return 0.0
    
    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    
    return intersection / union if union > 0 else 0.0

def extract_ngrams(tokens: List[str], n: int = 2) -> List[str]:
    """Extract n-grams from token list"""
    if len(tokens) < n:
        return []
    
    ngrams = []
    for i in range(len(tokens) - n + 1):
        ngram = ' '.join(tokens[i:i+n])
        ngrams.append(ngram)
    
    return ngrams