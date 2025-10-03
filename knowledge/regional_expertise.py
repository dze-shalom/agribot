"""
Regional Expertise Module
Location: agribot/knowledge/regional_expertise.py

Specialized knowledge about agricultural practices, crop suitability,
and farming conditions specific to each of Cameroon's 10 regions.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RegionalProfile:
    """Data structure for regional agricultural profile"""
    name: str
    climate_zone: str
    rainfall_pattern: str
    soil_types: List[str]
    major_crops: List[str]
    challenges: List[str]
    opportunities: List[str]
    market_access: str

class RegionalExpertise:
    """Regional agricultural expertise for all Cameroon regions"""
    
    def __init__(self):
        self.regions = self._initialize_regional_data()
        self.seasonal_calendars = self._load_seasonal_calendars()
        self.regional_practices = self._load_traditional_practices()
        self.market_information = self._load_market_data()
        self.extension_networks = self._load_extension_contacts()
    
    def get_regional_profile(self, region: str) -> Dict[str, Any]:
        """Get comprehensive regional agricultural profile"""
        region_lower = region.lower()
        
        if region_lower not in self.regions:
            return {
                'error': f'Region "{region}" not found',
                'available_regions': list(self.regions.keys()),
                'suggestion': 'Please check region name spelling'
            }
        
        profile = self.regions[region_lower]
        
        return {
            'region_name': profile.name,
            'climate_characteristics': {
                'zone': profile.climate_zone,
                'rainfall_pattern': profile.rainfall_pattern,
                'seasonal_variations': self._get_seasonal_variations(region_lower)
            },
            'soil_information': {
                'dominant_types': profile.soil_types,
                'fertility_status': self._assess_soil_fertility(region_lower),
                'management_needs': self._get_soil_management_advice(region_lower)
            },
            'crop_portfolio': {
                'major_crops': profile.major_crops,
                'emerging_opportunities': profile.opportunities,
                'crop_diversification_potential': self._assess_diversification_potential(region_lower)
            },
            'challenges_and_solutions': {
                'main_challenges': profile.challenges,
                'mitigation_strategies': self._get_mitigation_strategies(region_lower),
                'success_stories': self._get_regional_success_stories(region_lower)
            },
            'market_connectivity': {
                'access_rating': profile.market_access,
                'main_markets': self._get_main_markets(region_lower),
                'value_chain_opportunities': self._get_value_chain_info(region_lower)
            }
        }
    
    def get_crop_suitability(self, crop: str, region: str = None) -> Dict[str, Any]:
        """Assess crop suitability across regions"""
        if region:
            # Single region assessment
            return self._assess_single_region_suitability(crop, region)
        else:
            # Multi-region suitability ranking
            return self._rank_regions_for_crop(crop)
    
    def get_seasonal_calendar(self, region: str, crop: str = None) -> Dict[str, Any]:
        """Get seasonal farming calendar for region"""
        region_lower = region.lower()
        
        if region_lower not in self.seasonal_calendars:
            return {'error': f'Calendar data not available for {region}'}
        
        calendar = self.seasonal_calendars[region_lower]
        
        if crop:
            crop_calendar = calendar.get('crops', {}).get(crop.lower(), {})
            if crop_calendar:
                return {
                    'region': region,
                    'crop': crop,
                    'planting_windows': crop_calendar['planting'],
                    'management_schedule': crop_calendar['care'],
                    'harvest_periods': crop_calendar['harvest'],
                    'seasonal_risks': crop_calendar.get('risks', []),
                    'best_practices': crop_calendar.get('practices', [])
                }
            else:
                return {'error': f'Calendar data not available for {crop} in {region}'}
        else:
            return {
                'region': region,
                'general_calendar': calendar['general'],
                'rainfall_seasons': calendar['rainfall'],
                'temperature_patterns': calendar['temperature'],
                'critical_periods': calendar['critical_periods']
            }
    
    def get_traditional_practices(self, region: str, practice_type: str = None) -> Dict[str, Any]:
        """Get traditional agricultural practices for region"""
        region_lower = region.lower()
        
        if region_lower not in self.regional_practices:
            return {'error': f'Traditional practice data not available for {region}'}
        
        practices = self.regional_practices[region_lower]
        
        if practice_type:
            specific_practice = practices.get(practice_type, {})
            return {
                'region': region,
                'practice_type': practice_type,
                'details': specific_practice,
                'modern_adaptations': self._suggest_modern_adaptations(specific_practice)
            }
        else:
            return {
                'region': region,
                'available_practices': list(practices.keys()),
                'summary': {practice: info.get('description', '') for practice, info in practices.items()}
            }
    
    def get_extension_support(self, region: str) -> Dict[str, Any]:
        """Get agricultural extension support information"""
        region_lower = region.lower()
        
        extension_info = self.extension_networks.get(region_lower, {})
        
        return {
            'region': region,
            'extension_offices': extension_info.get('offices', []),
            'key_contacts': extension_info.get('contacts', []),
            'support_services': extension_info.get('services', []),
            'farmer_organizations': extension_info.get('organizations', []),
            'training_programs': extension_info.get('programs', [])
        }
    
    def compare_regions(self, regions: List[str], criteria: str = 'overall') -> Dict[str, Any]:
        """Compare multiple regions based on specified criteria"""
        comparison = {
            'regions_compared': regions,
            'criteria': criteria,
            'comparison_results': {},
            'recommendations': {}
        }
        
        for region in regions:
            if region.lower() in self.regions:
                profile = self.regions[region.lower()]
                
                if criteria == 'market_access':
                    score = self._score_market_access(profile.market_access)
                elif criteria == 'crop_diversity':
                    score = len(profile.major_crops)
                elif criteria == 'climate_stability':
                    score = self._score_climate_stability(region.lower())
                else:  # overall
                    score = self._calculate_overall_score(profile)
                
                comparison['comparison_results'][region] = {
                    'score': score,
                    'strengths': profile.opportunities,
                    'challenges': profile.challenges
                }
        
        # Generate recommendations
        if comparison['comparison_results']:
            best_region = max(comparison['comparison_results'], 
                            key=lambda x: comparison['comparison_results'][x]['score'])
            comparison['recommendations']['top_choice'] = best_region
            comparison['recommendations']['reasoning'] = f"Highest score in {criteria}"
        
        return comparison
    
    def _initialize_regional_data(self) -> Dict[str, RegionalProfile]:
        """Initialize comprehensive regional data"""
        return {
            'centre': RegionalProfile(
                name='Centre Region',
                climate_zone='Humid Tropical Forest',
                rainfall_pattern='Bimodal (March-June, September-November)',
                soil_types=['Ferralsols', 'Acrisols', 'Gleysols'],
                major_crops=['cassava', 'plantain', 'maize', 'cocoa', 'yam', 'groundnuts'],
                challenges=['Soil acidity', 'Deforestation pressure', 'Urban encroachment'],
                opportunities=['Peri-urban agriculture', 'Value addition', 'Organic farming'],
                market_access='excellent'
            ),
            'littoral': RegionalProfile(
                name='Littoral Region',
                climate_zone='Coastal Humid Tropical',
                rainfall_pattern='Unimodal (April-November)',
                soil_types=['Fluvisols', 'Gleysols', 'Arenosols'],
                major_crops=['banana', 'oil_palm', 'pineapple', 'vegetables', 'rice'],
                challenges=['Flooding', 'Saltwater intrusion', 'Land pressure'],
                opportunities=['Export crops', 'Aquaculture', 'Processing industries'],
                market_access='excellent'
            ),
            'west': RegionalProfile(
                name='West Region',
                climate_zone='Highland Tropical',
                rainfall_pattern='Unimodal (May-October)',
                soil_types=['Andosols', 'Nitisols', 'Cambisols'],
                major_crops=['coffee', 'beans', 'irish_potato', 'maize', 'vegetables'],
                challenges=['Soil erosion', 'Climate variability', 'Market fluctuations'],
                opportunities=['High-value crops', 'Coffee quality improvement', 'Agritourism'],
                market_access='good'
            ),
            'northwest': RegionalProfile(
                name='Northwest Region',
                climate_zone='Highland Tropical',
                rainfall_pattern='Unimodal (May-October)',
                soil_types=['Andosols', 'Lixisols', 'Cambisols'],
                major_crops=['beans', 'maize', 'irish_potato', 'vegetables', 'coffee'],
                challenges=['Political instability', 'Market access', 'Soil degradation'],
                opportunities=['Vegetable production', 'Seed multiplication', 'Cooperative farming'],
                market_access='moderate'
            ),
            'southwest': RegionalProfile(
                name='Southwest Region',
                climate_zone='Coastal Mountain Forest',
                rainfall_pattern='Long rainy season (March-November)',
                soil_types=['Andosols', 'Acrisols', 'Gleysols'],
                major_crops=['oil_palm', 'cocoa', 'banana', 'rubber', 'pepper'],
                challenges=['Excessive rainfall', 'Political instability', 'Infrastructure'],
                opportunities=['Industrial crops', 'Spices', 'Eco-friendly agriculture'],
                market_access='moderate'
            ),
            'east': RegionalProfile(
                name='East Region',
                climate_zone='Congo Basin Forest',
                rainfall_pattern='Bimodal with long rainy season',
                soil_types=['Ferralsols', 'Acrisols', 'Gleysols'],
                major_crops=['cassava', 'plantain', 'cocoa', 'coffee', 'maize'],
                challenges=['Poor infrastructure', 'Limited market access', 'Forest pressure'],
                opportunities=['Sustainable forestry', 'Non-timber products', 'Eco-tourism'],
                market_access='limited'
            ),
            'north': RegionalProfile(
                name='North Region',
                climate_zone='Sudan Savanna',
                rainfall_pattern='Unimodal (May-September)',
                soil_types=['Lixisols', 'Luvisols', 'Vertisols'],
                major_crops=['cotton', 'millet', 'sorghum', 'groundnuts', 'rice'],
                challenges=['Drought risk', 'Soil fertility decline', 'Pest pressure'],
                opportunities=['Irrigation development', 'Livestock integration', 'Grain storage'],
                market_access='moderate'
            ),
            'far_north': RegionalProfile(
                name='Far North Region',
                climate_zone='Sahel',
                rainfall_pattern='Short unimodal (June-September)',
                soil_types=['Vertisols', 'Arenosols', 'Regosols'],
                major_crops=['millet', 'sorghum', 'cotton', 'onions', 'pepper'],
                challenges=['Water scarcity', 'Desertification', 'Climate extremes'],
                opportunities=['Irrigation agriculture', 'Drought-resistant varieties', 'Livestock'],
                market_access='limited'
            ),
            'adamawa': RegionalProfile(
                name='Adamawa Region',
                climate_zone='Guinea Savanna Highland',
                rainfall_pattern='Unimodal (April-October)',
                soil_types=['Lixisols', 'Ferralsols', 'Planosols'],
                major_crops=['maize', 'beans', 'groundnuts', 'irish_potato', 'vegetables'],
                challenges=['Seasonal water stress', 'Cattle-farmer conflicts', 'Market distance'],
                opportunities=['Livestock-crop integration', 'Seed production', 'Food processing'],
                market_access='moderate'
            ),
            'south': RegionalProfile(
                name='South Region',
                climate_zone='Equatorial Forest',
                rainfall_pattern='Bimodal with short dry season',
                soil_types=['Ferralsols', 'Acrisols', 'Histosols'],
                major_crops=['cocoa', 'cassava', 'plantain', 'oil_palm', 'coffee'],
                challenges=['Transport costs', 'Processing facilities', 'Youth migration'],
                opportunities=['Sustainable cocoa', 'Agroforestry', 'Carbon credits'],
                market_access='moderate'
            )
        }
    
    def _load_seasonal_calendars(self) -> Dict[str, Dict]:
        """Load seasonal farming calendars"""
        return {
            'centre': {
                'general': {
                    'main_season': 'March-July',
                    'off_season': 'August-December',
                    'dry_season': 'December-February'
                },
                'rainfall': {
                    'first_rains': 'March-June',
                    'short_dry': 'July-August',
                    'second_rains': 'September-November'
                },
                'temperature': {
                    'hot_period': 'February-April',
                    'cool_period': 'July-August',
                    'average_range': '22-28°C'
                },
                'critical_periods': [
                    'Late February: Land preparation',
                    'March: Main season planting',
                    'July-August: Pest management critical',
                    'October-November: Major harvest'
                ],
                'crops': {
                    'maize': {
                        'planting': ['March-April', 'August-September'],
                        'care': ['Weeding at 3 and 6 weeks', 'Fertilizer at 4 weeks'],
                        'harvest': ['July', 'December'],
                        'risks': ['Armyworm in young crops', 'Storage pests']
                    },
                    'cassava': {
                        'planting': ['March-May', 'September-October'],
                        'care': ['Monthly weeding first 4 months', 'Hilling at 3 months'],
                        'harvest': ['8-12 months after planting'],
                        'risks': ['Mosaic virus', 'Cassava mealybug']
                    }
                }
            },
            'north': {
                'general': {
                    'rainy_season': 'May-September',
                    'dry_season': 'October-April',
                    'harmattan': 'December-February'
                },
                'rainfall': {
                    'onset': 'May',
                    'peak': 'July-August',
                    'cessation': 'September'
                },
                'temperature': {
                    'hot_season': 'March-May',
                    'cool_season': 'December-January',
                    'average_range': '25-35°C'
                },
                'critical_periods': [
                    'April: Land preparation',
                    'May-June: Planting window',
                    'July-August: Weeding critical',
                    'September-October: Harvest season'
                ],
                'crops': {
                    'millet': {
                        'planting': ['May-June'],
                        'care': ['First weeding at 3 weeks', 'Thinning at 4 weeks'],
                        'harvest': ['September-October'],
                        'risks': ['Birds at maturity', 'Drought stress']
                    },
                    'cotton': {
                        'planting': ['May-June'],
                        'care': ['Regular weeding', 'Pest monitoring'],
                        'harvest': ['October-December'],
                        'risks': ['Bollworm', 'Late season rains']
                    }
                }
            }
        }
    
    def _load_traditional_practices(self) -> Dict[str, Dict]:
        """Load traditional agricultural practices"""
        return {
            'centre': {
                'slash_and_burn': {
                    'description': 'Traditional forest clearing and burning',
                    'process': ['Clear forest', 'Dry for 2-3 months', 'Burn', 'Plant crops'],
                    'duration': '2-3 years cultivation, 10-15 years fallow',
                    'crops': ['cassava', 'plantain', 'cocoa'],
                    'sustainability_issues': ['Deforestation', 'Soil degradation']
                },
                'intercropping': {
                    'description': 'Mixed cropping system',
                    'combinations': ['cassava-maize-groundnuts', 'cocoa-plantain-yam'],
                    'benefits': ['Risk reduction', 'Soil protection', 'Multiple harvests'],
                    'management': ['Sequential planting', 'Careful crop selection']
                },
                'mulching': {
                    'description': 'Use of organic materials for soil cover',
                    'materials': ['Palm fronds', 'Grass', 'Crop residues'],
                    'benefits': ['Moisture retention', 'Weed suppression', 'Soil improvement'],
                    'application': 'Apply 5-10cm thick around plants'
                }
            },
            'north': {
                'crop_rotation': {
                    'description': 'Systematic rotation of crops',
                    'sequence': ['Cotton-Millet-Groundnuts-Fallow'],
                    'duration': '4-year cycle',
                    'benefits': ['Pest control', 'Soil fertility', 'Risk management']
                },
                'water_harvesting': {
                    'description': 'Traditional rainwater collection',
                    'methods': ['Contour bunds', 'Stone lines', 'Planting basins'],
                    'effectiveness': 'Increases water availability by 30-40%'
                },
                'livestock_integration': {
                    'description': 'Cattle-crop integration',
                    'practice': 'Cattle graze crop residues, provide manure',
                    'benefits': ['Nutrient cycling', 'Income diversification'],
                    'challenges': ['Grazing conflicts', 'Crop damage']
                }
            }
        }
    
    def _load_market_data(self) -> Dict[str, Dict]:
        """Load regional market information"""
        return {
            'centre': {
                'major_markets': ['Mfoundi Central Market', 'Mokolo Market', 'Etoudi'],
                'export_facilities': ['Port of Douala access', 'Airport facilities'],
                'price_trends': 'Stable with seasonal variations',
                'value_chains': ['Processing facilities', 'Cold storage', 'Transport networks']
            },
            'littoral': {
                'major_markets': ['New Bell Market', 'Port of Douala'],
                'export_facilities': ['International port', 'Airport'],
                'price_trends': 'Export crop prices volatile',
                'value_chains': ['Banana plantations', 'Palm oil mills', 'Pineapple processing']
            }
        }
    
    def _load_extension_contacts(self) -> Dict[str, Dict]:
        """Load extension service contacts"""
        return {
            'centre': {
                'offices': ['MINADER Yaoundé', 'IRAD Nkolbisson', 'World Agroforestry Centre'],
                'contacts': ['Regional Delegate MINADER', 'IRAD Research Stations'],
                'services': ['Technical training', 'Input supply', 'Market information'],
                'organizations': ['UCCAO', 'PLANOPAC', 'Cooperative societies'],
                'programs': ['PIDMA', 'ACEFA', 'Youth in Agriculture']
            },
            'north': {
                'offices': ['MINADER Garoua', 'IRAD Garoua', 'SODECOTON'],
                'contacts': ['Regional Extension Officers', 'Cotton Development Company'],
                'services': ['Input credit', 'Technical advice', 'Equipment rental'],
                'organizations': ['Cotton cooperatives', 'Livestock associations'],
                'programs': ['Cotton development', 'Irrigation support']
            }
        }
    
    def _assess_single_region_suitability(self, crop: str, region: str) -> Dict[str, Any]:
        """Assess crop suitability for a specific region"""
        region_lower = region.lower()
        
        if region_lower not in self.regions:
            return {'error': f'Region {region} not found'}
        
        profile = self.regions[region_lower]
        
        # Check if crop is already grown in region
        is_major_crop = crop.lower() in [c.lower() for c in profile.major_crops]
        
        # Climate suitability assessment
        climate_match = self._assess_climate_match(crop, profile.climate_zone)
        
        # Soil suitability
        soil_match = self._assess_soil_suitability(crop, profile.soil_types)
        
        # Market potential
        market_score = self._assess_market_potential(crop, region_lower)
        
        overall_score = (climate_match + soil_match + market_score) / 3
        
        if overall_score > 0.8:
            suitability = 'highly_suitable'
        elif overall_score > 0.6:
            suitability = 'suitable'
        elif overall_score > 0.4:
            suitability = 'moderately_suitable'
        else:
            suitability = 'challenging'
        
        return {
            'crop': crop,
            'region': region,
            'suitability_rating': suitability,
            'overall_score': round(overall_score, 2),
            'currently_grown': is_major_crop,
            'detailed_assessment': {
                'climate_suitability': climate_match,
                'soil_suitability': soil_match,
                'market_potential': market_score
            },
            'recommendations': self._generate_suitability_recommendations(
                crop, region_lower, suitability, is_major_crop
            ),
            'success_factors': self._identify_success_factors(crop, region_lower),
            'potential_challenges': self._identify_regional_challenges(crop, region_lower)
        }
    
    def _rank_regions_for_crop(self, crop: str) -> Dict[str, Any]:
        """Rank all regions by suitability for a specific crop"""
        rankings = []
        
        for region_name, profile in self.regions.items():
            climate_match = self._assess_climate_match(crop, profile.climate_zone)
            soil_match = self._assess_soil_suitability(crop, profile.soil_types)
            market_score = self._assess_market_potential(crop, region_name)
            
            overall_score = (climate_match + soil_match + market_score) / 3
            
            rankings.append({
                'region': region_name,
                'score': round(overall_score, 2),
                'climate_score': round(climate_match, 2),
                'soil_score': round(soil_match, 2),
                'market_score': round(market_score, 2),
                'currently_grown': crop.lower() in [c.lower() for c in profile.major_crops]
            })
        
        # Sort by overall score
        rankings.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'crop': crop,
            'regional_rankings': rankings,
            'top_recommendation': rankings[0]['region'] if rankings else None,
            'established_production_areas': [
                r['region'] for r in rankings if r['currently_grown']
            ],
            'emerging_opportunities': [
                r['region'] for r in rankings[:3] if not r['currently_grown']
            ]
        }
    
    # Helper methods for assessments and calculations
    
    def _assess_climate_match(self, crop: str, climate_zone: str) -> float:
        """Assess how well crop matches climate zone"""
        # Crop-climate suitability matrix
        climate_suitability = {
            'maize': {
                'Humid Tropical Forest': 0.8,
                'Guinea Savanna Highland': 0.9,
                'Sudan Savanna': 0.7,
                'Highland Tropical': 0.8,
                'Coastal Humid Tropical': 0.6
            },
            'cassava': {
                'Humid Tropical Forest': 0.9,
                'Congo Basin Forest': 0.9,
                'Guinea Savanna Highland': 0.7,
                'Sudan Savanna': 0.6,
                'Sahel': 0.4
            },
            'cocoa': {
                'Humid Tropical Forest': 0.9,
                'Congo Basin Forest': 0.9,
                'Coastal Mountain Forest': 0.8,
                'Highland Tropical': 0.3,
                'Sudan Savanna': 0.1
            },
            'cotton': {
                'Sudan Savanna': 0.9,
                'Sahel': 0.8,
                'Guinea Savanna Highland': 0.7,
                'Humid Tropical Forest': 0.3
            }
        }
        
        return climate_suitability.get(crop.lower(), {}).get(climate_zone, 0.5)
    
    def _assess_soil_suitability(self, crop: str, soil_types: List[str]) -> float:
        """Assess soil suitability for crop"""
        # Simplified soil-crop suitability
        soil_preferences = {
            'maize': ['Ferralsols', 'Luvisols', 'Cambisols'],
            'cassava': ['Ferralsols', 'Acrisols', 'Arenosols'],
            'cocoa': ['Ferralsols', 'Nitisols'],
            'cotton': ['Vertisols', 'Luvisols'],
            'beans': ['Andosols', 'Cambisols', 'Nitisols']
        }
        
        preferred_soils = soil_preferences.get(crop.lower(), [])
        if not preferred_soils:
            return 0.5
        
        # Calculate match score
        matches = sum(1 for soil in soil_types if soil in preferred_soils)
        return min(matches / len(preferred_soils), 1.0) if preferred_soils else 0.5
    
    def _assess_market_potential(self, crop: str, region: str) -> float:
        """Assess market potential for crop in region"""
        market_ratings = {
            'centre': 0.9,      # Capital region
            'littoral': 0.9,    # Port city
            'west': 0.7,
            'northwest': 0.5,
            'southwest': 0.5,
            'east': 0.4,
            'north': 0.6,
            'far_north': 0.4,
            'adamawa': 0.6,
            'south': 0.5
        }
        
        # Adjust based on crop type
        if crop.lower() in ['cocoa', 'coffee', 'cotton']:  # Export crops
            if region in ['littoral']:
                return 0.9
            elif region in ['centre']:
                return 0.8
        elif crop.lower() in ['vegetables', 'fruits']:  # Perishables
            if region in ['centre', 'littoral', 'west']:
                return 0.9
        
        return market_ratings.get(region, 0.5)
    
    def _generate_suitability_recommendations(self, crop: str, region: str, 
                                           suitability: str, is_major_crop: bool) -> List[str]:
        """Generate recommendations based on suitability assessment"""
        recommendations = []
        
        if suitability == 'highly_suitable':
            if is_major_crop:
                recommendations.extend([
                    f"{crop.title()} is well-established in {region} - focus on yield optimization",
                    "Consider value addition and quality improvement",
                    "Explore export market opportunities"
                ])
            else:
                recommendations.extend([
                    f"Excellent potential for {crop} production in {region}",
                    "Conduct pilot trials before large-scale adoption",
                    "Connect with successful growers in similar regions"
                ])
        
        elif suitability == 'suitable':
            recommendations.extend([
                f"{crop.title()} can be grown successfully with proper management",
                "Focus on variety selection and optimal practices",
                "Consider risk mitigation strategies"
            ])
        
        elif suitability == 'challenging':
            recommendations.extend([
                f"{crop.title()} production will face significant challenges",
                "Consider more suitable alternatives",
                "If proceeding, invest in protected cultivation or improved varieties"
            ])
        
        return recommendations
    
    def _identify_success_factors(self, crop: str, region: str) -> List[str]:
        """Identify key success factors for crop in region"""
        regional_profile = self.regions.get(region)
        if not regional_profile:
            return []
        
        factors = []
        
        # Climate-based factors
        if 'Forest' in regional_profile.climate_zone:
            factors.extend(['Disease management critical', 'Good drainage essential'])
        elif 'Savanna' in regional_profile.climate_zone:
            factors.extend(['Water management important', 'Soil fertility maintenance'])
        elif 'Highland' in regional_profile.climate_zone:
            factors.extend(['Soil erosion control', 'Temperature management'])
        
        # Market-based factors
        if regional_profile.market_access == 'excellent':
            factors.append('Proximity to markets - focus on quality')
        elif regional_profile.market_access == 'limited':
            factors.append('Processing and storage critical due to market distance')
        
        return factors
    
    def _identify_regional_challenges(self, crop: str, region: str) -> List[str]:
        """Identify potential challenges for crop in region"""
        regional_profile = self.regions.get(region)
        if not regional_profile:
            return []
        
        challenges = regional_profile.challenges.copy()
        
        # Add crop-specific challenges
        if crop.lower() in ['tomatoes', 'vegetables'] and 'humid' in regional_profile.climate_zone.lower():
            challenges.append('High disease pressure in humid conditions')
        
        if crop.lower() in ['maize', 'cotton'] and 'sahel' in regional_profile.climate_zone.lower():
            challenges.append('Water stress during critical growth periods')
        
        return challenges
    
    def _suggest_modern_adaptations(self, traditional_practice: Dict) -> List[str]:
        """Suggest modern adaptations of traditional practices"""
        practice_type = traditional_practice.get('description', '').lower()
        
        adaptations = []
        
        if 'slash and burn' in practice_type:
            adaptations.extend([
                'Reduce burning - use improved fallow with legumes',
                'Implement agroforestry systems',
                'Use minimal tillage techniques'
            ])
        elif 'intercropping' in practice_type:
            adaptations.extend([
                'Optimize plant spacing for mechanization',
                'Use compatible crop varieties',
                'Apply precision fertilizer application'
            ])
        elif 'water harvesting' in practice_type:
            adaptations.extend([
                'Install lined ponds for water storage',
                'Use drip irrigation systems',
                'Implement soil moisture monitoring'
            ])
        
        return adaptations
    
    def _get_seasonal_variations(self, region: str) -> Dict[str, str]:
        """Get seasonal climate variations"""
        variations = {
            'centre': 'Two rainy seasons with short dry period',
            'littoral': 'Long rainy season with short dry season',
            'north': 'Single rainy season with long dry period',
            'far_north': 'Very short rainy season with extended dry period'
        }
        return {'pattern': variations.get(region, 'Variable seasonal pattern')}
    
    def _assess_soil_fertility(self, region: str) -> str:
        """Assess general soil fertility status"""
        fertility_status = {
            'centre': 'Moderate - acidic soils need liming',
            'west': 'Good - volcanic soils naturally fertile',
            'north': 'Variable - some fertile valleys',
            'far_north': 'Low - sandy soils need organic matter'
        }
        return fertility_status.get(region, 'Variable fertility status')
    
    def _get_soil_management_advice(self, region: str) -> List[str]:
        """Get soil management advice for region"""
        advice = {
            'centre': ['Apply lime to reduce acidity', 'Use organic matter', 'Practice conservation tillage'],
            'west': ['Control erosion on slopes', 'Maintain organic matter', 'Use contour farming'],
            'north': ['Build organic matter', 'Use crop rotation', 'Apply phosphorus fertilizers'],
            'far_north': ['Sand dune stabilization', 'Water conservation', 'Organic matter critical']
        }
        return advice.get(region, ['Conduct soil testing', 'Use appropriate fertilizers'])