"""
Geographic Data Model
Location: agribot/database/models/geographic.py

Defines models for storing geographic information about Cameroon regions,
climate zones, and agricultural suitability data.
"""

from database import db
from datetime import datetime, timezone
import json
from typing import List


class GeographicData(db.Model):
    """Geographic information for Cameroon regions and agricultural zones"""
    __tablename__ = 'geographic_data'
    
    # Primary identification
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50), nullable=False, unique=True)
    
    # Administrative divisions
    division = db.Column(db.String(100))
    subdivision = db.Column(db.String(100))
    city_town = db.Column(db.String(100))
    
    # Geographic coordinates
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    elevation = db.Column(db.Integer)  # meters above sea level
    
    # Climate and agricultural data
    climate_zone = db.Column(db.String(50))
    main_crops = db.Column(db.Text)  # JSON array of primary crops
    soil_types = db.Column(db.Text)  # JSON array of soil types
    rainfall_pattern = db.Column(db.String(50))  # bimodal, unimodal, etc.
    
    # Demographic information
    population = db.Column(db.Integer)
    agricultural_population_percent = db.Column(db.Float)
    
    # Economic indicators
    main_economic_activities = db.Column(db.Text)  # JSON array
    market_access_rating = db.Column(db.Integer)  # 1-5 scale
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<GeographicData {self.region} - {self.climate_zone}>'
    
    def get_main_crops(self) -> List[str]:
        """Get list of main crops for this region"""
        if self.main_crops:
            try:
                return json.loads(self.main_crops)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_main_crops(self, crops: List[str]):
        """Set the main crops list"""
        self.main_crops = json.dumps(crops)
    
    def get_soil_types(self) -> List[str]:
        """Get list of soil types for this region"""
        if self.soil_types:
            try:
                return json.loads(self.soil_types)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_soil_types(self, soils: List[str]):
        """Set the soil types list"""
        self.soil_types = json.dumps(soils)
    
    def get_economic_activities(self) -> List[str]:
        """Get list of main economic activities"""
        if self.main_economic_activities:
            try:
                return json.loads(self.main_economic_activities)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_economic_activities(self, activities: List[str]):
        """Set the economic activities list"""
        self.main_economic_activities = json.dumps(activities)
    
    def to_dict(self) -> dict:
        """Convert geographic data to dictionary"""
        return {
            'region': self.region,
            'division': self.division,
            'city_town': self.city_town,
            'coordinates': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'elevation': self.elevation
            },
            'climate_zone': self.climate_zone,
            'main_crops': self.get_main_crops(),
            'soil_types': self.get_soil_types(),
            'rainfall_pattern': self.rainfall_pattern,
            'population': self.population,
            'agricultural_population_percent': self.agricultural_population_percent,
            'economic_activities': self.get_economic_activities(),
            'market_access_rating': self.market_access_rating
        }

class ClimateData(db.Model):
    """Historical and seasonal climate data for regions"""
    __tablename__ = 'climate_data'
    
    # Primary key and geographic relationship
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50), db.ForeignKey('geographic_data.region'), nullable=False)
    
    # Time period
    month = db.Column(db.Integer, nullable=False)  # 1-12
    season = db.Column(db.String(20))  # dry, rainy, transition
    
    # Temperature data (Celsius)
    avg_temperature = db.Column(db.Float)
    min_temperature = db.Column(db.Float)
    max_temperature = db.Column(db.Float)
    
    # Precipitation data (mm)
    avg_rainfall = db.Column(db.Float)
    rainy_days = db.Column(db.Integer)
    
    # Humidity and other factors
    avg_humidity = db.Column(db.Float)
    avg_solar_radiation = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    
    # Agricultural calendar markers
    planting_season = db.Column(db.Boolean, default=False)
    harvesting_season = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ClimateData {self.region} - Month {self.month}>'