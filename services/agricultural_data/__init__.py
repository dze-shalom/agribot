"""
Agricultural Data Services Package
Location: agribot/services/agricultural_data/__init__.py

Provides access to external agricultural data sources including
FAO statistics and NASA climate data.
"""

from .fao_client import FAOClient
from .nasa_client import NASAClient

__all__ = ['FAOClient', 'NASAClient']