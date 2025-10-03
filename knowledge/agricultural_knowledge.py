"""
Agricultural Knowledge Base
Location: agribot/knowledge/agricultural_knowledge.py

Comprehensive domain knowledge about agricultural practices, diseases, 
fertilizers, and farming procedures specific to Cameroon.
"""

from typing import Dict, List, Optional, Any
import random
from knowledge.crop_database import CropDatabase
from knowledge.regional_expertise import RegionalExpertise

class AgriculturalKnowledgeBase:
    """Central repository for agricultural domain knowledge"""
    
    def __init__(self):
        self.crop_db = CropDatabase()
        self.regional_expert = RegionalExpertise()
        
        # Load core knowledge databases
        self.diseases = self._load_disease_database()
        self.fertilizers = self._load_fertilizer_guide()
        self.planting_procedures = self._load_planting_procedures()
        self.pest_control = self._load_pest_control_guide()
        self.harvest_timing = self._load_harvest_timing()
        self.response_templates = self._load_response_templates()
    
    def get_comprehensive_crop_info(self, crop: str) -> Dict[str, Any]:
        """Get all available information about a specific crop"""
        crop_info = {
            'crop_name': crop,
            'basic_info': self.crop_db.get_crop_basics(crop),
            'diseases': self.get_disease_info(crop),
            'pests': self.get_pest_info(crop),
            'fertilizer_program': self.get_fertilizer_recommendation(crop),
            'planting_guide': self.get_planting_guide(crop),
            'harvest_info': self.get_harvest_timing(crop),
            'regional_suitability': self.regional_expert.get_crop_suitability(crop),
            'yield_optimization': self.get_yield_tips(crop)
        }
        return crop_info
    
    def get_disease_info(self, crop: str, disease_name: str = None) -> Dict[str, Any]:
        """Get disease information for a crop"""
        crop_diseases = self.diseases.get(crop.lower(), {})
        
        if disease_name:
            disease_key = disease_name.lower().replace(' ', '_')
            specific_disease = crop_diseases.get(disease_key)
            
            if specific_disease:
                return {
                    'crop': crop,
                    'disease': disease_name,
                    'symptoms': specific_disease['symptoms'],
                    'causes': specific_disease['causes'],
                    'treatment': specific_disease['treatment'],
                    'prevention': specific_disease['prevention'],
                    'severity': specific_disease.get('severity', 'moderate'),
                    'seasonal_occurrence': specific_disease.get('seasonal_occurrence', 'year_round')
                }
            else:
                return {'error': f'Disease "{disease_name}" not found for {crop}'}
        else:
            return {
                'crop': crop,
                'available_diseases': list(crop_diseases.keys()),
                'common_symptoms': self._get_common_symptoms(crop_diseases),
                'total_diseases': len(crop_diseases)
            }
    
    def get_fertilizer_recommendation(self, crop: str, growth_stage: str = 'all') -> Dict[str, Any]:
        """Get fertilizer recommendations for a crop"""
        crop_fertilizers = self.fertilizers.get(crop.lower(), {})
        
        if not crop_fertilizers:
            return {
                'crop': crop,
                'general_recommendation': self._get_general_fertilizer_advice(crop),
                'note': 'Specific fertilizer program not available - using general guidelines'
            }
        
        if growth_stage == 'all':
            return {
                'crop': crop,
                'complete_program': crop_fertilizers,
                'key_nutrients': self._identify_key_nutrients(crop),
                'application_schedule': self._create_fertilizer_schedule(crop_fertilizers),
                'organic_alternatives': crop_fertilizers.get('organic_options', {})
            }
        else:
            stage_info = crop_fertilizers.get(growth_stage)
            return {
                'crop': crop,
                'growth_stage': growth_stage,
                'recommendation': stage_info if stage_info else f'No specific guidance for {growth_stage} stage',
                'next_application': self._get_next_fertilizer_stage(crop_fertilizers, growth_stage)
            }
    
    def get_planting_guide(self, crop: str) -> Dict[str, Any]:
        """Get comprehensive planting guide for a crop"""
        planting_info = self.planting_procedures.get(crop.lower())
        
        if planting_info:
            return {
                'crop': crop,
                'land_preparation': planting_info['land_preparation'],
                'seed_preparation': planting_info.get('seed_preparation', []),
                'planting_process': planting_info['planting'],
                'post_planting_care': planting_info.get('post_planting', []),
                'timing_guide': {'optimal_planting_time': 'Beginning of rainy season (March-May)'},
                'spacing_requirements': {'row_spacing': '75cm', 'plant_spacing': '25cm'},
                'success_indicators': ['Good germination (>80%)', 'Healthy green leaves', 'Strong root development']
            }
        else:
            return {
                'crop': crop,
                'error': 'Detailed planting guide not available',
                'general_steps': self._get_general_planting_steps(),
                'recommendation': f'Consult local extension services for specific {crop} planting guidance'
            }
    
    def get_pest_info(self, crop: str, pest_name: str = None) -> Dict[str, Any]:
        """Get pest control information"""
        crop_pests = self.pest_control.get(crop.lower(), {})
        
        if pest_name:
            pest_key = pest_name.lower().replace(' ', '_')
            specific_pest = crop_pests.get(pest_key)
            
            if specific_pest:
                return {
                    'crop': crop,
                    'pest': pest_name,
                    'identification': specific_pest['identification'],
                    'damage_signs': specific_pest['damage'],
                    'control_methods': specific_pest['control'],
                    'prevention': specific_pest['prevention'],
                    'natural_enemies': specific_pest.get('natural_enemies', []),
                    'chemical_control': specific_pest.get('chemical_options', [])
                }
        
        return {
            'crop': crop,
            'common_pests': list(crop_pests.keys()),
            'integrated_pest_management': self._get_ipm_strategy(crop),
            'monitoring_schedule': self._get_pest_monitoring_schedule(crop)
        }
    
    def get_harvest_timing(self, crop: str) -> Dict[str, Any]:
        """Get harvest timing and post-harvest handling information"""
        harvest_info = self.harvest_timing.get(crop.lower(), {})
        
        return {
            'crop': crop,
            'maturity_indicators': harvest_info.get('maturity_signs', []),
            'optimal_harvest_time': harvest_info.get('timing', 'When fully mature'),
            'harvest_method': harvest_info.get('method', 'Hand picking'),
            'post_harvest_handling': harvest_info.get('post_harvest', []),
            'storage_requirements': harvest_info.get('storage', {}),
            'expected_yield': harvest_info.get('expected_yield', 'Varies by variety and conditions')
        }
    
    def get_yield_tips(self, crop: str) -> Dict[str, Any]:
        """Get yield optimization strategies"""
        yield_strategies = {
            'crop': crop,
            'key_factors': self._get_yield_factors(crop),
            'optimization_strategies': self._get_optimization_strategies(crop),
            'common_mistakes': self._get_common_mistakes(crop),
            'monitoring_checkpoints': self._get_monitoring_points(crop)
        }
        
        return yield_strategies
    
    def generate_natural_response(self, topic: str, context: Dict = None, 
                                user_name: str = 'Friend') -> str:
        """Generate natural, conversational response"""
        templates = self.response_templates.get(topic, {})
        
        if not templates:
            return f"I'd be happy to help with {topic}. What specific information do you need?"
        
        # Select appropriate template based on context
        template_key = self._select_response_template(templates, context)
        template = templates.get(template_key, templates.get('general', ''))
        
        # Format template with context
        return self._format_response_template(template, context or {}, user_name)
    
    def _load_disease_database(self) -> Dict[str, Dict]:
        """Load comprehensive disease information"""
        return {
            'maize': {
                'maize_streak_virus': {
                    'symptoms': ['Yellow streaks on leaves', 'Stunted growth', 'Reduced grain yield'],
                    'causes': ['Leafhopper transmission', 'Infected planting material', 'Poor field sanitation'],
                    'treatment': ['Remove infected plants', 'Control leafhoppers with neem oil', 'Use resistant varieties'],
                    'prevention': ['Plant certified seeds', 'Early planting', 'Control vector insects'],
                    'severity': 'high',
                    'seasonal_occurrence': 'rainy_season'
                },
                'northern_corn_leaf_blight': {
                    'symptoms': ['Long gray-green lesions on leaves', 'Lesions with dark borders', 'Premature leaf death'],
                    'causes': ['Fungal pathogen', 'High humidity', 'Cool temperatures', 'Dense planting'],
                    'treatment': ['Apply fungicide sprays', 'Remove crop residue', 'Improve air circulation'],
                    'prevention': ['Use resistant varieties', 'Crop rotation', 'Proper spacing'],
                    'severity': 'moderate',
                    'seasonal_occurrence': 'cool_humid_periods'
                },
                'fall_armyworm': {
                    'symptoms': ['Holes in leaves', 'Missing plant parts', 'Visible caterpillars in whorl'],
                    'causes': ['Armyworm moth infestation', 'Favorable weather conditions', 'Continuous cropping'],
                    'treatment': ['Handpicking caterpillars', 'Bt spray application', 'Targeted insecticides'],
                    'prevention': ['Early planting', 'Trap crops', 'Natural predator conservation'],
                    'severity': 'high',
                    'seasonal_occurrence': 'year_round'
                }
            },
            'tomatoes': {
                'early_blight': {
                    'symptoms': ['Brown spots with concentric rings', 'Yellow halos around spots', 'Defoliation'],
                    'causes': ['Alternaria solani fungus', 'Warm humid conditions', 'Plant stress'],
                    'treatment': ['Copper-based fungicides', 'Remove affected leaves', 'Improve ventilation'],
                    'prevention': ['Drip irrigation', 'Mulching', 'Resistant varieties'],
                    'severity': 'moderate',
                    'seasonal_occurrence': 'warm_humid_season'
                },
                'bacterial_wilt': {
                    'symptoms': ['Sudden wilting', 'Brown vascular discoloration', 'Plant death'],
                    'causes': ['Ralstonia solanacearum bacteria', 'Soil contamination', 'Root wounds'],
                    'treatment': ['Remove infected plants', 'Soil solarization', 'Resistant rootstocks'],
                    'prevention': ['Clean tools', 'Avoid waterlogging', 'Crop rotation'],
                    'severity': 'very_high',
                    'seasonal_occurrence': 'warm_wet_conditions'
                }
            },
            'cassava': {
                'cassava_mosaic_disease': {
                    'symptoms': ['Yellow-green mosaic on leaves', 'Leaf distortion', 'Stunted growth'],
                    'causes': ['Whitefly transmission', 'Infected cuttings', 'Viral infection'],
                    'treatment': ['Use clean planting material', 'Control whiteflies', 'Remove infected plants'],
                    'prevention': ['Certified cuttings', 'Vector control', 'Field sanitation'],
                    'severity': 'high',
                    'seasonal_occurrence': 'year_round'
                }
            }
        }
    
    def _load_fertilizer_guide(self) -> Dict[str, Dict]:
        """Load fertilizer recommendations"""
        return {
            'maize': {
                'basal_application': {
                    'fertilizer': 'NPK 20-10-10',
                    'rate': '300kg per hectare',
                    'timing': 'At planting or 1 week after emergence',
                    'method': 'Band placement 5cm from seeds'
                },
                'top_dressing': {
                    'fertilizer': 'Urea 46-0-0',
                    'rate': '150kg per hectare',
                    'timing': '4-6 weeks after planting',
                    'method': 'Side dress and incorporate lightly'
                },
                'organic_options': {
                    'compost': '3-4 tons per hectare before planting',
                    'poultry_manure': '2 tons per hectare (well decomposed)',
                    'green_manure': 'Plant legume cover crops in rotation'
                }
            },
            'tomatoes': {
                'nursery_stage': {
                    'fertilizer': 'Balanced NPK 15-15-15',
                    'rate': '50g per square meter',
                    'timing': 'Mix with nursery soil before sowing',
                    'method': 'Thorough incorporation'
                },
                'transplanting': {
                    'fertilizer': 'NPK 20-10-20 + compost',
                    'rate': '250kg NPK + 5 tons compost per hectare',
                    'timing': 'At transplanting',
                    'method': 'Apply in planting holes'
                },
                'flowering_fruiting': {
                    'fertilizer': 'High potassium fertilizer',
                    'rate': '150kg per hectare every 2 weeks',
                    'timing': 'From first flower formation',
                    'method': 'Side dress and water immediately'
                }
            }
        }
    
    def _load_planting_procedures(self) -> Dict[str, Dict]:
        """Load detailed planting procedures"""
        return {
            'maize': {
                'land_preparation': [
                    'Clear field of weeds and crop residue completely',
                    'Plow to 20-25cm depth when soil has optimal moisture',
                    'Make ridges if drainage is poor or in heavy clay soils',
                    'Apply organic matter and incorporate well',
                    'Level field if necessary for uniform water distribution'
                ],
                'seed_preparation': [
                    'Select certified seeds with >85% germination rate',
                    'Test germination before planting season begins',
                    'Treat seeds with recommended fungicide/insecticide',
                    'Store treated seeds in cool, dry conditions'
                ],
                'planting': [
                    'Plant at onset of reliable rains (March-May in most regions)',
                    'Space rows 75cm apart with 25cm between plants within rows',
                    'Plant 2-3 seeds per hole at 3-5cm depth',
                    'Cover seeds with fine soil and firm gently',
                    'Apply starter fertilizer if not done during land preparation'
                ],
                'post_planting': [
                    'Thin to 1-2 strongest plants per stand at 2 weeks',
                    'Begin weeding program - critical first 6 weeks',
                    'Apply first top-dressing at 4-6 weeks',
                    'Monitor for pests and diseases throughout season',
                    'Provide support for tall varieties if necessary'
                ]
            },
            'tomatoes': {
                'land_preparation': [
                    'Choose well-drained site with 6+ hours daily sunlight',
                    'Test soil pH and adjust to 6.0-6.8 if necessary',
                    'Make raised beds 1m wide, 20cm high for good drainage',
                    'Incorporate 4-5 tons compost or well-aged manure per hectare',
                    'Install irrigation system if rainfall is unreliable'
                ],
                'seed_preparation': [
                    'Prepare nursery beds with sterilized soil mixture',
                    'Sow seeds 1cm deep with 2cm spacing between seeds',
                    'Maintain soil temperature at 20-25°C for germination',
                    'Water gently twice daily to maintain moisture',
                    'Provide shade during hottest part of day'
                ],
                'planting': [
                    'Transplant when seedlings have 4-6 true leaves',
                    'Harden seedlings 1 week before transplanting',
                    'Space plants 45cm apart with 60cm between rows',
                    'Transplant in evening or cloudy day to reduce shock',
                    'Water immediately and daily for first week'
                ]
            },
            'pepper': {
                'land_preparation': [
                    'Choose well-drained site with full sunlight exposure',
                    'Test soil pH and adjust to 6.0-6.8 for optimal growth',
                    'Make raised beds 15cm high for improved drainage',
                    'Incorporate 3-4 tons compost per hectare into soil',
                    'Install mulching materials to conserve moisture'
                ],
                'seed_preparation': [
                    'Select high-quality certified pepper seeds with 85%+ germination',
                    'Soak seeds in warm water for 8-12 hours before sowing',
                    'Prepare nursery beds with fine, well-draining soil mix',
                    'Sow seeds 0.5cm deep with 3cm spacing in nursery',
                    'Maintain optimal temperature at 25-30°C for germination'
                ],
                'planting': [
                    'Transplant when seedlings reach 10-15cm height with 4-6 leaves',
                    'Harden seedlings for 7-10 days before transplanting',
                    'Space plants 30cm apart with 50cm between rows',
                    'Transplant during cool morning or evening hours',
                    'Water thoroughly after transplanting and maintain regular irrigation'
                ]
            }
        }
    
    def _load_pest_control_guide(self) -> Dict[str, Dict]:
        """Load pest control information"""
        return {
            'maize': {
                'fall_armyworm': {
                    'identification': 'Gray-brown caterpillars with distinctive head capsule markings',
                    'damage': 'Circular holes in leaves, damaged growing points, reduced yield',
                    'control': ['Early morning handpicking', 'Bt-based biopesticides', 'Neem oil application'],
                    'prevention': ['Early planting', 'Intercropping with legumes', 'Conservation of natural enemies'],
                    'natural_enemies': ['Spiders', 'Ground beetles', 'Parasitic wasps']
                },
                'stem_borer': {
                    'identification': 'Caterpillars boring into maize stems, visible entry holes',
                    'damage': 'Weakened stems, broken plants, reduced grain filling',
                    'control': ['Cut and destroy infested stems', 'Biological control agents', 'Pheromone traps'],
                    'prevention': ['Clean cultivation', 'Crop rotation', 'Resistant varieties']
                }
            },
            'tomatoes': {
                'whitefly': {
                    'identification': 'Small white flying insects on undersides of leaves',
                    'damage': 'Yellowing leaves, sooty mold, virus transmission',
                    'control': ['Yellow sticky traps', 'Reflective mulches', 'Insecticidal soaps'],
                    'prevention': ['Screen houses', 'Remove weeds', 'Avoid over-fertilizing with nitrogen']
                }
            }
        }
    
    def _load_harvest_timing(self) -> Dict[str, Dict]:
        """Load harvest timing information"""
        return {
            'maize': {
                'maturity_signs': ['Husks turn brown and dry', 'Kernels dent and become hard', 'Moisture content 20-25%'],
                'timing': '90-120 days after planting depending on variety',
                'method': 'Hand harvesting of ears when husks are dry',
                'post_harvest': ['Dry to 12-14% moisture content', 'Remove damaged kernels', 'Store in sealed containers'],
                'storage': {'moisture': '12-14%', 'temperature': 'Cool and dry', 'pest_control': 'Regular monitoring'},
                'expected_yield': '2-6 tons per hectare depending on variety and management'
            },
            'tomatoes': {
                'maturity_signs': ['Color change from green to desired final color', 'Slight softening', 'Easy separation from vine'],
                'timing': '70-90 days from transplanting for determinate varieties',
                'method': 'Hand picking every 2-3 days when fruits reach mature green or breaker stage',
                'post_harvest': ['Sort by maturity stage', 'Handle gently to avoid bruising', 'Pack in ventilated containers'],
                'storage': {'temperature': '12-15°C for green, 20-25°C for ripe', 'humidity': '85-90%', 'ventilation': 'Good air circulation'},
                'expected_yield': '20-40 tons per hectare for indeterminate varieties with good management'
            }
        }
    
    def _load_response_templates(self) -> Dict[str, Dict]:
        """Load conversational response templates"""
        return {
            'greeting': {
                'general': "Hello {name}! I'm here to help with your agricultural questions. What would you like to know about farming today?",
                'returning_user': "Welcome back {name}! Ready to continue our farming discussion?",
                'crop_specific': "Hi {name}! I see you're interested in {crop}. I have comprehensive information to help you succeed with this crop."
            },
            'disease_inquiry': {
                'general': "I can help identify and treat plant diseases. Can you describe what you're seeing on your {crop}?",
                'specific_symptoms': "Based on your description of {symptoms}, this could be {disease}. Let me explain the treatment options.",
                'prevention_focus': "Prevention is always better than cure. For {crop}, here are the key disease prevention strategies."
            },
            'fertilizer_advice': {
                'general': "For {crop} fertilization, timing and application method are crucial. Here's what I recommend:",
                'stage_specific': "At the {stage} stage, your {crop} needs specific nutrients. Here's the optimal approach:",
                'organic_focus': "Organic fertilization for {crop} can be very effective. Here are proven organic approaches:"
            }
        }
    
    # Helper methods for processing and formatting responses
    def _get_common_symptoms(self, diseases_dict: Dict) -> List[str]:
        """Extract common symptoms across diseases"""
        all_symptoms = []
        for disease_info in diseases_dict.values():
            all_symptoms.extend(disease_info.get('symptoms', []))
        
        # Count frequency and return most common
        from collections import Counter
        symptom_counts = Counter(all_symptoms)
        return [symptom for symptom, count in symptom_counts.most_common(5)]
    
    def _identify_key_nutrients(self, crop: str) -> List[str]:
        """Identify key nutrients for a crop"""
        nutrient_needs = {
            'maize': ['Nitrogen', 'Phosphorus', 'Potassium'],
            'tomatoes': ['Nitrogen', 'Phosphorus', 'Potassium', 'Calcium'],
            'cassava': ['Potassium', 'Phosphorus'],
            'beans': ['Phosphorus', 'Potassium', 'Molybdenum']
        }
        return nutrient_needs.get(crop.lower(), ['Nitrogen', 'Phosphorus', 'Potassium'])
    
    def _get_general_fertilizer_advice(self, crop: str) -> Dict[str, str]:
        """Provide general fertilizer advice when specific program unavailable"""
        return {
            'base_recommendation': 'Apply balanced NPK fertilizer based on soil test results',
            'organic_option': 'Use compost or well-aged manure as base fertilizer',
            'timing': 'Split application - basal at planting, top-dressing during active growth',
            'note': f'Consult local extension services for specific {crop} fertilizer programs'
        }
    
    def _select_response_template(self, templates: Dict, context: Dict) -> str:
        """Select appropriate response template based on context"""
        if not context:
            return 'general'
        
        # Simple template selection logic
        if 'crop' in context and 'crop_specific' in templates:
            return 'crop_specific'
        elif 'returning_user' in context and 'returning_user' in templates:
            return 'returning_user'
        else:
            return 'general'
    
    def _get_general_planting_steps(self) -> List[str]:
        """Get general planting steps for any crop"""
        return [
            "Choose healthy, certified seeds appropriate for your region",
            "Prepare the soil by clearing, tilling, and adding organic matter",
            "Plant at the right spacing and depth for the specific crop",
            "Water regularly but avoid overwatering to prevent root rot",
            "Monitor for pests and diseases and take early action",
            "Apply fertilizers based on soil test recommendations"
        ]

    def _format_response_template(self, template: str, context: Dict, user_name: str) -> str:
        """Format response template with context variables"""
        format_dict = {'name': user_name}
        format_dict.update(context)

        try:
            return template.format(**format_dict)
        except KeyError:
            # Return template without formatting if variables are missing
            return template

    def export_for_claude_context(self) -> Dict[str, Any]:
        """Export knowledge base in structured format for Claude API context"""
        try:
            export_data = {
                'crops': {
                    'maize': self.get_comprehensive_crop_info('maize'),
                    'tomatoes': self.get_comprehensive_crop_info('tomatoes'),
                    'pepper': self.get_comprehensive_crop_info('pepper'),
                    'cassava': self.get_comprehensive_crop_info('cassava'),
                    'beans': self.get_comprehensive_crop_info('beans')
                },
                'general_knowledge': {
                    'diseases': self.diseases,
                    'fertilizers': self.fertilizers,
                    'pest_control': self.pest_control,
                    'harvest_timing': self.harvest_timing
                },
                'regional_info': {
                    'cameroon_regions': [
                        'Centre', 'Littoral', 'West', 'Northwest', 'Southwest',
                        'East', 'North', 'Far North', 'Adamawa', 'South'
                    ],
                    'climate_zones': self.regional_expert.climate_zones if hasattr(self.regional_expert, 'climate_zones') else {},
                    'regional_expertise': 'Available for all Cameroon regions'
                },
                'best_practices': {
                    'sustainable_farming': [
                        'Crop rotation to maintain soil health',
                        'Integrated pest management (IPM)',
                        'Water conservation techniques',
                        'Organic matter incorporation',
                        'Minimal tillage practices'
                    ],
                    'soil_health': [
                        'Regular soil testing',
                        'Balanced fertilization',
                        'Erosion control measures',
                        'Cover cropping',
                        'pH management'
                    ]
                }
            }
            return export_data
        except Exception as e:
            # Return simplified structure if full export fails
            return {
                'crops': ['maize', 'tomatoes', 'pepper', 'cassava', 'beans'],
                'focus': 'Cameroon agricultural practices',
                'error': f'Partial export due to: {str(e)}'
            }