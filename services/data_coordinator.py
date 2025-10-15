"""
Data Coordinator Service
Location: agribot/services/data_coordinator.py

Orchestrates data retrieval from multiple external services (weather, FAO, NASA)
and combines them into comprehensive agricultural insights for farmers.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from services.weather.openweather_client import OpenWeatherClient
from services.weather.weather_analyzer import WeatherAnalyzer
from services.agricultural_data.fao_client import FAOClient
from services.agricultural_data.nasa_client import NASAClient
from services.cache.redis_cache import RedisCache
from config.settings import APIConfig
from utils.exceptions import APIServiceError
import asyncio
import concurrent.futures

class DataCoordinator:
    """Coordinates data from multiple agricultural and weather services"""
    
    def __init__(self, config: APIConfig = None):
        self.config = config or APIConfig()
        
        # Initialize service clients
        self.weather_client = OpenWeatherClient(self.config)
        self.weather_analyzer = WeatherAnalyzer(self.weather_client)
        self.fao_client = FAOClient(self.config)
        self.nasa_client = NASAClient(self.config)
        self.cache = RedisCache()
        
        # Regional crop specializations for Cameroon
        self.regional_specializations = {
            'centre': ['cassava', 'plantain', 'maize', 'cocoa', 'yam'],
            'littoral': ['banana', 'oil_palm', 'pineapple', 'cocoa', 'rubber'],
            'west': ['coffee', 'beans', 'irish_potato', 'vegetables', 'maize'],
            'northwest': ['beans', 'maize', 'vegetables', 'irish_potato', 'coffee'],
            'southwest': ['oil_palm', 'cocoa', 'banana', 'pepper', 'rubber'],
            'east': ['cassava', 'plantain', 'cocoa', 'maize', 'coffee'],
            'north': ['cotton', 'millet', 'sorghum', 'groundnuts', 'rice'],
            'far_north': ['cotton', 'millet', 'onions', 'pepper', 'groundnuts'],
            'adamawa': ['maize', 'beans', 'groundnuts', 'irish_potato', 'rice'],
            'south': ['cocoa', 'cassava', 'plantain', 'oil_palm', 'rubber']
        }
    
    def get_comprehensive_analysis(self, region: str, crop: str = None, 
                                 include_forecast: bool = False) -> Dict[str, Any]:
        """Get comprehensive agricultural analysis combining all data sources"""
        cache_key = f"comprehensive:{region}:{crop}:{include_forecast}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        analysis_start = datetime.now()
        
        try:
            # Gather data from all sources concurrently
            data_results = self._gather_all_data(region, crop, include_forecast)
            
            # Combine and analyze all data
            comprehensive_analysis = {
                'region': region,
                'crop_focus': crop,
                'analysis_timestamp': analysis_start.isoformat(),
                'data_sources': self._get_successful_sources(data_results),
                'current_weather': data_results.get('weather', {}),
                'climate_analysis': data_results.get('nasa_weather', {}),
                'production_data': data_results.get('fao_data', {}),
                'weather_forecast': data_results.get('forecast', {}) if include_forecast else None,
                'integrated_insights': self._generate_integrated_insights(
                    data_results, region, crop
                ),
                'actionable_recommendations': self._generate_actionable_recommendations(
                    data_results, region, crop
                ),
                'risk_assessment': self._assess_agricultural_risks(
                    data_results, region, crop
                ),
                'regional_context': self._get_regional_context(region, crop)
            }
            
            # Cache for 30 minutes
            self.cache.set(cache_key, comprehensive_analysis, 1800)
            
            return comprehensive_analysis
            
        except Exception as e:
            return {
                'region': region,
                'crop_focus': crop,
                'error': f"Failed to generate comprehensive analysis: {str(e)}",
                'fallback_advice': self._get_fallback_advice(region, crop)
            }
    
    def _gather_all_data(self, region: str, crop: str, include_forecast: bool) -> Dict[str, Any]:
        """Gather data from all services concurrently"""
        data_results = {}
        
        # Use ThreadPoolExecutor for concurrent API calls
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            # Submit all API calls
            futures['weather'] = executor.submit(self._safe_get_weather, region)
            futures['nasa_weather'] = executor.submit(self._safe_get_nasa_weather, region)
            
            if crop:
                futures['fao_data'] = executor.submit(self._safe_get_fao_data, crop)
            
            if include_forecast:
                futures['forecast'] = executor.submit(self._safe_get_forecast, region)
            
            # Collect results
            for key, future in futures.items():
                try:
                    data_results[key] = future.result(timeout=30)
                except Exception as e:
                    data_results[key] = {'error': str(e)}
        
        return data_results
    
    def _safe_get_weather(self, region: str) -> Dict:
        """Safely get weather data with error handling"""
        try:
            return self.weather_analyzer.analyze_current_conditions(region)
        except Exception as e:
            return {'error': str(e), 'service': 'weather'}
    
    def _safe_get_nasa_weather(self, region: str) -> Dict:
        """Safely get NASA weather data"""
        try:
            return self.nasa_client.get_agricultural_weather(region, days_back=7)
        except Exception as e:
            return {'error': str(e), 'service': 'nasa'}
    
    def _safe_get_fao_data(self, crop: str) -> Dict:
        """Safely get FAO production data"""
        try:
            return self.fao_client.get_crop_production_data(crop, year=2020)
        except Exception as e:
            return {'error': str(e), 'service': 'fao'}
    
    def _safe_get_forecast(self, region: str) -> Dict:
        """Safely get weather forecast"""
        try:
            return self.weather_client.get_5day_forecast(region)
        except Exception as e:
            return {'error': str(e), 'service': 'forecast'}
    
    def _get_successful_sources(self, data_results: Dict) -> List[str]:
        """Get list of successfully contacted data sources"""
        successful = []
        source_mapping = {
            'weather': 'OpenWeatherMap',
            'nasa_weather': 'NASA POWER',
            'fao_data': 'FAO FAOSTAT',
            'forecast': 'Weather Forecast'
        }
        
        for key, data in data_results.items():
            if 'error' not in data:
                successful.append(source_mapping.get(key, key))
        
        return successful
    
    def _generate_integrated_insights(self, data_results: Dict, region: str, 
                                    crop: str = None) -> List[str]:
        """Generate insights by combining data from multiple sources"""
        insights = []
        
        # Weather-based insights
        weather_data = data_results.get('weather', {})
        if 'error' not in weather_data:
            weather_insights = weather_data.get('recommendations', [])
            insights.extend(weather_insights[:3])  # Top 3 weather insights
        
        # NASA climate insights
        nasa_data = data_results.get('nasa_weather', {})
        if 'error' not in nasa_data:
            nasa_insights = nasa_data.get('agricultural_insights', [])
            insights.extend(nasa_insights[:2])  # Top 2 NASA insights
        
        # Production trend insights
        fao_data = data_results.get('fao_data', {})
        if 'error' not in fao_data and crop:
            trend = fao_data.get('trend', 'stable')
            if trend == 'increasing':
                insights.append(f"{crop.title()} production in Cameroon is growing - favorable market conditions")
            elif trend == 'decreasing':
                insights.append(f"{crop.title()} production declining - consider diversification or improved practices")
        
        # Regional specialization insights
        regional_insights = self._get_regional_specialization_insights(region, crop)
        insights.extend(regional_insights)
        
        # Cross-data insights (combining weather + production)
        cross_insights = self._generate_cross_data_insights(data_results, region, crop)
        insights.extend(cross_insights)
        
        return insights
    
    def _generate_actionable_recommendations(self, data_results: Dict, region: str, 
                                          crop: str = None) -> List[Dict[str, str]]:
        """Generate specific, actionable recommendations"""
        recommendations = []
        
        # Weather-based actions
        weather_data = data_results.get('weather', {})
        if 'error' not in weather_data:
            current_temp = weather_data.get('current_conditions', {}).get('temperature', 25)
            humidity = weather_data.get('current_conditions', {}).get('humidity', 70)
            
            if current_temp > 32:
                recommendations.append({
                    'category': 'immediate',
                    'action': 'Provide shade or increase watering',
                    'reason': f'High temperature ({current_temp}°C) may stress crops',
                    'priority': 'high'
                })
            
            if humidity > 85:
                recommendations.append({
                    'category': 'monitoring',
                    'action': 'Increase disease surveillance',
                    'reason': f'High humidity ({humidity}%) increases disease risk',
                    'priority': 'medium'
                })
        
        # Crop-specific recommendations
        if crop:
            crop_recommendations = self._get_crop_specific_recommendations(
                crop, data_results, region
            )
            recommendations.extend(crop_recommendations)
        
        # Regional recommendations
        regional_recs = self._get_regional_recommendations(region, data_results)
        recommendations.extend(regional_recs)
        
        return recommendations
    
    def _assess_agricultural_risks(self, data_results: Dict, region: str, 
                                 crop: str = None) -> Dict[str, Any]:
        """Assess current agricultural risks"""
        risks = {
            'overall_risk_level': 'low',
            'specific_risks': [],
            'mitigation_strategies': []
        }
        
        risk_factors = []
        
        # Weather-related risks
        weather_data = data_results.get('weather', {})
        if 'error' not in weather_data:
            alerts = weather_data.get('alerts', [])
            for alert in alerts:
                risk_factors.append({
                    'type': 'weather',
                    'severity': alert.get('severity', 'medium'),
                    'description': alert.get('message', 'Weather alert'),
                    'source': 'current_weather'
                })
        
        # Climate pattern risks
        nasa_data = data_results.get('nasa_weather', {})
        if 'error' not in nasa_data:
            temp_analysis = nasa_data.get('temperature_analysis', {})
            rainfall = nasa_data.get('precipitation_analysis', {}).get('total_rainfall', 0)
            
            if temp_analysis.get('max_temp', 30) > 40:
                risk_factors.append({
                    'type': 'extreme_heat',
                    'severity': 'high',
                    'description': 'Extreme heat conditions detected',
                    'source': 'nasa_climate'
                })
            
            if rainfall < 5:
                risk_factors.append({
                    'type': 'drought',
                    'severity': 'medium',
                    'description': 'Low rainfall may affect crop growth',
                    'source': 'nasa_climate'
                })
        
        # Determine overall risk level
        if any(risk['severity'] == 'high' for risk in risk_factors):
            risks['overall_risk_level'] = 'high'
        elif any(risk['severity'] == 'medium' for risk in risk_factors):
            risks['overall_risk_level'] = 'medium'
        
        risks['specific_risks'] = risk_factors
        risks['mitigation_strategies'] = self._generate_mitigation_strategies(risk_factors)
        
        return risks
    
    def _generate_mitigation_strategies(self, risk_factors: List[Dict]) -> List[str]:
        """Generate mitigation strategies for identified risks"""
        strategies = []
        
        for risk in risk_factors:
            risk_type = risk['type']
            
            if risk_type == 'extreme_heat':
                strategies.extend([
                    'Install shade structures for sensitive crops',
                    'Increase irrigation frequency during peak heat hours',
                    'Apply mulch to conserve soil moisture'
                ])
            elif risk_type == 'drought':
                strategies.extend([
                    'Implement water conservation techniques',
                    'Consider drought-resistant crop varieties',
                    'Install efficient irrigation systems'
                ])
            elif risk_type == 'weather':
                strategies.append('Monitor weather conditions closely and adjust activities accordingly')
        
        return list(set(strategies))  # Remove duplicates
    
    def _get_regional_specialization_insights(self, region: str, crop: str = None) -> List[str]:
        """Get insights based on regional crop specializations"""
        insights = []
        specialties = self.regional_specializations.get(region.lower(), [])
        
        if crop and crop.lower() in specialties:
            insights.append(f"{region.title()} region is well-suited for {crop} production")
            insights.append("Connect with local farmers' cooperatives for best practices")
        elif specialties:
            top_crops = ', '.join(specialties[:3])
            insights.append(f"Consider {region}'s specialty crops: {top_crops}")
        
        return insights
    
    def _generate_cross_data_insights(self, data_results: Dict, region: str, 
                                    crop: str = None) -> List[str]:
        """Generate insights by combining multiple data sources"""
        insights = []
        
        weather_data = data_results.get('weather', {})
        nasa_data = data_results.get('nasa_weather', {})
        fao_data = data_results.get('fao_data', {})
        
        # Combine weather and production data
        if ('error' not in weather_data and 'error' not in fao_data and 
            crop and weather_data.get('current_conditions')):
            
            temp = weather_data['current_conditions'].get('temperature', 25)
            trend = fao_data.get('trend', 'stable')
            
            if temp > 30 and trend == 'decreasing':
                insights.append(f"High temperatures may be contributing to declining {crop} yields")
            elif temp < 25 and trend == 'increasing':
                insights.append(f"Favorable temperatures supporting {crop} production growth")
        
        return insights
    
    def _get_regional_context(self, region: str, crop: str = None) -> Dict[str, Any]:
        """Get regional context information"""
        return {
            'region': region,
            'primary_crops': self.regional_specializations.get(region.lower(), []),
            'crop_suitability': crop.lower() in self.regional_specializations.get(region.lower(), []) if crop else None,
            'agricultural_zones': self._get_agricultural_zones(region),
            'market_access': self._assess_market_access(region)
        }
    
    def _get_agricultural_zones(self, region: str) -> List[str]:
        """Get agricultural zones for the region"""
        zone_mapping = {
            'centre': ['humid_forest', 'transition_savanna'],
            'littoral': ['coastal_plain', 'humid_forest'],
            'west': ['highland', 'volcanic_soils'],
            'northwest': ['highland', 'grassland'],
            'southwest': ['coastal_mountain', 'volcanic_soils'],
            'east': ['humid_forest', 'congo_basin'],
            'north': ['sudan_savanna', 'sahel_transition'],
            'far_north': ['sahel', 'semi_arid'],
            'adamawa': ['guinea_savanna', 'plateau'],
            'south': ['humid_forest', 'equatorial']
        }
        return zone_mapping.get(region.lower(), ['general'])
    
    def _assess_market_access(self, region: str) -> str:
        """Assess market access for the region"""
        access_ratings = {
            'centre': 'excellent',  # Capital region
            'littoral': 'excellent',  # Port city
            'west': 'good',
            'northwest': 'good',
            'southwest': 'good',
            'east': 'moderate',
            'north': 'moderate',
            'far_north': 'limited',
            'adamawa': 'moderate',
            'south': 'moderate'
        }
        return access_ratings.get(region.lower(), 'moderate')
    
    def _get_crop_specific_recommendations(self, crop: str, data_results: Dict, 
                                        region: str) -> List[Dict[str, str]]:
        """Get crop-specific recommendations"""
        recommendations = []
        
        # Basic crop care recommendations
        if crop.lower() in ['maize', 'rice', 'millet']:
            recommendations.append({
                'category': 'cultivation',
                'action': 'Monitor for stem borer and fall armyworm',
                'reason': 'Cereals are susceptible to these pests',
                'priority': 'medium'
            })
        elif crop.lower() in ['tomatoes', 'pepper', 'eggplant']:
            recommendations.append({
                'category': 'disease_prevention',
                'action': 'Ensure good air circulation between plants',
                'reason': 'Nightshade family crops prone to blight',
                'priority': 'high'
            })
        
        return recommendations
    
    def _get_regional_recommendations(self, region: str, data_results: Dict) -> List[Dict[str, str]]:
        """Get region-specific recommendations"""
        recommendations = []
        
        if region.lower() in ['north', 'far_north']:
            recommendations.append({
                'category': 'water_management',
                'action': 'Implement water conservation practices',
                'reason': 'Semi-arid climate requires careful water management',
                'priority': 'high'
            })
        elif region.lower() in ['southwest', 'littoral']:
            recommendations.append({
                'category': 'drainage',
                'action': 'Ensure adequate drainage systems',
                'reason': 'High rainfall regions need good drainage',
                'priority': 'medium'
            })
        
        return recommendations
    
    def _get_fallback_advice(self, region: str, crop: str = None) -> List[str]:
        """Provide fallback advice when data services fail"""
        advice = [
            f"Unable to retrieve current data for {region} region",
            "Follow general best practices for your crop and season",
            "Consult with local agricultural extension officers",
            "Monitor weather conditions using local sources"
        ]
        
        if crop:
            advice.append(f"Apply standard {crop} cultivation practices for your area")
        
        return advice

    def get_multi_region_comparison(self, regions: List[str], crop: str = None) -> Dict[str, Any]:
        """Compare agricultural conditions across multiple regions"""
        comparison_data = {}
        
        for region in regions:
            try:
                region_analysis = self.get_comprehensive_analysis(region, crop, include_forecast=False)
                comparison_data[region] = region_analysis
            except Exception as e:
                comparison_data[region] = {'error': str(e)}
        
        return {
            'comparison_type': 'multi_region',
            'regions_compared': regions,
            'crop_focus': crop,
            'region_data': comparison_data,
            'summary': self._generate_comparison_summary(comparison_data, crop)
        }
    
    def _generate_comparison_summary(self, comparison_data: Dict, crop: str = None) -> Dict[str, Any]:
        """Generate summary of multi-region comparison"""
        successful_regions = [r for r, data in comparison_data.items() if 'error' not in data]
        
        if not successful_regions:
            return {'error': 'No successful data retrieval for any region'}
        
        summary = {
            'best_weather_conditions': None,
            'highest_production_potential': None,
            'lowest_risk_region': None,
            'overall_recommendation': None
        }
        
        # Simple scoring to determine best regions
        region_scores = {}
        for region in successful_regions:
            data = comparison_data[region]
            
            # Score based on available metrics
            score = 50  # Base score
            
            # Weather score
            weather = data.get('current_weather', {})
            if 'error' not in weather:
                score += 10
            
            # Risk score (lower risk = higher score)
            risk_level = data.get('risk_assessment', {}).get('overall_risk_level', 'medium')
            if risk_level == 'low':
                score += 20
            elif risk_level == 'high':
                score -= 10
            
            region_scores[region] = score
        
        if region_scores:
            best_region = max(region_scores, key=region_scores.get)
            summary['overall_recommendation'] = f"{best_region.title()} region shows most favorable conditions"
        
        return summary