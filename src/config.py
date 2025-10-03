import os

class Config:
    OPENWEATHER_API_KEY = "7af36f0d640659510c5735d7856f6413"
    CACHE_ENABLED = False
    LOG_LEVEL = "INFO"
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///agribot.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # For production, use PostgreSQL:
    # SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/agribot_db'

def test_config():
    if Config.OPENWEATHER_API_KEY == "your_api_key_here":
        print("Please add your OpenWeatherMap API key")
        return False
    else:
        print("API key configured!")
        print("Key: " + Config.OPENWEATHER_API_KEY)
        return True

if __name__ == "__main__":
    test_config()