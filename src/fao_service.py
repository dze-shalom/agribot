import requests
import json
import time

class FAOService:
    def __init__(self):
        self.base_url = "https://fenixservices.fao.org/faostat/api/v1/en"
        self.country_code = "32"
        
        self.crop_codes = {
            'maize': '56',
            'cassava': '125',
            'plantain': '486',
            'cocoa': '661',
            'coffee': '656'
        }
    
    def get_crop_production(self, crop, year=2020):
        crop_code = self.crop_codes.get(crop.lower())
        if not crop_code:
            return {"error": "Crop not found: " + crop}
        
        # Try 3 times with increasing timeout
        for attempt in range(3):
            try:
                timeout = 10 + (attempt * 10)  # 10, 20, 30 seconds
                print(f"Attempt {attempt + 1} with {timeout}s timeout...")
                
                url = self.base_url + "/data/QCL"
                params = {
                    'area_code': self.country_code,
                    'item_code': crop_code,
                    'year': str(year),
                    'element_code': '5510'
                }
                
                response = requests.get(url, params=params, timeout=timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and data['data']:
                        processed_data = self.process_production_data(data['data'], crop, year)
                        return processed_data
                
                time.sleep(2)  # Wait 2 seconds between attempts
                
            except requests.Timeout:
                print(f"Timeout on attempt {attempt + 1}")
                if attempt == 2:  # Last attempt
                    return self.get_fallback_data(crop, year)
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
        
        return self.get_fallback_data(crop, year)
    
    def get_fallback_data(self, crop, year):
        """Provide fallback data when API is unavailable"""
        # Sample data based on typical Cameroon production
        fallback_data = {
            'maize': {'production': 2100000, 'trend': 'increasing'},
            'cassava': {'production': 5800000, 'trend': 'stable'},
            'plantain': {'production': 4200000, 'trend': 'increasing'},
            'cocoa': {'production': 295000, 'trend': 'stable'},
            'coffee': {'production': 25000, 'trend': 'decreasing'}
        }
        
        crop_info = fallback_data.get(crop.lower(), {'production': 100000, 'trend': 'stable'})
        
        return {
            'crop': crop,
            'country': 'Cameroon',
            'year': year,
            'production_tonnes': crop_info['production'],
            'trend': crop_info['trend'],
            'unit': 'tonnes',
            'data_source': 'Fallback data (FAO API unavailable)',
            'note': 'This is sample data - FAO API was unreachable'
        }
    
    def process_production_data(self, raw_data, crop, year):
        if not raw_data:
            return {"error": "No data to process"}
        
        item = raw_data[0]
        production_value = float(item['Value']) if item['Value'] else 0
        
        return {
            'crop': crop,
            'country': 'Cameroon',
            'year': year,
            'production_tonnes': production_value,
            'unit': item.get('Unit', 'tonnes'),
            'data_source': 'FAO Statistics'
        }

if __name__ == "__main__":
    fao = FAOService()
    
    print("Testing FAO Service with fallback...")
    print("=" * 40)
    
    result = fao.get_crop_production('maize', 2020)
    print("MAIZE PRODUCTION DATA:")
    print(json.dumps(result, indent=2))
    
    print("\nTesting other crops:")
    for crop in ['cassava', 'cocoa']:
        result = fao.get_crop_production(crop, 2020)
        print(f"\n{crop.upper()}:")
        print(f"Production: {result.get('production_tonnes', 'N/A')} tonnes")
        print(f"Source: {result.get('data_source', 'N/A')}")