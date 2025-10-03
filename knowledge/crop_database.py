"""
Crop Database
Location: agribot/knowledge/crop_database.py

Comprehensive database of crop varieties, characteristics, and growing
requirements specific to crops cultivated in Cameroon.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class CropVariety:
    """Data structure for crop variety information"""
    name: str
    maturity_days: int
    yield_potential: str
    disease_resistance: List[str]
    climate_zones: List[str]
    special_characteristics: List[str]

class CropDatabase:
    """Database of crop information and varieties"""
    
    def __init__(self):
        self.crops = self._initialize_crop_database()
        self.crop_categories = self._define_crop_categories()
        self.nutritional_requirements = self._load_nutritional_requirements()
        self.climate_preferences = self._load_climate_preferences()
        self.companion_plants = self._load_companion_planting_data()
        
    def get_crop_basics(self, crop: str) -> Dict[str, Any]:
        """Get basic information about a crop"""
        crop_lower = crop.lower()
        
        if crop_lower not in self.crops:
            return {
                'error': f'Crop "{crop}" not found in database',
                'available_crops': self.get_available_crops(),
                'suggestion': self._suggest_similar_crops(crop)
            }
        
        crop_data = self.crops[crop_lower]
        
        return {
            'name': crop,
            'scientific_name': crop_data['scientific_name'],
            'family': crop_data['family'],
            'category': crop_data['category'],
            'description': crop_data['description'],
            'varieties': [var.name for var in crop_data['varieties']],
            'growing_season': crop_data['growing_season'],
            'water_requirements': crop_data['water_requirements'],
            'soil_preferences': crop_data['soil_preferences'],
            'temperature_range': crop_data['temperature_range'],
            'main_uses': crop_data['main_uses']
        }
    
    def get_variety_details(self, crop: str, variety_name: str = None) -> Dict[str, Any]:
        """Get detailed information about crop varieties"""
        crop_lower = crop.lower()
        
        if crop_lower not in self.crops:
            return {'error': f'Crop "{crop}" not found'}
        
        varieties = self.crops[crop_lower]['varieties']
        
        if variety_name:
            # Find specific variety
            variety = next((v for v in varieties if v.name.lower() == variety_name.lower()), None)
            if variety:
                return {
                    'crop': crop,
                    'variety': variety.name,
                    'maturity_days': variety.maturity_days,
                    'yield_potential': variety.yield_potential,
                    'disease_resistance': variety.disease_resistance,
                    'suitable_climate_zones': variety.climate_zones,
                    'special_characteristics': variety.special_characteristics,
                    'recommended_regions': self._get_recommended_regions(crop, variety)
                }
            else:
                return {'error': f'Variety "{variety_name}" not found for {crop}'}
        else:
            # Return all varieties
            return {
                'crop': crop,
                'total_varieties': len(varieties),
                'varieties': [
                    {
                        'name': var.name,
                        'maturity_days': var.maturity_days,
                        'yield_potential': var.yield_potential,
                        'key_features': var.special_characteristics[:2]  # Top 2 features
                    }
                    for var in varieties
                ]
            }
    
    def get_nutritional_requirements(self, crop: str) -> Dict[str, Any]:
        """Get nutritional requirements for a crop"""
        crop_lower = crop.lower()
        
        requirements = self.nutritional_requirements.get(crop_lower, {})
        
        if not requirements:
            return {
                'error': f'Nutritional data not available for {crop}',
                'general_advice': 'Apply balanced NPK fertilizer and organic matter'
            }
        
        return {
            'crop': crop,
            'primary_nutrients': requirements['primary'],
            'secondary_nutrients': requirements['secondary'],
            'micronutrients': requirements['micronutrients'],
            'soil_ph_range': requirements['ph_range'],
            'organic_matter_needs': requirements['organic_matter'],
            'fertilizer_timing': requirements['timing']
        }
    
    def get_climate_suitability(self, crop: str, region: str = None) -> Dict[str, Any]:
        """Assess climate suitability for a crop"""
        crop_lower = crop.lower()
        
        if crop_lower not in self.climate_preferences:
            return {'error': f'Climate data not available for {crop}'}
        
        climate_data = self.climate_preferences[crop_lower]
        suitability = {
            'crop': crop,
            'optimal_conditions': climate_data['optimal'],
            'tolerable_range': climate_data['tolerable'],
            'critical_factors': climate_data['critical_factors'],
            'seasonal_considerations': climate_data['seasonal_notes']
        }
        
        if region:
            suitability['region_assessment'] = self._assess_regional_suitability(
                crop_lower, region, climate_data
            )
        
        return suitability
    
    def get_companion_plants(self, crop: str) -> Dict[str, Any]:
        """Get companion planting information"""
        crop_lower = crop.lower()
        companions = self.companion_plants.get(crop_lower, {})
        
        return {
            'crop': crop,
            'beneficial_companions': companions.get('beneficial', []),
            'avoid_planting_with': companions.get('avoid', []),
            'companion_benefits': companions.get('benefits', {}),
            'intercropping_systems': companions.get('systems', [])
        }
    
    def get_available_crops(self) -> List[str]:
        """Get list of all available crops in database"""
        return sorted(list(self.crops.keys()))
    
    def search_crops_by_category(self, category: str) -> List[str]:
        """Search crops by category"""
        category_crops = []
        
        for crop_name, crop_data in self.crops.items():
            if crop_data['category'].lower() == category.lower():
                category_crops.append(crop_name)
        
        return sorted(category_crops)
    
    def get_crop_categories(self) -> Dict[str, List[str]]:
        """Get crops organized by categories"""
        return self.crop_categories
    
    def _initialize_crop_database(self) -> Dict[str, Dict]:
        """Initialize comprehensive crop database"""
        return {
            'maize': {
                'scientific_name': 'Zea mays',
                'family': 'Poaceae',
                'category': 'cereals',
                'description': 'Major cereal crop grown throughout Cameroon for food and feed',
                'growing_season': 'March to July (main season), August to December (off-season)',
                'water_requirements': 'Moderate (500-800mm during growing season)',
                'soil_preferences': 'Well-drained loamy soils, pH 6.0-7.0',
                'temperature_range': '20-30°C optimal',
                'main_uses': ['Human food', 'Animal feed', 'Industrial processing'],
                'varieties': [
                    CropVariety(
                        name='IRAD Local Yellow',
                        maturity_days=90,
                        yield_potential='3-5 tons/ha',
                        disease_resistance=['Leaf blight tolerance'],
                        climate_zones=['humid_forest', 'savanna'],
                        special_characteristics=['High vitamin A', 'Good storage quality']
                    ),
                    CropVariety(
                        name='ATP Y2',
                        maturity_days=95,
                        yield_potential='4-6 tons/ha',
                        disease_resistance=['Streak virus resistance'],
                        climate_zones=['all_zones'],
                        special_characteristics=['High yielding', 'Drought tolerant']
                    ),
                    CropVariety(
                        name='CMS 8704',
                        maturity_days=110,
                        yield_potential='5-7 tons/ha',
                        disease_resistance=['Multiple disease resistance'],
                        climate_zones=['humid_forest'],
                        special_characteristics=['Large grain size', 'Good processing quality']
                    )
                ]
            },
            'cassava': {
                'scientific_name': 'Manihot esculenta',
                'family': 'Euphorbiaceae',
                'category': 'root_tubers',
                'description': 'Primary food security crop, drought tolerant root vegetable',
                'growing_season': 'Year-round planting possible, 8-18 months to harvest',
                'water_requirements': 'Low to moderate (300-500mm annually)',
                'soil_preferences': 'Well-drained soils, tolerates poor fertility, pH 5.5-7.0',
                'temperature_range': '25-35°C optimal',
                'main_uses': ['Fresh consumption', 'Flour production', 'Starch extraction', 'Animal feed'],
                'varieties': [
                    CropVariety(
                        name='TMS 4(2)1425',
                        maturity_days=360,
                        yield_potential='25-35 tons/ha',
                        disease_resistance=['Mosaic virus resistance', 'Bacterial blight tolerance'],
                        climate_zones=['all_zones'],
                        special_characteristics=['High starch content', 'Good cooking quality']
                    ),
                    CropVariety(
                        name='Local Red',
                        maturity_days=450,
                        yield_potential='20-30 tons/ha',
                        disease_resistance=['Moderate disease tolerance'],
                        climate_zones=['humid_forest', 'transition'],
                        special_characteristics=['Traditional variety', 'Excellent taste']
                    )
                ]
            },
            'tomatoes': {
                'scientific_name': 'Solanum lycopersicum',
                'family': 'Solanaceae',
                'category': 'vegetables',
                'description': 'Important vegetable crop for fresh market and processing',
                'growing_season': 'Dry season (November to March) for open field, year-round under protection',
                'water_requirements': 'High (600-800mm, evenly distributed)',
                'soil_preferences': 'Rich, well-drained soils with high organic matter, pH 6.0-6.8',
                'temperature_range': '18-25°C optimal for fruit set',
                'main_uses': ['Fresh consumption', 'Processing', 'Sauce production'],
                'varieties': [
                    CropVariety(
                        name='Roma VF',
                        maturity_days=85,
                        yield_potential='30-50 tons/ha',
                        disease_resistance=['Fusarium wilt', 'Verticillium wilt'],
                        climate_zones=['highland', 'transition'],
                        special_characteristics=['Processing type', 'Determinate growth']
                    ),
                    CropVariety(
                        name='Mongal F1',
                        maturity_days=75,
                        yield_potential='40-60 tons/ha',
                        disease_resistance=['Multiple virus resistance'],
                        climate_zones=['highland'],
                        special_characteristics=['Hybrid vigor', 'Uniform ripening']
                    )
                ]
            },
            'cocoa': {
                'scientific_name': 'Theobroma cacao',
                'family': 'Malvaceae',
                'category': 'cash_crops',
                'description': 'Major export cash crop, requires shade and high humidity',
                'growing_season': 'Year-round cultivation, two harvest seasons',
                'water_requirements': 'High (1500-2000mm annually, well distributed)',
                'soil_preferences': 'Deep, well-drained fertile soils, pH 6.0-7.0',
                'temperature_range': '21-32°C with minimal variation',
                'main_uses': ['Export commodity', 'Chocolate production', 'Local beverages'],
                'varieties': [
                    CropVariety(
                        name='Trinitario',
                        maturity_days=1825,  # 5 years to full production
                        yield_potential='800-1200 kg/ha dried beans',
                        disease_resistance=['Black pod tolerance'],
                        climate_zones=['humid_forest'],
                        special_characteristics=['High quality beans', 'Good flavor']
                    ),
                    CropVariety(
                        name='Amelonado',
                        maturity_days=1460,  # 4 years to production
                        yield_potential='600-1000 kg/ha dried beans',
                        disease_resistance=['Swollen shoot tolerance'],
                        climate_zones=['humid_forest'],
                        special_characteristics=['Local variety', 'Hardy']
                    )
                ]
            },
            'beans': {
                'scientific_name': 'Phaseolus vulgaris',
                'family': 'Fabaceae',
                'category': 'legumes',
                'description': 'Important protein crop and soil fertility builder',
                'growing_season': 'Two seasons - March to June, August to November',
                'water_requirements': 'Moderate (400-600mm during growing season)',
                'soil_preferences': 'Well-drained fertile soils, pH 6.0-7.0',
                'temperature_range': '18-28°C optimal',
                'main_uses': ['Fresh consumption', 'Dried beans', 'Soil improvement'],
                'varieties': [
                    CropVariety(
                        name='Red Kidney',
                        maturity_days=90,
                        yield_potential='2-3 tons/ha',
                        disease_resistance=['Anthracnose tolerance'],
                        climate_zones=['highland', 'transition'],
                        special_characteristics=['High protein', 'Market preferred']
                    ),
                    CropVariety(
                        name='Black Bean',
                        maturity_days=85,
                        yield_potential='1.5-2.5 tons/ha',
                        disease_resistance=['Root rot tolerance'],
                        climate_zones=['all_zones'],
                        special_characteristics=['Fast cooking', 'Drought tolerant']
                    )
                ]
            }
        }
    
    def _define_crop_categories(self) -> Dict[str, List[str]]:
        """Define crop categories"""
        categories = {}
        
        for crop_name, crop_data in self.crops.items():
            category = crop_data['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(crop_name)
        
        return categories
    
    def _load_nutritional_requirements(self) -> Dict[str, Dict]:
        """Load nutritional requirements for each crop"""
        return {
            'maize': {
                'primary': {'N': 'High', 'P': 'Medium', 'K': 'Medium'},
                'secondary': {'Ca': 'Low', 'Mg': 'Low', 'S': 'Low'},
                'micronutrients': ['Zn', 'B', 'Fe'],
                'ph_range': '6.0-7.0',
                'organic_matter': 'Medium requirements',
                'timing': 'Split application - basal + top dressing'
            },
            'tomatoes': {
                'primary': {'N': 'High', 'P': 'High', 'K': 'Very High'},
                'secondary': {'Ca': 'High', 'Mg': 'Medium', 'S': 'Medium'},
                'micronutrients': ['B', 'Zn', 'Mn'],
                'ph_range': '6.0-6.8',
                'organic_matter': 'High requirements',
                'timing': 'Continuous feeding during growth'
            },
            'cassava': {
                'primary': {'N': 'Low', 'P': 'Medium', 'K': 'High'},
                'secondary': {'Ca': 'Low', 'Mg': 'Low', 'S': 'Low'},
                'micronutrients': ['Zn', 'Mn'],
                'ph_range': '5.5-7.0',
                'organic_matter': 'Low to medium',
                'timing': 'Single application at 2-3 months'
            }
        }
    
    def _load_climate_preferences(self) -> Dict[str, Dict]:
        """Load climate preference data"""
        return {
            'maize': {
                'optimal': {
                    'temperature': '22-30°C',
                    'rainfall': '500-800mm',
                    'humidity': '50-70%'
                },
                'tolerable': {
                    'temperature': '18-35°C',
                    'rainfall': '400-1000mm',
                    'humidity': '40-80%'
                },
                'critical_factors': ['Avoid waterlogging', 'Needs warm germination'],
                'seasonal_notes': 'Plant with reliable rainfall onset'
            },
            'tomatoes': {
                'optimal': {
                    'temperature': '20-25°C',
                    'rainfall': '600-800mm',
                    'humidity': '60-70%'
                },
                'tolerable': {
                    'temperature': '15-30°C',
                    'rainfall': '500-1000mm',
                    'humidity': '50-80%'
                },
                'critical_factors': ['Avoid extreme heat during flowering', 'Good drainage essential'],
                'seasonal_notes': 'Best in dry season or under protection'
            }
        }
    
    def _load_companion_planting_data(self) -> Dict[str, Dict]:
        """Load companion planting information"""
        return {
            'maize': {
                'beneficial': ['beans', 'squash', 'pumpkin'],
                'avoid': ['tomatoes', 'fennel'],
                'benefits': {
                    'beans': 'Nitrogen fixation for maize',
                    'squash': 'Ground cover and pest deterrent'
                },
                'systems': ['Three sisters (maize-beans-squash)']
            },
            'tomatoes': {
                'beneficial': ['basil', 'pepper', 'carrots'],
                'avoid': ['maize', 'fennel', 'walnut'],
                'benefits': {
                    'basil': 'Pest deterrent and flavor enhancement',
                    'pepper': 'Similar growing requirements'
                },
                'systems': ['Solanaceae family grouping']
            }
        }
    
    def _suggest_similar_crops(self, crop: str) -> List[str]:
        """Suggest similar crops based on name similarity"""
        crop_lower = crop.lower()
        available = list(self.crops.keys())
        
        # Simple similarity matching
        suggestions = []
        for available_crop in available:
            if (crop_lower in available_crop or 
                available_crop in crop_lower or
                self._calculate_similarity(crop_lower, available_crop) > 0.6):
                suggestions.append(available_crop)
        
        return suggestions[:3]  # Top 3 suggestions
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple string similarity"""
        shorter = str1 if len(str1) <= len(str2) else str2
        longer = str2 if len(str1) <= len(str2) else str1
        
        if len(longer) == 0:
            return 1.0
        
        matches = sum(c1 == c2 for c1, c2 in zip(shorter, longer))
        return matches / len(longer)
    
    def _assess_regional_suitability(self, crop: str, region: str, climate_data: Dict) -> Dict:
        """Assess how suitable a crop is for a specific region"""
        # Regional climate characteristics (simplified)
        regional_climate = {
            'centre': {'temp': 25, 'rainfall': 1600, 'humidity': 80},
            'littoral': {'temp': 26, 'rainfall': 3000, 'humidity': 85},
            'west': {'temp': 22, 'rainfall': 2000, 'humidity': 75},
            'north': {'temp': 28, 'rainfall': 900, 'humidity': 45},
            'far_north': {'temp': 30, 'rainfall': 500, 'humidity': 35}
        }
        
        region_data = regional_climate.get(region.lower(), {'temp': 25, 'rainfall': 1200, 'humidity': 65})
        optimal = climate_data['optimal']
        
        # Simple suitability assessment
        temp_match = self._assess_parameter_match(region_data['temp'], optimal['temperature'])
        rainfall_match = self._assess_parameter_match(region_data['rainfall'], optimal['rainfall'])
        
        overall_score = (temp_match + rainfall_match) / 2
        
        if overall_score > 0.8:
            suitability = 'excellent'
        elif overall_score > 0.6:
            suitability = 'good'
        elif overall_score > 0.4:
            suitability = 'moderate'
        else:
            suitability = 'challenging'
        
        return {
            'suitability_rating': suitability,
            'score': round(overall_score, 2),
            'limiting_factors': self._identify_limiting_factors(region_data, optimal)
        }
    
    def _assess_parameter_match(self, actual_value: float, optimal_range: str) -> float:
        """Assess how well actual value matches optimal range"""
        # Parse range string like "20-25°C" or "500-800mm"
        import re
        numbers = re.findall(r'\d+', optimal_range)
        if len(numbers) >= 2:
            min_val, max_val = float(numbers[0]), float(numbers[1])
            if min_val <= actual_value <= max_val:
                return 1.0
            elif actual_value < min_val:
                return max(0, 1 - (min_val - actual_value) / min_val)
            else:
                return max(0, 1 - (actual_value - max_val) / max_val)
        return 0.5  # Default if can't parse
    
    def _identify_limiting_factors(self, region_data: Dict, optimal: Dict) -> List[str]:
        """Identify what factors might limit crop success in region"""
        factors = []
        
        # Simplified factor identification
        if region_data['rainfall'] > 2500:
            factors.append('High rainfall may cause waterlogging')
        elif region_data['rainfall'] < 600:
            factors.append('Low rainfall requires irrigation')
        
        if region_data['temp'] > 32:
            factors.append('High temperatures may stress crops')
        elif region_data['temp'] < 18:
            factors.append('Cool temperatures may slow growth')
        
        return factors
    
    def _get_recommended_regions(self, crop: str, variety: CropVariety) -> List[str]:
        """Get recommended regions for a crop variety"""
        # Map climate zones to regions
        zone_regions = {
            'humid_forest': ['centre', 'south', 'east'],
            'savanna': ['adamawa', 'north'],
            'highland': ['west', 'northwest'],
            'coastal': ['littoral', 'southwest'],
            'all_zones': ['centre', 'littoral', 'west', 'northwest', 'southwest', 'east', 'north', 'far_north', 'adamawa', 'south']
        }
        
        recommended = []
        for zone in variety.climate_zones:
            recommended.extend(zone_regions.get(zone, []))
        
        return list(set(recommended))  # Remove duplicates