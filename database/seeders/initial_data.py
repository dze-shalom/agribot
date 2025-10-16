# database/seeders/initial_data.py
"""
Seed initial data for AgriBot database
"""

from werkzeug.security import generate_password_hash
from database.models.user import User
from database.models.crop_knowledge import CropKnowledge
from database import db_session
from datetime import datetime

def seed_initial_data():
    """Seed the database with initial data"""
    
    # Create admin user
    admin_data = {
        'name': 'System Administrator',
        'email': 'admin@agribot.cm',
        'password_hash': generate_password_hash('admin123'),
        'phone': '+237123456789',
        'region': 'centre',
        'account_type': 'admin',
        'status': 'active',
        'created_at': datetime.utcnow()
    }
    
    if not User.get_by_email(admin_data['email']):
        admin_user = User.create(admin_data)
        print(f"Created admin user: {admin_user.email}")
    
    # Create demo farmer user
    farmer_data = {
        'name': 'Demo Farmer',
        'email': 'farmer@test.cm',
        'password_hash': generate_password_hash('farmer123'),
        'phone': '+237987654321',
        'region': 'littoral',
        'account_type': 'user',
        'status': 'active',
        'created_at': datetime.utcnow()
    }
    
    if not User.get_by_email(farmer_data['email']):
        farmer_user = User.create(farmer_data)
        print(f"Created demo farmer: {farmer_user.email}")
    
    # Seed crop knowledge
    crops_data = [
        {
            'crop_name': 'Maize',
            'scientific_name': 'Zea mays',
            'region_suitability': ['centre', 'littoral', 'west', 'northwest', 'southwest'],
            'planting_seasons': {
                'rainy_season': 'March-June',
                'dry_season': 'September-December (with irrigation)'
            },
            'growth_requirements': {
                'soil_type': 'Well-drained, fertile soils',
                'ph_range': '6.0-7.5',
                'rainfall': '500-800mm during growing season',
                'temperature': '20-30°C'
            },
            'common_diseases': [
                'Maize streak virus',
                'Maize lethal necrosis',
                'Gray leaf spot',
                'Northern corn leaf blight'
            ],
            'common_pests': [
                'Fall armyworm',
                'Stem borers',
                'Aphids',
                'Termites'
            ],
            'harvesting_info': {
                'maturity_period': '90-120 days',
                'harvest_indicators': 'Dry husks, hard kernels',
                'storage_tips': 'Dry to 13-14% moisture content'
            }
        },
        {
            'crop_name': 'Cassava',
            'scientific_name': 'Manihot esculenta',
            'region_suitability': ['centre', 'littoral', 'west', 'east', 'south'],
            'planting_seasons': {
                'optimal': 'Beginning of rainy season (March-May)',
                'alternative': 'Can be planted year-round with adequate water'
            },
            'growth_requirements': {
                'soil_type': 'Well-drained, sandy loam',
                'ph_range': '5.5-6.5',
                'rainfall': '1000-1500mm annually',
                'temperature': '25-35°C'
            },
            'common_diseases': [
                'Cassava mosaic disease',
                'Cassava brown streak disease',
                'Bacterial blight',
                'Root rot'
            ],
            'common_pests': [
                'Cassava mealybug',
                'Green spider mite',
                'Variegated grasshopper',
                'Termites'
            ],
            'harvesting_info': {
                'maturity_period': '8-24 months',
                'harvest_indicators': 'Yellowing leaves, root size',
                'storage_tips': 'Process within 48 hours or store in sand'
            }
        },
        {
            'crop_name': 'Cocoa',
            'scientific_name': 'Theobroma cacao',
            'region_suitability': ['littoral', 'centre', 'southwest', 'south'],
            'planting_seasons': {
                'optimal': 'Beginning of rainy season (March-April)',
                'nursery': 'Year-round with proper care'
            },
            'growth_requirements': {
                'soil_type': 'Deep, well-drained, rich in organic matter',
                'ph_range': '6.0-7.0',
                'rainfall': '1500-2000mm annually',
                'temperature': '18-32°C',
                'shade': 'Requires 50-70% shade when young'
            },
            'common_diseases': [
                'Black pod disease',
                'Witches broom',
                'Frosty pod rot',
                'Vascular streak dieback'
            ],
            'common_pests': [
                'Cocoa pod borer',
                'Mirids',
                'Thrips',
                'Mealybugs'
            ],
            'harvesting_info': {
                'maturity_period': '3-5 years to first harvest',
                'harvest_indicators': 'Pod color change, sound when tapped',
                'storage_tips': 'Ferment and dry beans properly'
            }
        }
    ]
    
    for crop_data in crops_data:
        existing_crop = CropKnowledge.get_by_name(crop_data['crop_name'])
        if not existing_crop:
            crop = CropKnowledge.create(crop_data)
            print(f"Created crop knowledge for: {crop.crop_name}")
    
    print("Initial data seeding completed!")
