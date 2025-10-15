"""
NASA POWER API Client
Location: agribot/services/agricultural_data/nasa_client.py

Handles communication with NASA POWER API for agricultural meteorology,
solar data, and climate information for Cameroon regions.
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config.settings import APIConfig
from services.cache.redis_cache import RedisCache, cached
from utils.exceptions import APIServiceError

class NASAClient:
    """Client for NASA POWER API integration"""
    
    def __init__(self, config: APIConfig = None):
        self.config = config or APIConfig()
        self.base_url = self.config.nasa_base_url
        self.cache = RedisCache()
        
        # Cameroon regions with coordinates
        self.region_coordinates = {
            'centre': {'lat': 3.85, 'lon': 11.5, 'name': 'Centre (Yaounde)'},
            'littoral': {'lat': 4.06, 'lon': 9.79, 'name': 'Littoral (Douala)'},
            'west': {'lat': 5.48, 'lon': 10.42, 'name': 'West (Bafoussam)'},
            'northwest': {'lat': 5.96, 'lon': 10.15, 'name': 'Northwest (Bamenda)'},
            'southwest': {'lat': 4.15, 'lon': 9.23, 'name': 'Southwest (Buea)'},
            'east': {'lat': 4.58, 'lon': 13.69, 'name': 'East (Bertoua)'},
            'north': {'lat': 9.30, 'lon': 13.40, 'name': 'North (Garoua)'},
            'far_north': {'lat': 10.59, 'lon': 14.32, 'name': 'Far North (Maroua)'},
            'adamawa': {'lat': 7.32, 'lon': 13.59, 'name': 'Adamawa (Ngaoundere)'},
            'south': {'lat': 2.91, 'lon': 11.15, 'name': 'South (Ebolowa)'}
        }
        
        # NASA POWER parameters for agriculture
        self.agricultural_parameters = [
            'T2M',      # Temperature at 2 meters
            'T2M_MIN',  # Minimum temperature
            'T2M_MAX',  # Maximum temperature
            'RH2M',     # Relative humidity at 2 meters
            'PRECTOTCORR',  # Precipitation corrected
            'WS2M',     # Wind speed at 2 meters
            'ALLSKY_SFC_SW_DWN'  # Solar irradiance
        ]
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.config.max_retries):
            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    if attempt == self.config.max_retries - 1:
                        raise APIServiceError(
                            "NASA POWER",
                            f"HTTP {response.status_code}: {response.text}",
                            response.status_code
                        )
                    
            except requests.Timeout:
                if attempt == self.config.max_retries - 1:
                    raise APIServiceError(
                        "NASA POWER",
                        "Request timeout after retries"
                    )
            except requests.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise APIServiceError(
                        "NASA POWER",
                        f"Request failed: {str(e)}"
                    )
        
        raise APIServiceError("NASA POWER", "Max retries exceeded")
    
    @cached(timeout=21600, key_prefix="nasa:agri_weather")  # Cache for 6 hours
    def get_agricultural_weather(self, region: str, days_back: int = 7) -> Dict:
        """Get agricultural weather data for a region"""
        if region.lower() not in self.region_coordinates:
            available_regions = ', '.join(self.region_coordinates.keys())
            raise APIServiceError(
                "NASA POWER",
                f"Unknown region: {region}. Available: {available_regions}"
            )
        
        coords = self.region_coordinates[region.lower()]
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            params = {
                'parameters': ','.join(self.agricultural_parameters),
                'community': 'AG',  # Agricultural community
                'longitude': coords['lon'],
                'latitude': coords['lat'],
                'start': start_date.strftime('%Y%m%d'),
                'end': end_date.strftime('%Y%m%d'),
                'format': 'JSON'
            }
            
            data = self._make_request('daily/1.0/point', params)
            
            return self._process_nasa_weather_data(data, region, coords, days_back)
            
        except APIServiceError:
            # Return fallback data
            return self._get_fallback_weather_data(region, days_back)
        except Exception as e:
            raise APIServiceError(
                "NASA POWER",
                f"Failed to process weather data: {str(e)}"
            )
    
    def _process_nasa_weather_data(self, raw_data: Dict, region: str, 
                                 coords: Dict, days_back: int) -> Dict:
        """Process raw NASA POWER data into agricultural insights"""
        try:
            parameters = raw_data.get('properties', {}).get('parameter', {})
            
            # Extract and process temperature data
            temps = list(parameters.get('T2M', {}).values())
            temp_mins = list(parameters.get('T2M_MIN', {}).values())
            temp_maxs = list(parameters.get('T2M_MAX', {}).values())
            
            # Clean invalid data (NASA uses -999 for missing data)
            temps = [t for t in temps if t > -500]
            temp_mins = [t for t in temp_mins if t > -500]
            temp_maxs = [t for t in temp_maxs if t > -500]
            
            # Extract other parameters
            humidity = list(parameters.get('RH2M', {}).values())
            precipitation = list(parameters.get('PRECTOTCORR', {}).values())
            wind_speed = list(parameters.get('WS2M', {}).values())
            solar_radiation = list(parameters.get('ALLSKY_SFC_SW_DWN', {}).values())
            
            # Clean data
            humidity = [h for h in humidity if h > -500]
            precipitation = [p for p in precipitation if p > -500]
            wind_speed = [w for w in wind_speed if w > -500]
            solar_radiation = [s for s in solar_radiation if s > -500]
            
            # Calculate statistics
            analysis = {
                'region': region,
                'region_name': coords['name'],
                'coordinates': {'latitude': coords['lat'], 'longitude': coords['lon']},
                'period_days': days_back,
                'temperature_analysis': {
                    'avg_temp': round(sum(temps) / len(temps), 1) if temps else 25,
                    'min_temp': min(temp_mins) if temp_mins else 20,
                    'max_temp': max(temp_maxs) if temp_maxs else 30,
                    'temp_range': max(temp_maxs) - min(temp_mins) if temp_mins and temp_maxs else 10
                },
                'humidity_analysis': {
                    'avg_humidity': round(sum(humidity) / len(humidity), 1) if humidity else 70,
                    'humidity_range': [min(humidity), max(humidity)] if humidity else [60, 80]
                },
                'precipitation_analysis': {
                    'total_rainfall': round(sum(precipitation), 1) if precipitation else 5,
                    'avg_daily_rainfall': round(sum(precipitation) / len(precipitation), 1) if precipitation else 0.7,
                    'rainy_days': len([p for p in precipitation if p > 1]) if precipitation else 2
                },
                'solar_analysis': {
                    'avg_solar_radiation': round(sum(solar_radiation) / len(solar_radiation), 1) if solar_radiation else 18,
                    'total_solar_energy': round(sum(solar_radiation), 1) if solar_radiation else 126
                },
                'wind_analysis': {
                    'avg_wind_speed': round(sum(wind_speed) / len(wind_speed), 1) if wind_speed else 3
                },
                'data_source': 'NASA POWER',
                'data_quality': 'satellite_derived'
            }
            
            # Add agricultural insights
            analysis['agricultural_insights'] = self._generate_agricultural_insights(analysis)
            
            return analysis
            
        except Exception as e:
            raise APIServiceError(
                "NASA POWER",
                f"Failed to process NASA data: {str(e)}"
            )
    
    def _get_fallback_weather_data(self, region: str, days_back: int) -> Dict:
        """Provide fallback weather data based on regional climate patterns"""
        # Typical climate patterns for each region
        regional_patterns = {
            'centre': {'temp': 25, 'humidity': 80, 'rainfall': 4.2, 'solar': 18.5},
            'littoral': {'temp': 26, 'humidity': 85, 'rainfall': 6.8, 'solar': 16.2},
            'west': {'temp': 22, 'humidity': 75, 'rainfall': 2.8, 'solar': 19.8},
            'northwest': {'temp': 21, 'humidity': 70, 'rainfall': 3.5, 'solar': 19.5},
            'southwest': {'temp': 24, 'humidity': 90, 'rainfall': 8.2, 'solar': 15.8},
            'east': {'temp': 24, 'humidity': 85, 'rainfall': 5.1, 'solar': 17.9},
            'north': {'temp': 28, 'humidity': 45, 'rainfall': 0.8, 'solar': 22.4},
            'far_north': {'temp': 30, 'humidity': 35, 'rainfall': 0.3, 'solar': 23.8},
            'adamawa': {'temp': 23, 'humidity': 60, 'rainfall': 2.5, 'solar': 20.9},
            'south': {'temp': 24, 'humidity': 85, 'rainfall': 6.8, 'solar': 17.3}
        }
        
        pattern = regional_patterns.get(region.lower(), regional_patterns['centre'])
        coords = self.region_coordinates.get(region.lower(), self.region_coordinates['centre'])
        
        return {
            'region': region,
            'region_name': coords['name'],
            'coordinates': {'latitude': coords['lat'], 'longitude': coords['lon']},
            'period_days': days_back,
            'temperature_analysis': {
                'avg_temp': pattern['temp'],
                'min_temp': pattern['temp'] - 3,
                'max_temp': pattern['temp'] + 5,
                'temp_range': 8
            },
            'humidity_analysis': {
                'avg_humidity': pattern['humidity'],
                'humidity_range': [pattern['humidity'] - 10, pattern['humidity'] + 10]
            },
            'precipitation_analysis': {
                'total_rainfall': pattern['rainfall'] * days_back,
                'avg_daily_rainfall': pattern['rainfall'],
                'rainy_days': max(1, int(days_back * 0.3))
            },
            'solar_analysis': {
                'avg_solar_radiation': pattern['solar'],
                'total_solar_energy': pattern['solar'] * days_back
            },
            'wind_analysis': {
                'avg_wind_speed': 3.5
            },
            'data_source': 'Regional climate patterns (NASA API unavailable)',
            'data_quality': 'estimated',
            'agricultural_insights': self._generate_agricultural_insights({
                'temperature_analysis': {'avg_temp': pattern['temp']},
                'humidity_analysis': {'avg_humidity': pattern['humidity']},
                'precipitation_analysis': {'total_rainfall': pattern['rainfall'] * days_back}
            })
        }
    
    def _generate_agricultural_insights(self, weather_data: Dict) -> List[str]:
        """Generate agricultural insights from weather analysis"""
        insights = []
        
        temp_data = weather_data.get('temperature_analysis', {})
        humidity_data = weather_data.get('humidity_analysis', {})
        rainfall_data = weather_data.get('precipitation_analysis', {})
        
        avg_temp = temp_data.get('avg_temp', 25)
        avg_humidity = humidity_data.get('avg_humidity', 70)
        total_rainfall = rainfall_data.get('total_rainfall', 10)
        
        # Temperature insights
        if avg_temp > 30:
            insights.append("High temperatures may stress heat-sensitive crops")
        elif avg_temp < 20:
            insights.append("Cool temperatures may slow crop growth")
        else:
            insights.append("Temperature conditions are favorable for most crops")
        
        # Humidity insights
        if avg_humidity > 85:
            insights.append("High humidity increases disease risk - monitor crops closely")
        elif avg_humidity < 50:
            insights.append("Low humidity may increase irrigation needs")
        
        # Rainfall insights
        if total_rainfall > 50:
            insights.append("Good rainfall supports crop growth and development")
        elif total_rainfall < 10:
            insights.append("Low rainfall - consider supplemental irrigation")
        
        # Seasonal advice
        insights.append("Weather conditions suitable for fieldwork and crop management")
        
        return insights