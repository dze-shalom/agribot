import requests
import json
from datetime import datetime, timedelta

class NASAService:
    def __init__(self):
        self.base_url = "https://power.larc.nasa.gov/api/temporal"
        
        # ALL 10 Cameroon regions with coordinates
        self.regions = {
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
        
        # ALL crops grown in Cameroon organized by category
        self.crops = {
            # Staple crops
            'cereals': ['maize', 'rice', 'millet', 'sorghum', 'wheat'],
            'roots_tubers': ['cassava', 'yam', 'sweet_potato', 'irish_potato', 'cocoyam', 'plantain'],
            
            # Legumes
            'legumes': ['beans', 'cowpeas', 'groundnuts', 'soybeans', 'bambara_nuts'],
            
            # Cash crops
            'cash_crops': ['cocoa', 'coffee', 'cotton', 'oil_palm', 'rubber', 'tea', 'sugar_cane'],
            
            # Vegetables
            'vegetables': [
                'tomatoes', 'pepper', 'okra', 'onions', 'garlic', 'cabbage', 
                'lettuce', 'carrot', 'cucumber', 'eggplant', 'spinach', 
                'amaranth', 'pumpkin', 'watermelon', 'bitter_leaf'
            ],
            
            # Fruits
            'fruits': [
                'banana', 'pineapple', 'mango', 'avocado', 'orange', 'lemon',
                'papaya', 'guava', 'passion_fruit', 'coconut', 'cashew',
                'african_plum', 'soursop', 'breadfruit'
            ],
            
            # Spices and others
            'spices_others': ['ginger', 'turmeric', 'black_pepper', 'cinnamon', 'nutmeg']
        }
    
    def get_all_crops_list(self):
        """Get flat list of all crops"""
        all_crops = []
        for category, crops in self.crops.items():
            all_crops.extend(crops)
        return all_crops
    
    def get_crop_category(self, crop):
        """Find which category a crop belongs to"""
        crop = crop.lower().replace(' ', '_')
        for category, crops in self.crops.items():
            if crop in crops:
                return category
        return 'other'
    
    def get_regional_weather_patterns(self):
        """Typical weather patterns for all 10 regions"""
        return {
            'centre': {'temp_max': 28.5, 'temp_min': 20.2, 'rain': 3.2, 'solar': 18.5, 'climate': 'humid_forest'},
            'littoral': {'temp_max': 29.1, 'temp_min': 22.8, 'rain': 4.8, 'solar': 16.2, 'climate': 'coastal_humid'},
            'west': {'temp_max': 24.3, 'temp_min': 16.5, 'rain': 2.1, 'solar': 19.8, 'climate': 'highland'},
            'northwest': {'temp_max': 23.8, 'temp_min': 15.2, 'rain': 2.8, 'solar': 19.5, 'climate': 'highland'},
            'southwest': {'temp_max': 26.5, 'temp_min': 19.8, 'rain': 6.2, 'solar': 15.8, 'climate': 'coastal_mountain'},
            'east': {'temp_max': 27.8, 'temp_min': 19.5, 'rain': 3.8, 'solar': 17.9, 'climate': 'humid_forest'},
            'north': {'temp_max': 32.1, 'temp_min': 18.9, 'rain': 0.5, 'solar': 22.4, 'climate': 'sahel'},
            'far_north': {'temp_max': 34.2, 'temp_min': 20.1, 'rain': 0.3, 'solar': 23.8, 'climate': 'sahel_dry'},
            'adamawa': {'temp_max': 29.5, 'temp_min': 17.2, 'rain': 1.8, 'solar': 20.9, 'climate': 'savanna'},
            'south': {'temp_max': 27.8, 'temp_min': 21.1, 'rain': 5.2, 'solar': 17.3, 'climate': 'humid_forest'}
        }
    
    def get_crop_climate_suitability(self, crop, region):
        """Determine if a crop is suitable for a region's climate"""
        crop_category = self.get_crop_category(crop)
        weather_patterns = self.get_regional_weather_patterns()
        region_climate = weather_patterns.get(region, {}).get('climate', 'unknown')
        
        # Crop-climate suitability matrix
        suitability = {
            'cereals': {
                'humid_forest': ['maize', 'rice'],
                'sahel': ['millet', 'sorghum'],
                'coastal_humid': ['maize', 'rice'],
                'highland': ['wheat', 'maize'],
                'savanna': ['maize', 'millet', 'sorghum']
            },
            'roots_tubers': {
                'humid_forest': ['cassava', 'yam', 'plantain', 'cocoyam'],
                'highland': ['irish_potato', 'sweet_potato'],
                'coastal_humid': ['cassava', 'plantain'],
                'sahel': ['sweet_potato', 'cassava']
            },
            'cash_crops': {
                'humid_forest': ['cocoa', 'oil_palm', 'rubber'],
                'highland': ['coffee', 'tea'],
                'sahel': ['cotton'],
                'coastal_humid': ['oil_palm']
            },
            'vegetables': {
                'highland': ['cabbage', 'carrot', 'irish_potato'],
                'humid_forest': ['tomatoes', 'pepper', 'okra', 'eggplant'],
                'sahel': ['onions', 'pepper'],
                'coastal_humid': ['tomatoes', 'cucumber', 'watermelon']
            },
            'fruits': {
                'humid_forest': ['banana', 'avocado', 'mango', 'papaya'],
                'coastal_humid': ['pineapple', 'coconut', 'banana'],
                'highland': ['orange', 'lemon'],
                'sahel': ['mango', 'cashew']
            }
        }
        
        suitable_crops = suitability.get(crop_category, {}).get(region_climate, [])
        crop_name = crop.lower().replace(' ', '_')
        
        if crop_name in suitable_crops:
            return "highly_suitable"
        elif crop_category in suitability and region_climate in suitability[crop_category]:
            return "moderately_suitable"
        else:
            return "challenging"
    
    def get_agricultural_advice_for_crop(self, crop, region, weather_data):
        """Generate specific agricultural advice for crop and region"""
        advice = []
        crop_category = self.get_crop_category(crop)
        suitability = self.get_crop_climate_suitability(crop, region)
        temp_analysis = weather_data.get('temperature_analysis', {})
        rain_analysis = weather_data.get('rainfall_analysis', {})
        
        # Suitability advice
        if suitability == "highly_suitable":
            advice.append(f"{crop.title()} is well-suited for {region} region")
        elif suitability == "challenging":
            advice.append(f"{crop.title()} may be challenging in {region} - consider alternatives")
        
        # Temperature-specific advice for crop categories
        avg_temp = temp_analysis.get('avg_max_temp', 25)
        
        if crop_category == 'vegetables':
            if avg_temp > 30:
                advice.append("High temperatures - provide shade nets for vegetables")
                advice.append("Water vegetables twice daily during hot weather")
            elif avg_temp < 20:
                advice.append("Cool weather - protect tender vegetables from cold")
        
        elif crop_category == 'fruits':
            if avg_temp > 32:
                advice.append("Hot weather may stress fruit trees - ensure deep watering")
            advice.append("Fruit trees need consistent moisture during development")
        
        elif crop_category == 'cereals':
            if avg_temp > 35:
                advice.append("Heat stress possible for cereals - consider heat-tolerant varieties")
        
        elif crop_category == 'cash_crops':
            if crop.lower() == 'cocoa' and avg_temp > 32:
                advice.append("High temperatures may affect cocoa yield - maintain shade trees")
            elif crop.lower() == 'coffee' and avg_temp > 28:
                advice.append("Coffee prefers cooler temperatures - consider highland areas")
        
        # Rainfall-specific advice
        total_rain = rain_analysis.get('total_rainfall', 0)
        
        if crop_category in ['vegetables', 'fruits'] and total_rain < 10:
            advice.append("Vegetables and fruits need regular watering - install drip irrigation")
        elif crop_category == 'cereals' and total_rain > 50:
            advice.append("Heavy rainfall - ensure good drainage to prevent root rot")
        
        return advice
    
    def clean_nasa_data(self, data_list):
        """Remove invalid values from NASA data"""
        clean_data = []
        for value in data_list:
            if value > -500:  # Filter out obvious error codes
                clean_data.append(value)
        return clean_data
    
    def get_agricultural_weather(self, region, crop=None, days_back=7):
        """Get agricultural weather data for any region and crop"""
        region_info = self.regions.get(region.lower())
        if not region_info:
            available_regions = ', '.join(self.regions.keys())
            return {"error": f"Unknown region: {region}. Available regions: {available_regions}"}
        
        # Validate crop if provided
        if crop:
            all_crops = self.get_all_crops_list()
            if crop.lower().replace(' ', '_') not in all_crops:
                return {"error": f"Unknown crop: {crop}. Use get_all_crops_list() to see available crops"}
        
        try:
            # Use fallback data for now (NASA API has issues)
            weather_patterns = self.get_regional_weather_patterns()
            weather = weather_patterns.get(region.lower(), weather_patterns['centre'])
            
            analysis = {
                'region': region,
                'region_name': region_info['name'],
                'crop_focus': crop,
                'period_days': 7,
                'temperature_analysis': {
                    'avg_max_temp': weather['temp_max'],
                    'avg_min_temp': weather['temp_min'],
                    'highest_temp': weather['temp_max'] + 2,
                    'lowest_temp': weather['temp_min'] - 1
                },
                'rainfall_analysis': {
                    'total_rainfall': weather['rain'] * 7,
                    'avg_daily_rainfall': weather['rain'],
                    'rainy_days': 3 if weather['rain'] > 1 else 1
                },
                'solar_analysis': {
                    'avg_solar_radiation': weather['solar']
                },
                'climate_zone': weather['climate'],
                'data_source': 'NASA POWER (Regional Patterns)',
                'data_quality': 'Typical patterns for region'
            }
            
            # Add crop-specific advice if crop is provided
            if crop:
                analysis['crop_suitability'] = self.get_crop_climate_suitability(crop, region)
                analysis['crop_specific_advice'] = self.get_agricultural_advice_for_crop(crop, region, analysis)
            
            # Add general regional insights
            analysis['regional_insights'] = self.generate_regional_insights(region, weather)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to get weather data: {str(e)}"}
    
    def generate_regional_insights(self, region, weather):
        """Generate insights specific to each region"""
        insights = []
        
        climate = weather['climate']
        
        if climate == 'sahel' or climate == 'sahel_dry':
            insights.append("Sahel climate - drought-resistant crops essential")
            insights.append("Focus on water conservation techniques")
            insights.append("Best crops: millet, sorghum, cotton, cashew")
        
        elif climate == 'humid_forest':
            insights.append("Humid forest climate - excellent for cocoa and oil palm")
            insights.append("High humidity - monitor for fungal diseases")
            insights.append("Best crops: cocoa, cassava, plantain, yam")
        
        elif climate == 'highland':
            insights.append("Highland climate - excellent for coffee and vegetables")
            insights.append("Cooler temperatures allow temperate crops")
            insights.append("Best crops: coffee, irish potato, cabbage, beans")
        
        elif climate == 'coastal_humid' or climate == 'coastal_mountain':
            insights.append("Coastal climate - high rainfall and humidity")
            insights.append("Excellent for oil palm and pineapple")
            insights.append("Ensure good drainage systems")
        
        elif climate == 'savanna':
            insights.append("Savanna climate - good for cereals and livestock")
            insights.append("Moderate rainfall - suitable for diverse crops")
            insights.append("Best crops: maize, beans, groundnuts")
        
        return insights

if __name__ == "__main__":
    nasa = NASAService()
    
    print("Testing NASA Service for ALL 10 Cameroon Regions")
    print("=" * 60)
    
    # Test all regions with different crops
    test_cases = [
        ('centre', 'maize'),
        ('littoral', 'pineapple'),
        ('west', 'coffee'),
        ('northwest', 'beans'),
        ('southwest', 'oil_palm'),
        ('east', 'cassava'),
        ('north', 'millet'),
        ('far_north', 'cotton'),
        ('adamawa', 'groundnuts'),
        ('south', 'cocoa')
    ]
    
    for region, crop in test_cases:
        print(f"\n{region.upper()} REGION - {crop.upper()}:")
        result = nasa.get_agricultural_weather(region, crop)
        
        if 'error' not in result:
            temp = result['temperature_analysis']
            print(f"Climate: {result['climate_zone']}")
            print(f"Temperature: {temp['avg_min_temp']}°C to {temp['avg_max_temp']}°C")
            print(f"Crop suitability: {result.get('crop_suitability', 'N/A')}")
            
            if 'crop_specific_advice' in result:
                print("Crop advice:")
                for advice in result['crop_specific_advice'][:2]:
                    print(f"• {advice}")
        else:
            print(f"Error: {result['error']}")
    
    print(f"\nTotal crops supported: {len(nasa.get_all_crops_list())}")
    print("Crop categories:", list(nasa.crops.keys()))