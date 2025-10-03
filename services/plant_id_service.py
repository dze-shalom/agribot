"""
Plant.id API Service
Handles plant disease identification using Claude Vision API
"""

import os
import requests
import base64
import logging
from typing import Dict, Optional, List
import anthropic

logger = logging.getLogger(__name__)


class PlantIdService:
    """Service for plant disease identification using Claude Vision API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize plant identification service with Claude API"""
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        self.timeout = 30

        # Initialize Anthropic client if API key is available
        if self.api_key and self.api_key != 'your_api_key_here':
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {str(e)}")
                self.client = None
        else:
            self.client = None

    def identify_health(self, image_data: bytes, language: str = 'en') -> Dict:
        """
        Identify plant health issues from image using Claude Vision API

        Args:
            image_data: Image file bytes
            language: Language code (en, fr, pcm)

        Returns:
            Dictionary with disease identification results
        """
        if not self.client:
            return self._get_fallback_response(language, 'Claude API key not configured')

        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('ascii')

            # Determine image media type (assume common formats)
            media_type = "image/jpeg"
            if image_data[:4] == b'\x89PNG':
                media_type = "image/png"
            elif image_data[:3] == b'GIF':
                media_type = "image/gif"
            elif image_data[:4] == b'RIFF':
                media_type = "image/webp"

            # Prepare language-specific prompt
            prompts = {
                'en': self._get_analysis_prompt_en(),
                'fr': self._get_analysis_prompt_fr(),
                'pcm': self._get_analysis_prompt_pcm()
            }
            prompt = prompts.get(language, prompts['en'])

            # Make API request to Claude
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            # Parse Claude's response
            return self._parse_claude_response(message.content[0].text, language)

        except anthropic.APIError as e:
            logger.error(f'Claude API error: {str(e)}')
            return self._get_fallback_response(language, f'API error: {str(e)}')
        except Exception as e:
            logger.error(f'Error analyzing image with Claude: {str(e)}')
            return self._get_fallback_response(language, str(e))

    def _get_analysis_prompt_en(self) -> str:
        """Get English prompt for plant disease analysis"""
        return """You are an expert agricultural botanist analyzing a plant image for diseases and health issues.

Analyze this plant image and provide:
1. Is the plant healthy? (yes/no)
2. Confidence level (0-100%)
3. If unhealthy, list up to 3 most likely diseases/problems with:
   - Disease name
   - Probability (0-100%)
   - Brief description
   - Treatment recommendations (biological, chemical, and prevention methods)
4. Care recommendations

Format your response as JSON:
{
  "is_healthy": boolean,
  "confidence": float (0-1),
  "diseases": [
    {
      "name": "disease name",
      "probability": float (0-1),
      "description": "brief description",
      "treatment": {
        "biological": ["method 1", "method 2"],
        "chemical": ["fungicide name", "application method"],
        "prevention": ["preventive measure 1", "preventive measure 2"]
      }
    }
  ]
}

Be specific about diseases common in Cameroon agriculture."""

    def _get_analysis_prompt_fr(self) -> str:
        """Get French prompt for plant disease analysis"""
        return """Vous êtes un botaniste agricole expert analysant une image de plante pour détecter les maladies et problèmes de santé.

Analysez cette image de plante et fournissez:
1. La plante est-elle en bonne santé? (oui/non)
2. Niveau de confiance (0-100%)
3. Si malade, listez jusqu'à 3 maladies/problèmes les plus probables avec:
   - Nom de la maladie
   - Probabilité (0-100%)
   - Description brève
   - Recommandations de traitement (méthodes biologiques, chimiques et de prévention)
4. Recommandations de soins

Formatez votre réponse en JSON (en gardant les clés en anglais pour la compatibilité):
{
  "is_healthy": boolean,
  "confidence": float (0-1),
  "diseases": [...]
}

Soyez spécifique sur les maladies courantes dans l'agriculture camerounaise."""

    def _get_analysis_prompt_pcm(self) -> str:
        """Get Pidgin prompt for plant disease analysis"""
        return """You be expert plant doctor wey dey check plant picture to see if e get sickness.

Check dis plant picture well well and tell me:
1. The plant dey healthy? (yes/no)
2. How sure you dey (0-100%)
3. If e sick, show me like 3 sickness wey fit dey worry am with:
   - Sickness name
   - How e fit be (0-100%)
   - Small explanation
   - Wetin we go do (natural treatment, chemical treatment, and how to prevent am)
4. How we go take care of am

Make your answer for JSON format (keep the keys for English so e go work):
{
  "is_healthy": boolean,
  "confidence": float (0-1),
  "diseases": [...]
}

Talk about sickness wey common for Cameroon farming."""

    def _parse_claude_response(self, response_text: str, language: str = 'en') -> Dict:
        """Parse Claude's vision API response"""
        try:
            import json
            import re

            # Try to extract JSON from the response
            # Look for JSON block in the response
            json_match = re.search(r'\{[\s\S]*\}', response_text)

            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)

                # Validate and format the response
                result = {
                    'is_healthy': data.get('is_healthy', True),
                    'confidence': float(data.get('confidence', 0.7)),
                    'diseases': [],
                    'suggestions': []
                }

                # Process diseases
                diseases = data.get('diseases', [])
                for disease in diseases[:3]:
                    disease_info = {
                        'name': disease.get('name', 'Unknown disease'),
                        'probability': float(disease.get('probability', 0.0)),
                        'description': disease.get('description', ''),
                        'treatment': disease.get('treatment', {})
                    }
                    result['diseases'].append(disease_info)

                # Generate suggestions
                if result['is_healthy']:
                    result['suggestions'] = self._get_healthy_suggestions(language)
                else:
                    result['suggestions'] = self._generate_treatment_suggestions(result['diseases'], language)

                return result
            else:
                # If no JSON found, create a response from the text
                logger.warning("No JSON found in Claude response, using fallback parsing")
                return self._parse_text_response(response_text, language)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude JSON response: {str(e)}")
            return self._parse_text_response(response_text, language)
        except Exception as e:
            logger.error(f"Error parsing Claude response: {str(e)}")
            return self._get_fallback_response(language, "Failed to parse analysis")

    def _parse_text_response(self, text: str, language: str = 'en') -> Dict:
        """Parse text-based response when JSON parsing fails"""
        # Basic text analysis
        text_lower = text.lower()

        is_healthy = any(word in text_lower for word in ['healthy', 'good condition', 'no disease', 'sain', 'bonne santé'])

        return {
            'is_healthy': is_healthy,
            'confidence': 0.7,
            'diseases': [],
            'suggestions': [text] if not is_healthy else self._get_healthy_suggestions(language),
            'raw_response': text
        }

    def _parse_health_response(self, data: Dict, language: str = 'en') -> Dict:
        """Parse Plant.id health assessment response"""
        try:
            result = {
                'is_healthy': data.get('is_healthy', True),
                'diseases': [],
                'confidence': 0.0,
                'suggestions': []
            }

            # Extract health assessment
            health_assessment = data.get('health_assessment', {})
            if not health_assessment:
                return result

            # Check if plant is healthy
            is_healthy = health_assessment.get('is_healthy', True)
            is_healthy_probability = health_assessment.get('is_healthy_probability', 1.0)

            result['is_healthy'] = is_healthy
            result['confidence'] = is_healthy_probability

            # Extract diseases if unhealthy
            if not is_healthy:
                diseases = health_assessment.get('diseases', [])

                for disease in diseases[:3]:  # Top 3 diseases
                    disease_info = {
                        'name': disease.get('name', 'Unknown disease'),
                        'probability': disease.get('probability', 0.0),
                        'common_names': disease.get('disease_details', {}).get('common_names', []),
                        'description': disease.get('disease_details', {}).get('description', ''),
                        'treatment': disease.get('disease_details', {}).get('treatment', {})
                    }
                    result['diseases'].append(disease_info)

                # Generate suggestions
                result['suggestions'] = self._generate_treatment_suggestions(result['diseases'], language)
            else:
                result['suggestions'] = self._get_healthy_suggestions(language)

            return result

        except Exception as e:
            logger.error(f'Error parsing Plant.id response: {str(e)}')
            return self._get_fallback_response()

    def _get_healthy_suggestions(self, language: str = 'en') -> List[str]:
        """Get suggestions for healthy plants in specified language"""
        suggestions = {
            'en': [
                'Plant appears healthy!',
                'Continue regular care and monitoring',
                'Maintain proper watering schedule',
                'Ensure adequate sunlight'
            ],
            'fr': [
                'La plante semble en bonne santé!',
                'Continuez les soins et la surveillance régulière',
                'Maintenez un programme d\'arrosage approprié',
                'Assurez un ensoleillement adéquat'
            ],
            'pcm': [
                'Plant dey healthy well well!',
                'Continue to take care of am well',
                'Make sure say you dey water am good',
                'Make sure say sun dey reach am'
            ]
        }
        return suggestions.get(language, suggestions['en'])

    def _generate_treatment_suggestions(self, diseases: List[Dict], language: str = 'en') -> List[str]:
        """Generate treatment suggestions from disease information"""
        suggestions = []

        for disease in diseases:
            treatment = disease.get('treatment', {})

            # Add biological treatment
            biological = treatment.get('biological', [])
            if biological:
                suggestions.append(f"Biological treatment: {biological[0]}")

            # Add chemical treatment
            chemical = treatment.get('chemical', [])
            if chemical:
                suggestions.append(f"Chemical treatment: {chemical[0]}")

            # Add prevention tips
            prevention = treatment.get('prevention', [])
            if prevention:
                suggestions.append(f"Prevention: {prevention[0]}")

        # Add general advice if no specific suggestions
        if not suggestions:
            general_advice = {
                'en': [
                    'Remove affected leaves or parts',
                    'Improve air circulation around the plant',
                    'Avoid overwatering',
                    'Consider consulting a local agricultural expert'
                ],
                'fr': [
                    'Enlevez les feuilles ou parties affectées',
                    'Améliorez la circulation d\'air autour de la plante',
                    'Évitez l\'arrosage excessif',
                    'Consultez un expert agricole local'
                ],
                'pcm': [
                    'Remove the bad leaf dem',
                    'Make air dey blow round the plant',
                    'No pour too much water',
                    'Go meet farming expert for your area'
                ]
            }
            suggestions = general_advice.get(language, general_advice['en'])

        return suggestions[:5]  # Return top 5 suggestions

    def _get_fallback_response(self, language: str = 'en', error_message: str = None) -> Dict:
        """Return fallback response when API is unavailable"""
        message = error_message if error_message else "Plant.id API key not configured"

        fallback_suggestions = {
            'en': [
                '⚠️ AI disease detection not available',
                'Please describe the symptoms you see',
                'Look for: discoloration, spots, wilting, or unusual growth',
                'I can help identify diseases based on your description'
            ],
            'fr': [
                '⚠️ Détection de maladies IA non disponible',
                'Veuillez décrire les symptômes que vous voyez',
                'Recherchez: décoloration, taches, flétrissement ou croissance inhabituelle',
                'Je peux aider à identifier les maladies selon votre description'
            ],
            'pcm': [
                '⚠️ AI disease detection no dey work now',
                'Tell me wetin you see for the plant',
                'Check if the plant color don change, get spot, or dey dry',
                'I fit help you find the sickness if you tell me wetin you see'
            ]
        }

        return {
            'is_healthy': None,
            'diseases': [],
            'confidence': 0.0,
            'suggestions': fallback_suggestions.get(language, fallback_suggestions['en']),
            'error': message,
            'fallback': True
        }

    def format_response_text(self, health_data: Dict) -> str:
        """Format health assessment data into readable text"""

        if health_data.get('fallback'):
            return f"""**Image Analysis Result**

WARNING: {health_data.get('error', 'Unable to analyze image automatically')}

However, I can still help! Please describe what you see on the plant:
- Are there any spots or discoloration?
- Are the leaves wilting or curling?
- Do you see any insects or pests?
- Is there unusual growth or decay?

I'll help you identify the issue and provide treatment recommendations!"""

        if health_data.get('is_healthy'):
            return f"""**Plant Health Analysis**

GOOD NEWS: Your plant appears to be healthy!

**Confidence:** {health_data.get('confidence', 0) * 100:.1f}%

**Care Recommendations:**
""" + "\n".join(f"- {sug}" for sug in health_data.get('suggestions', []))

        # Plant has diseases
        response = """**Plant Health Analysis**

**Potential issues detected:**\n\n"""

        diseases = health_data.get('diseases', [])
        for i, disease in enumerate(diseases, 1):
            response += f"**{i}. {disease['name']}**\n"
            response += f"   - Probability: {disease['probability'] * 100:.1f}%\n"

            if disease.get('description'):
                # Truncate long descriptions
                desc = disease['description']
                if len(desc) > 200:
                    desc = desc[:200] + "..."
                response += f"   - Details: {desc}\n"

            response += "\n"

        # Add treatment suggestions
        response += "\n**Treatment Recommendations:**\n"
        suggestions = health_data.get('suggestions', [])
        for sug in suggestions:
            response += f"- {sug}\n"

        response += "\n**Tip:** Take action early for best results!"

        return response
