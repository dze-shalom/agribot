"""
Weather Analysis Service
Location: agribot/services/weather/weather_analyzer.py

Analyzes weather data and provides agricultural insights and recommendations
based on current and forecast weather conditions.
"""

from typing import Dict, List, Any
from datetime import datetime
from services.weather.openweather_client import OpenWeatherClient
from utils.exceptions import APIServiceError

class WeatherAnalyzer:
    """Analyzes weather data for agricultural decision making"""
    
    def __init__(self, weather_client: OpenWeatherClient = None):
        self.weather_client = weather_client or OpenWeatherClient()
        
        # Temperature thresholds for different crop categories (Celsius)
        self.temperature_thresholds = {
            'cereals': {'min': 18, 'max': 35, 'optimal': (22, 30)},
            'vegetables': {'min': 15, 'max': 32, 'optimal': (18, 28)},
            'fruits': {'min': 20, 'max': 38, 'optimal': (23, 32)},
            'legumes': {'min': 16, 'max': 34, 'optimal': (20, 28)},
            'cash_crops': {'min': 18, 'max': 36, 'optimal': (22, 32)}
        }
        
        # Humidity thresholds
        self.humidity_thresholds = {
            'low': 40,
            'optimal_min': 50,
            'optimal_max': 70,
            'high': 85
        }
    
    def analyze_current_conditions(self, region: str) -> Dict[str, Any]:
        """Analyze current weather conditions for agricultural activities"""
        try:
            weather_data = self.weather_client.get_current_weather(region)
            
            analysis = {
                'region': region,
                'current_conditions': weather_data,
                'agricultural_analysis': self._analyze_agricultural_conditions(weather_data),
                'recommendations': self._generate_weather_recommendations(weather_data),
                'alerts': self._check_weather_alerts(weather_data),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return analysis
            
        except APIServiceError as e:
            return {
                'region': region,
                'error': str(e),
                'fallback_advice': self._get_general_weather_advice(region)
            }
    
    def _analyze_agricultural_conditions(self, weather_data: Dict) -> Dict[str, Any]:
        """Analyze weather conditions from agricultural perspective"""
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 60)
        wind_speed = weather_data.get('wind_speed', 0)
        description = weather_data.get('description', '').lower()
        
        analysis = {
            'temperature_analysis': {
                'current_temp': temp,
                'status': 'optimal' if 20 <= temp <= 32 else 'suboptimal',
                'suitability': self._assess_temperature_suitability(temp)
            },
            'humidity_analysis': {
                'current_humidity': humidity,
                'status': self._assess_humidity_status(humidity),
                'disease_risk': 'high' if humidity > 85 else 'moderate' if humidity > 70 else 'low'
            },
            'wind_analysis': {
                'wind_speed': wind_speed,
                'crop_stress_risk': 'high' if wind_speed > 10 else 'low'
            },
            'precipitation_status': {
                'current_weather': description,
                'is_rainy': any(word in description for word in ['rain', 'drizzle', 'shower']),
                'field_work_suitable': not any(word in description for word in ['rain', 'storm', 'heavy'])
            }
        }
        
        return analysis
    
    def _assess_temperature_suitability(self, temp: float) -> Dict[str, str]:
        """Assess temperature suitability for different crop categories"""
        suitability = {}
        
        for category, thresholds in self.temperature_thresholds.items():
            if thresholds['optimal'][0] <= temp <= thresholds['optimal'][1]:
                suitability[category] = 'excellent'
            elif thresholds['min'] <= temp <= thresholds['max']:
                suitability[category] = 'suitable'
            else:
                suitability[category] = 'challenging'
        
        return suitability
    
    def _assess_humidity_status(self, humidity: float) -> str:
        """Assess humidity status for agriculture"""
        if humidity < self.humidity_thresholds['low']:
            return 'too_low'
        elif self.humidity_thresholds['optimal_min'] <= humidity <= self.humidity_thresholds['optimal_max']:
            return 'optimal'
        elif humidity > self.humidity_thresholds['high']:
            return 'too_high'
        else:
            return 'acceptable'
    
    def _generate_weather_recommendations(self, weather_data: Dict) -> List[str]:
        """Generate agricultural recommendations based on weather"""
        recommendations = []
        
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 60)
        description = weather_data.get('description', '').lower()
        
        # Temperature-based recommendations
        if temp > 35:
            recommendations.extend([
                "High temperature alert - provide shade for sensitive crops",
                "Increase watering frequency for all crops",
                "Avoid transplanting or heavy field work during midday"
            ])
        elif temp < 18:
            recommendations.extend([
                "Cool temperature - protect sensitive crops from cold",
                "Consider covering young plants at night",
                "Delay planting of warm-season crops"
            ])
        
        # Humidity-based recommendations
        if humidity > 85:
            recommendations.extend([
                "High humidity increases disease risk - improve air circulation",
                "Monitor crops closely for fungal diseases",
                "Avoid overhead watering"
            ])
        elif humidity < 40:
            recommendations.extend([
                "Low humidity - increase watering frequency",
                "Consider mulching to retain soil moisture"
            ])
        
        # Weather-specific recommendations
        if 'rain' in description:
            recommendations.extend([
                "Good time for planting if soil is well-prepared",
                "Delay harvesting until weather clears",
                "Check drainage systems"
            ])
        elif 'clear' in description or 'sunny' in description:
            recommendations.extend([
                "Excellent weather for field work and harvesting",
                "Good time for drying crops",
                "Monitor soil moisture levels"
            ])
        
        return recommendations
    
    def _check_weather_alerts(self, weather_data: Dict) -> List[Dict]:
        """Check for weather conditions that require farmer attention"""
        alerts = []
        
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 60)
        wind_speed = weather_data.get('wind_speed', 0)
        description = weather_data.get('description', '').lower()
        
        # Temperature alerts
        if temp > 40:
            alerts.append({
                'type': 'extreme_heat',
                'severity': 'high',
                'message': 'Extreme heat warning - take immediate action to protect crops'
            })
        
        # Disease risk alerts
        if humidity > 90 and temp > 25:
            alerts.append({
                'type': 'disease_risk',
                'severity': 'medium',
                'message': 'High disease risk due to hot, humid conditions'
            })
        
        # Wind alerts
        if wind_speed > 15:
            alerts.append({
                'type': 'high_wind',
                'severity': 'medium',
                'message': 'Strong winds may damage crops - check support structures'
            })
        
        # Storm alerts
        if any(word in description for word in ['storm', 'thunder', 'heavy']):
            alerts.append({
                'type': 'storm',
                'severity': 'high',
                'message': 'Storm conditions - secure equipment and protect crops'
            })
        
        return alerts
    
    def _get_general_weather_advice(self, region: str) -> List[str]:
        """Provide general weather advice when API is unavailable"""
        return [
            f"Weather data temporarily unavailable for {region} region",
            "Monitor local weather conditions closely",
            "Follow seasonal farming calendar for your region",
            "Ensure good drainage systems are in place",
            "Keep emergency supplies ready for extreme weather"
        ]
    
    def get_farming_suitability_score(self, region: str) -> Dict[str, Any]:
        """Get overall farming suitability score based on current weather"""
        try:
            analysis = self.analyze_current_conditions(region)
            agricultural_analysis = analysis.get('agricultural_analysis', {})
            
            # Calculate composite score (0-100)
            temp_score = 80 if agricultural_analysis.get('temperature_analysis', {}).get('status') == 'optimal' else 60
            humidity_score = 80 if agricultural_analysis.get('humidity_analysis', {}).get('status') == 'optimal' else 60
            precipitation_score = 90 if agricultural_analysis.get('precipitation_status', {}).get('field_work_suitable', True) else 40
            
            overall_score = (temp_score + humidity_score + precipitation_score) / 3
            
            return {
                'region': region,
                'overall_score': round(overall_score, 1),
                'temperature_score': temp_score,
                'humidity_score': humidity_score,
                'precipitation_score': precipitation_score,
                'recommendation': 'excellent' if overall_score > 80 else 'good' if overall_score > 60 else 'fair'
            }
            
        except Exception as e:
            return {
                'region': region,
                'error': str(e),
                'overall_score': 0,
                'recommendation': 'unknown'
            }