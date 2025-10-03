import json
from weather_service import SimpleWeatherService
from fao_service import FAOService
from nasa_service import NASAService

class DataCoordinator:
    def __init__(self):
        self.weather_service = SimpleWeatherService()
        self.fao_service = FAOService()
        self.nasa_service = NASAService()
    
    def get_complete_agricultural_analysis(self, region, crop):
        """Get complete analysis combining all data sources"""
        
        print(f"Getting complete analysis for {crop} in {region}...")
        
        # Get data from all three services
        weather_data = self.weather_service.get_weather(region)
        fao_data = self.fao_service.get_crop_production(crop)
        nasa_data = self.nasa_service.get_agricultural_weather(region, crop)
        
        # Combine everything into comprehensive report
        analysis = {
            'region': region,
            'crop': crop,
            'current_weather': weather_data,
            'crop_production': fao_data,
            'agricultural_analysis': nasa_data,
            'integrated_recommendations': self.generate_integrated_recommendations(
                weather_data, fao_data, nasa_data, region, crop
            ),
            'data_sources': ['OpenWeatherMap', 'FAO Statistics', 'NASA POWER']
        }
        
        return analysis
    
    def generate_integrated_recommendations(self, weather_data, fao_data, nasa_data, region, crop):
        """Generate recommendations based on all data sources"""
        recommendations = []
        
        # Weather-based recommendations
        if 'error' not in weather_data:
            temp = weather_data.get('temperature', 0)
            humidity = weather_data.get('humidity', 0)
            
            if temp > 30:
                recommendations.append(f"High temperature ({temp}°C) - provide shade for {crop}")
            
            if humidity > 85:
                recommendations.append(f"High humidity ({humidity}%) - watch for diseases in {crop}")
        
        # Production trend recommendations
        if 'error' not in fao_data:
            trend = fao_data.get('trend', 'stable')
            if trend == 'increasing':
                recommendations.append(f"{crop.title()} production is growing - good market opportunity")
            elif trend == 'decreasing':
                recommendations.append(f"{crop.title()} production declining - consider diversification")
        
        # NASA climate recommendations
        if 'error' not in nasa_data:
            suitability = nasa_data.get('crop_suitability', 'unknown')
            if suitability == 'highly_suitable':
                recommendations.append(f"{crop.title()} is excellent choice for {region} region")
            elif suitability == 'challenging':
                recommendations.append(f"Consider alternatives to {crop} in {region} region")
            
            # Add NASA-specific advice
            crop_advice = nasa_data.get('crop_specific_advice', [])
            recommendations.extend(crop_advice[:2])  # Add top 2 NASA recommendations
        
        # Regional specialization advice
        regional_advice = self.get_regional_specialization_advice(region, crop)
        recommendations.extend(regional_advice)
        
        return recommendations
    
    def get_regional_specialization_advice(self, region, crop):
        """Get advice based on what each region is known for"""
        regional_specialties = {
            'centre': ['maize', 'cassava', 'plantain', 'vegetables'],
            'littoral': ['pineapple', 'banana', 'oil_palm', 'rice'],
            'west': ['coffee', 'beans', 'irish_potato', 'vegetables'],
            'northwest': ['beans', 'maize', 'vegetables', 'irish_potato'],
            'southwest': ['oil_palm', 'cocoa', 'banana', 'pepper'],
            'east': ['cassava', 'plantain', 'cocoa', 'maize'],
            'north': ['cotton', 'millet', 'sorghum', 'groundnuts'],
            'far_north': ['cotton', 'millet', 'onions', 'pepper'],
            'adamawa': ['maize', 'beans', 'groundnuts', 'irish_potato'],
            'south': ['cocoa', 'cassava', 'plantain', 'oil_palm']
        }
        
        advice = []
        specialties = regional_specialties.get(region.lower(), [])
        
        if crop.lower() in specialties:
            advice.append(f"{region.title()} region specializes in {crop} - you're in the right place!")
            advice.append("Connect with local farmers' cooperatives for best practices")
        else:
            advice.append(f"Consider {region}'s specialty crops: {', '.join(specialties[:3])}")
        
        return advice
    
    def get_farmer_dashboard(self, region, crops_list):
        """Get dashboard view for multiple crops"""
        dashboard = {
            'region': region,
            'crops_analysis': {},
            'region_weather_summary': self.weather_service.get_weather(region),
            'top_recommendations': []
        }
        
        all_recommendations = []
        
        for crop in crops_list:
            crop_analysis = self.get_complete_agricultural_analysis(region, crop)
            dashboard['crops_analysis'][crop] = crop_analysis
            
            # Collect recommendations
            recommendations = crop_analysis.get('integrated_recommendations', [])
            all_recommendations.extend(recommendations)
        
        # Get top 5 most important recommendations
        dashboard['top_recommendations'] = all_recommendations[:5]
        
        return dashboard

if __name__ == "__main__":
    coordinator = DataCoordinator()
    
    print("Testing Complete Agricultural Data Coordinator")
    print("=" * 60)
    
    # Test single crop analysis
    print("\n1. COMPLETE ANALYSIS - Maize in Centre Region:")
    result = coordinator.get_complete_agricultural_analysis('centre', 'maize')
    
    print(f"Region: {result['region']}")
    print(f"Crop: {result['crop']}")
    
    # Show current weather
    weather = result['current_weather']
    if 'error' not in weather:
        print(f"Current weather: {weather['temperature']}°C, {weather['description']}")
    
    # Show production info
    production = result['crop_production']
    if 'error' not in production:
        print(f"Production trend: {production.get('trend', 'Unknown')}")
    
    # Show NASA analysis
    nasa = result['agricultural_analysis']
    if 'error' not in nasa:
        print(f"Climate suitability: {nasa.get('crop_suitability', 'Unknown')}")
    
    print("\nIntegrated Recommendations:")
    recommendations = result['integrated_recommendations']
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"{i}. {rec}")
    
    # Test farmer dashboard
    print(f"\n\n2. FARMER DASHBOARD - Multiple Crops in West Region:")
    dashboard = coordinator.get_farmer_dashboard('west', ['coffee', 'beans', 'irish_potato'])
    
    weather_summary = dashboard['region_weather_summary']
    if 'error' not in weather_summary:
        print(f"Current conditions: {weather_summary['temperature']}°C, {weather_summary['description']}")
    
    print(f"\nCrops analyzed: {list(dashboard['crops_analysis'].keys())}")
    
    print("\nTop Recommendations:")
    for i, rec in enumerate(dashboard['top_recommendations'][:5], 1):
        print(f"{i}. {rec}")