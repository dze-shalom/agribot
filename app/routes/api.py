"""
API Routes
Location: agribot/app/routes/api.py

RESTful API endpoints for accessing agricultural data and services.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from knowledge.agricultural_knowledge import AgriculturalKnowledgeBase
from services.data_coordinator import DataCoordinator
from database.repositories.analytics_repository import AnalyticsRepository
from utils.exceptions import AgriBotException, APIServiceError
from utils.validators import validate_region, validate_crop

# Create blueprint
api_bp = Blueprint('api', __name__)

# Logger
logger = logging.getLogger(__name__)

@api_bp.route('/crops', methods=['GET'])
def get_crops():
    """Get list of supported crops"""
    try:
        knowledge_base = AgriculturalKnowledgeBase()
        crops = knowledge_base.get_all_crops()
        
        return jsonify({
            'success': True,
            'data': {
                'crops': crops,
                'total_count': len(crops)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting crops: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve crops list'
        }), 500

@api_bp.route('/crops/<crop_name>', methods=['GET'])
def get_crop_info(crop_name):
    """Get comprehensive information about a specific crop"""
    try:
        # Validate crop
        if not validate_crop(crop_name):
            return jsonify({
                'success': False,
                'error': f'Invalid or unsupported crop: {crop_name}'
            }), 400
        
        knowledge_base = AgriculturalKnowledgeBase()
        crop_info = knowledge_base.get_comprehensive_crop_info(crop_name)
        
        if 'error' in crop_info:
            return jsonify({
                'success': False,
                'error': crop_info['error']
            }), 404
        
        return jsonify({
            'success': True,
            'data': crop_info
        })
        
    except Exception as e:
        logger.error(f"Error getting crop info for {crop_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve crop information'
        }), 500

@api_bp.route('/crops/<crop_name>/diseases', methods=['GET'])
def get_crop_diseases(crop_name):
    """Get disease information for a specific crop"""
    try:
        # Validate crop
        if not validate_crop(crop_name):
            return jsonify({
                'success': False,
                'error': f'Invalid crop: {crop_name}'
            }), 400
        
        knowledge_base = AgriculturalKnowledgeBase()
        
        # Check for specific disease query
        disease_name = request.args.get('disease')
        
        if disease_name:
            disease_info = knowledge_base.get_disease_info(crop_name, disease_name)
        else:
            disease_info = knowledge_base.get_disease_info(crop_name)
        
        if 'error' in disease_info:
            return jsonify({
                'success': False,
                'error': disease_info['error']
            }), 404
        
        return jsonify({
            'success': True,
            'data': disease_info
        })
        
    except Exception as e:
        logger.error(f"Error getting diseases for {crop_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve disease information'
        }), 500

@api_bp.route('/crops/<crop_name>/fertilizer', methods=['GET'])
def get_crop_fertilizer(crop_name):
    """Get fertilizer recommendations for a specific crop"""
    try:
        # Validate crop
        if not validate_crop(crop_name):
            return jsonify({
                'success': False,
                'error': f'Invalid crop: {crop_name}'
            }), 400
        
        knowledge_base = AgriculturalKnowledgeBase()
        
        # Check for specific growth stage
        growth_stage = request.args.get('stage', 'all')
        
        fertilizer_info = knowledge_base.get_fertilizer_recommendation(crop_name, growth_stage)
        
        return jsonify({
            'success': True,
            'data': fertilizer_info
        })
        
    except Exception as e:
        logger.error(f"Error getting fertilizer info for {crop_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve fertilizer information'
        }), 500

@api_bp.route('/regions', methods=['GET'])
def get_regions():
    """Get list of supported regions"""
    try:
        regions = [
            'centre', 'littoral', 'west', 'northwest', 'southwest',
            'east', 'north', 'far_north', 'adamawa', 'south'
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'regions': regions,
                'total_count': len(regions)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting regions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve regions list'
        }), 500

@api_bp.route('/regions/<region_name>/weather', methods=['GET'])
def get_region_weather(region_name):
    """Get weather information for a specific region"""
    try:
        # Validate region
        if not validate_region(region_name):
            return jsonify({
                'success': False,
                'error': f'Invalid region: {region_name}'
            }), 400
        
        # Get data coordinator from app context
        data_coordinator = request.current_app.data_coordinator
        
        # Get optional crop parameter
        crop = request.args.get('crop')
        include_forecast = request.args.get('include_forecast', 'false').lower() == 'true'
        
        # Get weather analysis
        weather_analysis = data_coordinator.get_comprehensive_analysis(
            region=region_name,
            crop=crop,
            include_forecast=include_forecast
        )
        
        if 'error' in weather_analysis:
            return jsonify({
                'success': False,
                'error': weather_analysis['error']
            }), 500
        
        return jsonify({
            'success': True,
            'data': weather_analysis
        })
        
    except APIServiceError as e:
        logger.warning(f"API service error for weather in {region_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Weather service temporarily unavailable: {str(e)}',
            'error_type': 'api_service_error'
        }), 503
        
    except Exception as e:
        logger.error(f"Error getting weather for {region_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve weather information'
        }), 500

@api_bp.route('/analysis/comprehensive', methods=['GET'])
def get_comprehensive_analysis():
    """Get comprehensive agricultural analysis for region and crop"""
    try:
        # Get parameters
        region = request.args.get('region')
        crop = request.args.get('crop')
        include_forecast = request.args.get('include_forecast', 'false').lower() == 'true'
        
        if not region:
            return jsonify({
                'success': False,
                'error': 'Region parameter is required'
            }), 400
        
        # Validate region
        if not validate_region(region):
            return jsonify({
                'success': False,
                'error': f'Invalid region: {region}'
            }), 400
        
        # Validate crop if provided
        if crop and not validate_crop(crop):
            return jsonify({
                'success': False,
                'error': f'Invalid crop: {crop}'
            }), 400
        
        # Get data coordinator
        data_coordinator = request.current_app.data_coordinator
        
        # Get comprehensive analysis
        analysis = data_coordinator.get_comprehensive_analysis(
            region=region,
            crop=crop,
            include_forecast=include_forecast
        )
        
        if 'error' in analysis:
            return jsonify({
                'success': False,
                'error': analysis['error']
            }), 500
        
        return jsonify({
            'success': True,
            'data': analysis
        })
        
    except APIServiceError as e:
        logger.warning(f"API service error in comprehensive analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'External data services temporarily unavailable: {str(e)}',
            'error_type': 'api_service_error'
        }), 503
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve comprehensive analysis'
        }), 500

@api_bp.route('/compare/regions', methods=['GET'])
def compare_regions():
    """Compare multiple regions for crop suitability"""
    try:
        # Get parameters
        regions_param = request.args.get('regions')
        crop = request.args.get('crop')
        
        if not regions_param:
            return jsonify({
                'success': False,
                'error': 'Regions parameter is required (comma-separated list)'
            }), 400
        
        # Parse regions
        regions = [region.strip() for region in regions_param.split(',')]
        
        # Validate regions
        for region in regions:
            if not validate_region(region):
                return jsonify({
                    'success': False,
                    'error': f'Invalid region: {region}'
                }), 400
        
        # Validate crop if provided
        if crop and not validate_crop(crop):
            return jsonify({
                'success': False,
                'error': f'Invalid crop: {crop}'
            }), 400
        
        # Get data coordinator
        data_coordinator = request.current_app.data_coordinator
        
        # Compare regions
        comparison = data_coordinator.get_multi_region_comparison(regions, crop)
        
        return jsonify({
            'success': True,
            'data': comparison
        })
        
    except Exception as e:
        logger.error(f"Error comparing regions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to compare regions'
        }), 500

@api_bp.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get analytics summary (public metrics only)"""
    try:
        analytics_repo = AnalyticsRepository()
        
        # Get basic analytics without sensitive data
        analytics = analytics_repo.get_comprehensive_analytics(days=30)
        
        # Filter to public metrics only
        public_metrics = {
            'total_conversations': analytics['overview']['total_conversations'],
            'total_messages': analytics['overview']['total_messages'],
            'average_rating': analytics['satisfaction']['avg_overall_rating'],
            'satisfaction_rate': analytics['satisfaction']['satisfaction_rate'],
            'period_days': analytics['period_days']
        }
        
        return jsonify({
            'success': True,
            'data': public_metrics
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve analytics summary'
        }), 500

# ============================================
# KNOWLEDGE BASE ENDPOINTS FOR OFFLINE CACHING
# ============================================

@api_bp.route('/knowledge/crops', methods=['GET'])
def get_knowledge_crops():
    """Get all crops information for offline caching"""
    try:
        knowledge_base = AgriculturalKnowledgeBase()
        crops = knowledge_base.get_all_crops()

        return jsonify({
            'success': True,
            'items': crops,
            'category': 'crops',
            'cached_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting knowledge crops: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve crops knowledge'
        }), 500

@api_bp.route('/knowledge/diseases', methods=['GET'])
def get_knowledge_diseases():
    """Get all diseases information for offline caching"""
    try:
        knowledge_base = AgriculturalKnowledgeBase()
        # Get diseases for common crops
        common_crops = ['maize', 'cassava', 'cocoa', 'coffee', 'plantain']
        diseases = []

        for crop in common_crops:
            crop_diseases = knowledge_base.get_disease_info(crop)
            if 'diseases' in crop_diseases:
                for disease in crop_diseases['diseases']:
                    disease['crop'] = crop
                    diseases.append(disease)

        return jsonify({
            'success': True,
            'items': diseases,
            'category': 'diseases',
            'cached_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting knowledge diseases: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve diseases knowledge'
        }), 500

@api_bp.route('/knowledge/best-practices', methods=['GET'])
def get_knowledge_best_practices():
    """Get agricultural best practices for offline caching"""
    try:
        knowledge_base = AgriculturalKnowledgeBase()

        practices = [
            {
                'topic': 'soil-preparation',
                'title': 'Soil Preparation',
                'practices': [
                    'Clear land of weeds and debris',
                    'Test soil pH and nutrients',
                    'Add organic matter/compost',
                    'Ensure proper drainage',
                    'Till soil to appropriate depth'
                ]
            },
            {
                'topic': 'planting',
                'title': 'Planting Techniques',
                'practices': [
                    'Plant at optimal spacing',
                    'Use quality seeds or seedlings',
                    'Plant at the right depth',
                    'Consider companion planting',
                    'Water immediately after planting'
                ]
            },
            {
                'topic': 'irrigation',
                'title': 'Water Management',
                'practices': [
                    'Water early morning or evening',
                    'Use drip irrigation when possible',
                    'Mulch to retain moisture',
                    'Avoid overwatering',
                    'Monitor soil moisture regularly'
                ]
            },
            {
                'topic': 'fertilization',
                'title': 'Fertilizer Application',
                'practices': [
                    'Use balanced NPK ratios',
                    'Apply organic fertilizers',
                    'Follow recommended rates',
                    'Time applications with growth stages',
                    'Avoid fertilizer burn'
                ]
            },
            {
                'topic': 'pest-management',
                'title': 'Integrated Pest Management',
                'practices': [
                    'Regular field monitoring',
                    'Use resistant varieties',
                    'Practice crop rotation',
                    'Employ biological control',
                    'Use pesticides as last resort'
                ]
            }
        ]

        return jsonify({
            'success': True,
            'items': practices,
            'category': 'best-practices',
            'cached_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting best practices: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve best practices'
        }), 500

@api_bp.route('/knowledge/seasonal-calendar', methods=['GET'])
def get_knowledge_seasonal_calendar():
    """Get seasonal planting calendar for offline caching"""
    try:
        calendar = {
            'rainy_season': {
                'months': ['March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'],
                'crops': ['Maize', 'Cassava', 'Plantain', 'Yam', 'Groundnut', 'Rice'],
                'activities': ['Land preparation', 'Planting', 'Weeding', 'First harvest']
            },
            'dry_season': {
                'months': ['November', 'December', 'January', 'February'],
                'crops': ['Vegetables', 'Irrigated crops', 'Tree crops maintenance'],
                'activities': ['Harvest storage crops', 'Irrigation management', 'Soil preparation']
            }
        }

        return jsonify({
            'success': True,
            'items': calendar,
            'category': 'seasonal-calendar',
            'cached_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting seasonal calendar: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve seasonal calendar'
        }), 500

@api_bp.route('/knowledge/<category>', methods=['GET'])
def get_knowledge_category(category):
    """Generic endpoint for other knowledge categories"""
    try:
        # Map categories to basic data
        knowledge_data = {
            'pests': {
                'items': [
                    {'name': 'Aphids', 'description': 'Small sap-sucking insects', 'control': 'Neem oil, insecticidal soap'},
                    {'name': 'Caterpillars', 'description': 'Larvae that eat leaves', 'control': 'Handpicking, Bt spray'},
                    {'name': 'Mites', 'description': 'Tiny spider-like pests', 'control': 'Water spray, predatory mites'}
                ]
            },
            'soil-management': {
                'items': [
                    {'topic': 'composting', 'description': 'Creating organic fertilizer from waste'},
                    {'topic': 'mulching', 'description': 'Covering soil to retain moisture'},
                    {'topic': 'cover-cropping', 'description': 'Growing crops to improve soil'}
                ]
            },
            'irrigation': {
                'items': [
                    {'method': 'Drip', 'efficiency': 'High', 'description': 'Water delivered directly to roots'},
                    {'method': 'Sprinkler', 'efficiency': 'Medium', 'description': 'Overhead water distribution'},
                    {'method': 'Furrow', 'efficiency': 'Low', 'description': 'Water flows in channels'}
                ]
            },
            'fertilizers': {
                'items': [
                    {'type': 'NPK', 'nutrients': 'Nitrogen, Phosphorus, Potassium', 'use': 'General growth'},
                    {'type': 'Compost', 'nutrients': 'Balanced organic', 'use': 'Soil improvement'},
                    {'type': 'Urea', 'nutrients': 'High nitrogen', 'use': 'Leaf growth'}
                ]
            },
            'weather-tips': {
                'items': [
                    {'condition': 'Drought', 'action': 'Mulch heavily, use drought-resistant varieties'},
                    {'condition': 'Heavy rain', 'action': 'Ensure drainage, protect young plants'},
                    {'condition': 'Wind', 'action': 'Stake tall plants, use windbreaks'}
                ]
            },
            'market-info': {
                'items': [
                    {'tip': 'Harvest at peak quality', 'benefit': 'Better prices'},
                    {'tip': 'Store properly', 'benefit': 'Reduced losses'},
                    {'tip': 'Know market days', 'benefit': 'Sell when demand is high'}
                ]
            }
        }

        if category in knowledge_data:
            return jsonify({
                'success': True,
                **knowledge_data[category],
                'category': category,
                'cached_at': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown knowledge category: {category}'
            }), 404

    except Exception as e:
        logger.error(f"Error getting knowledge category {category}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve {category} knowledge'
        }), 500

@api_bp.errorhandler(404)
def api_not_found(error):
    """Handle 404 errors for API routes"""
    return jsonify({
        'success': False,
        'error': 'API endpoint not found'
    }), 404

@api_bp.errorhandler(405)
def api_method_not_allowed(error):
    """Handle 405 errors for API routes"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed for this endpoint'
    }), 405