"""
OpenWeatherMap API Client
Location: agribot/services/weather/openweather_client.py

Handles communication with OpenWeatherMap API for current weather data
and forecasts for Cameroon regions.
"""

import requests
from typing import Dict, Optional, List
from config.settings import APIConfig
from services.cache.redis_cache import RedisCache, cached
from config.settings import CacheConfig
from utils.exceptions import APIServiceError

class OpenWeatherClient:
    """Client for OpenWeatherMap API integration"""
    
    def __init__(self, config: APIConfig = None):
        self.config = config or APIConfig()
        self.base_url = "http://api.openweathermap.org/data/2.5"

        # Only initialize cache if caching is enabled
        cache_config = CacheConfig()
        if cache_config.enabled:
            try:
                self.cache = RedisCache(cache_config)
            except Exception:
                # If Redis connection fails, disable caching for this session
                self.cache = None
        else:
            self.cache = None
        
        # Cameroon regions with their main cities
        self.region_cities = {
            'centre': {'city': 'Yaounde', 'country': 'CM'},
            'littoral': {'city': 'Douala', 'country': 'CM'},
            'west': {'city': 'Bafoussam', 'country': 'CM'},
            'northwest': {'city': 'Bamenda', 'country': 'CM'},
            'southwest': {'city': 'Buea', 'country': 'CM'},
            'east': {'city': 'Bertoua', 'country': 'CM'},
            'north': {'city': 'Garoua', 'country': 'CM'},
            'far_north': {'city': 'Maroua', 'country': 'CM'},
            'adamawa': {'city': 'Ngaoundere', 'country': 'CM'},
            'south': {'city': 'Ebolowa', 'country': 'CM'}
        }
        
        if not self.config.openweather_key:
            raise APIServiceError(
                "OpenWeatherMap",
                "API key not configured"
            )
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make API request with error handling and retries"""
        params['appid'] = self.config.openweather_key
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
                elif response.status_code == 401:
                    raise APIServiceError(
                        "OpenWeatherMap",
                        "Invalid API key",
                        response.status_code
                    )
                elif response.status_code == 404:
                    raise APIServiceError(
                        "OpenWeatherMap", 
                        "Location not found",
                        response.status_code
                    )
                else:
                    if attempt == self.config.max_retries - 1:
                        raise APIServiceError(
                            "OpenWeatherMap",
                            f"HTTP {response.status_code}: {response.text}",
                            response.status_code
                        )
                    
            except requests.Timeout:
                if attempt == self.config.max_retries - 1:
                    raise APIServiceError(
                        "OpenWeatherMap",
                        "Request timeout after retries"
                    )
            except requests.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise APIServiceError(
                        "OpenWeatherMap",
                        f"Request failed: {str(e)}"
                    )
        
        raise APIServiceError("OpenWeatherMap", "Max retries exceeded")
    
    @cached(timeout=1800, key_prefix="weather:current")  # Cache for 30 minutes
    def get_current_weather(self, region: str) -> Dict:
        """Get current weather for a Cameroon region"""
        if region.lower() not in self.region_cities:
            available_regions = ', '.join(self.region_cities.keys())
            raise APIServiceError(
                "OpenWeatherMap",
                f"Unknown region: {region}. Available: {available_regions}"
            )
        
        city_info = self.region_cities[region.lower()]
        
        try:
            params = {
                'q': f"{city_info['city']},{city_info['country']}",
                'units': 'metric'
            }
            
            data = self._make_request('weather', params)
            
            return {
                'region': region,
                'city': city_info['city'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'wind_direction': data.get('wind', {}).get('deg', 0),
                'visibility': data.get('visibility', 0),
                'clouds': data.get('clouds', {}).get('all', 0),
                'sunrise': data['sys']['sunrise'],
                'sunset': data['sys']['sunset'],
                'timestamp': data['dt'],
                'data_source': 'OpenWeatherMap'
            }
            
        except APIServiceError:
            raise
        except Exception as e:
            raise APIServiceError(
                "OpenWeatherMap",
                f"Failed to parse weather data: {str(e)}"
            )
    
    @cached(timeout=3600, key_prefix="weather:forecast")  # Cache for 1 hour
    def get_5day_forecast(self, region: str) -> List[Dict]:
        """Get 5-day weather forecast for a region"""
        if region.lower() not in self.region_cities:
            available_regions = ', '.join(self.region_cities.keys())
            raise APIServiceError(
                "OpenWeatherMap",
                f"Unknown region: {region}. Available: {available_regions}"
            )
        
        city_info = self.region_cities[region.lower()]
        
        try:
            params = {
                'q': f"{city_info['city']},{city_info['country']}",
                'units': 'metric'
            }
            
            data = self._make_request('forecast', params)
            
            forecast_list = []
            for item in data['list']:
                forecast_list.append({
                    'datetime': item['dt'],
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'description': item['weather'][0]['description'],
                    'humidity': item['main']['humidity'],
                    'wind_speed': item.get('wind', {}).get('speed', 0),
                    'rain': item.get('rain', {}).get('3h', 0),
                    'clouds': item['clouds']['all']
                })
            
            return {
                'region': region,
                'city': city_info['city'],
                'forecast': forecast_list,
                'data_source': 'OpenWeatherMap'
            }
            
        except APIServiceError:
            raise
        except Exception as e:
            raise APIServiceError(
                "OpenWeatherMap",
                f"Failed to parse forecast data: {str(e)}"
            )
    
    def get_weather_alerts(self, region: str) -> List[Dict]:
        """Get weather alerts for a region (if available)"""
        # OpenWeatherMap alerts require One Call API (paid)
        # For now, return empty list
        return []
    
    def clear_cache(self, region: str = None):
        """Clear weather cache for specific region or all regions"""
        if region:
            self.cache.delete(f"weather:current:{region}")
            self.cache.delete(f"weather:forecast:{region}")
        else:
            self.cache.clear_pattern("weather:*")