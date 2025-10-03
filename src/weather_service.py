import requests
import json
from config import Config

class SimpleWeatherService:
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # In your weather_service.py, replace the cameroon_cities section with:

        self.cameroon_cities = {
            'centre': 'Yaounde',
            'littoral': 'Douala', 
            'west': 'Bafoussam',
            'northwest': 'Bamenda',
            'southwest': 'Buea',
            'east': 'Bertoua',
            'north': 'Garoua',
            'far_north': 'Maroua',
            'adamawa': 'Ngaoundere',
            'south': 'Ebolowa'
        }
    
    def get_weather(self, region):
        city = self.cameroon_cities.get(region.lower())
        if not city:
            return {"error": "Unknown region: " + region}
        
        try:
            url = self.base_url + "/weather"
            params = {
                'q': city + ',CM',
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    'region': region,
                    'city': city,
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed']
                }
                return result
            else:
                return {"error": "API error: " + str(response.status_code)}
                
        except Exception as e:
            return {"error": "Failed to get weather: " + str(e)}

if __name__ == "__main__":
    weather = SimpleWeatherService()
    
    print("Testing weather service...")
    result = weather.get_weather('centre')
    print(json.dumps(result, indent=2))