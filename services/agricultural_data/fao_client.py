"""
FAO API Client
Location: agribot/services/agricultural_data/fao_client.py

Handles communication with FAO FAOSTAT API for agricultural statistics,
crop production data, and food security information for Cameroon.
"""

import requests
import time
from typing import Dict, Optional, List
from config.settings import APIConfig
from services.cache.redis_cache import RedisCache, cached
from utils.exceptions import APIServiceError

class FAOClient:
    """Client for FAO FAOSTAT API integration"""
    
    def __init__(self, config: APIConfig = None):
        self.config = config or APIConfig()
        self.base_url = self.config.fao_base_url
        self.cache = RedisCache()
        
        # Cameroon country code in FAO system
        self.country_code = "32"
        
        # FAO crop codes for crops grown in Cameroon
        self.crop_codes = {
            'maize': '56',
            'cassava': '125', 
            'plantain': '486',
            'cocoa': '661',
            'coffee': '656',
            'rice': '27',
            'yam': '136',
            'sweet_potato': '122',
            'groundnuts': '242',
            'beans': '176',
            'cotton': '328',
            'millet': '79',
            'sorghum': '83',
            'oil_palm': '254',
            'banana': '489',
            'pineapple': '574',
            'tomatoes': '388',
            'onions': '403',
            'pepper': '401'
        }
        
        # FAO element codes for different data types
        self.element_codes = {
            'production': '5510',
            'area_harvested': '5312',
            'yield': '5419',
            'import_quantity': '5610',
            'export_quantity': '5910'
        }
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make API request with error handling and retries"""
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
                            "FAO",
                            f"HTTP {response.status_code}: {response.text}",
                            response.status_code
                        )
                    
                # Wait before retrying
                time.sleep(2 ** attempt)
                    
            except requests.Timeout:
                if attempt == self.config.max_retries - 1:
                    raise APIServiceError(
                        "FAO",
                        "Request timeout after retries"
                    )
                time.sleep(2 ** attempt)
            except requests.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise APIServiceError(
                        "FAO", 
                        f"Request failed: {str(e)}"
                    )
                time.sleep(2 ** attempt)
        
        raise APIServiceError("FAO", "Max retries exceeded")
    
    @cached(timeout=86400, key_prefix="fao:production")  # Cache for 24 hours
    def get_crop_production_data(self, crop: str, year: int = 2020, 
                               element: str = 'production') -> Dict:
        """Get crop production data for Cameroon"""
        crop_lower = crop.lower()
        if crop_lower not in self.crop_codes:
            available_crops = ', '.join(self.crop_codes.keys())
            raise APIServiceError(
                "FAO",
                f"Unknown crop: {crop}. Available crops: {available_crops}"
            )
        
        if element not in self.element_codes:
            available_elements = ', '.join(self.element_codes.keys())
            raise APIServiceError(
                "FAO",
                f"Unknown element: {element}. Available: {available_elements}"
            )
        
        try:
            params = {
                'area_code': self.country_code,
                'item_code': self.crop_codes[crop_lower],
                'element_code': self.element_codes[element],
                'year': str(year)
            }
            
            data = self._make_request('data/QCL', params)
            
            if not data or 'data' not in data or not data['data']:
                # Return fallback data
                return self._get_fallback_production_data(crop, year, element)
            
            return self._process_fao_data(data['data'][0], crop, year, element)
            
        except APIServiceError:
            # Return fallback data if API fails
            return self._get_fallback_production_data(crop, year, element)
        except Exception as e:
            raise APIServiceError(
                "FAO",
                f"Failed to process production data: {str(e)}"
            )
    
    def _process_fao_data(self, raw_data: Dict, crop: str, year: int, element: str) -> Dict:
        """Process raw FAO data into standardized format"""
        try:
            value = float(raw_data.get('Value', 0)) if raw_data.get('Value') else 0
            unit = raw_data.get('Unit', 'tonnes')
            
            # Calculate trend (simplified - would need multiple years for real trend)
            trend = self._estimate_trend(crop, value)
            
            return {
                'crop': crop,
                'country': 'Cameroon',
                'year': year,
                'element': element,
                'value': value,
                'unit': unit,
                'trend': trend,
                'data_source': 'FAO FAOSTAT',
                'reliability': 'official'
            }
            
        except Exception as e:
            raise APIServiceError(
                "FAO",
                f"Failed to process FAO data: {str(e)}"
            )
    
    def _get_fallback_production_data(self, crop: str, year: int, element: str) -> Dict:
        """Provide fallback data when FAO API is unavailable"""
        # Realistic production estimates for Cameroon based on typical values
        fallback_data = {
            'production': {
                'maize': 2100000,      # tonnes
                'cassava': 5800000,
                'plantain': 4200000,
                'cocoa': 295000,
                'coffee': 25000,
                'rice': 120000,
                'yam': 580000,
                'sweet_potato': 240000,
                'groundnuts': 290000,
                'beans': 280000,
                'cotton': 150000,
                'oil_palm': 450000,
                'banana': 1200000,
                'tomatoes': 1250000
            },
            'area_harvested': {  # hectares
                'maize': 700000,
                'cassava': 950000,
                'plantain': 280000,
                'cocoa': 600000,
                'coffee': 180000
            }
        }
        
        # Get fallback value or default
        value = fallback_data.get(element, {}).get(crop.lower(), 100000)
        trend = self._estimate_trend(crop, value)
        
        return {
            'crop': crop,
            'country': 'Cameroon',
            'year': year,
            'element': element,
            'value': value,
            'unit': 'tonnes' if element == 'production' else 'hectares',
            'trend': trend,
            'data_source': 'Fallback estimates (FAO API unavailable)',
            'reliability': 'estimated',
            'note': 'This is estimated data - FAO API was unreachable'
        }
    
    def _estimate_trend(self, crop: str, current_value: float) -> str:
        """Estimate production trend based on crop and current value"""
        # Simplified trend estimation - in reality would need historical data
        growth_crops = ['maize', 'cassava', 'rice', 'tomatoes']
        stable_crops = ['cocoa', 'plantain', 'yam']
        declining_crops = ['coffee', 'cotton']
        
        if crop.lower() in growth_crops:
            return 'increasing'
        elif crop.lower() in stable_crops:
            return 'stable'
        elif crop.lower() in declining_crops:
            return 'decreasing'
        else:
            return 'stable'
    
    def get_multiple_crops_data(self, crops: List[str], year: int = 2020) -> Dict:
        """Get production data for multiple crops"""
        results = {}
        
        for crop in crops:
            try:
                crop_data = self.get_crop_production_data(crop, year)
                results[crop] = crop_data
            except APIServiceError as e:
                results[crop] = {
                    'crop': crop,
                    'error': str(e),
                    'data_source': 'Error'
                }
        
        return {
            'country': 'Cameroon',
            'year': year,
            'crops_data': results,
            'total_crops': len(crops),
            'successful_requests': len([r for r in results.values() if 'error' not in r])
        }
    
    def get_crop_comparison(self, crops: List[str], year: int = 2020) -> Dict:
        """Compare production values across multiple crops"""
        crops_data = self.get_multiple_crops_data(crops, year)
        
        # Extract production values for comparison
        production_comparison = []
        for crop, data in crops_data['crops_data'].items():
            if 'error' not in data:
                production_comparison.append({
                    'crop': crop,
                    'production': data.get('value', 0),
                    'trend': data.get('trend', 'unknown')
                })
        
        # Sort by production value
        production_comparison.sort(key=lambda x: x['production'], reverse=True)
        
        return {
            'country': 'Cameroon',
            'year': year,
            'comparison': production_comparison,
            'top_producer': production_comparison[0]['crop'] if production_comparison else None,
            'data_source': 'FAO FAOSTAT'
        }