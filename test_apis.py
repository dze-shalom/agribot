"""
Test all API keys to verify they're working
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def test_openweather_api():
    """Test OpenWeatherMap API"""
    api_key = os.getenv('OPENWEATHER_API_KEY')
    print("\n" + "="*60)
    print("TESTING OPENWEATHERMAP API")
    print("="*60)
    print(f"API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'NOT SET'}")

    if not api_key:
        print("❌ API key not configured")
        return False

    try:
        # Test with a simple weather request for Yaoundé, Cameroon
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': 'Yaounde,CM',
            'appid': api_key,
            'units': 'metric'
        }

        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS!")
            print(f"   Location: {data['name']}, {data['sys']['country']}")
            print(f"   Temperature: {data['main']['temp']}°C")
            print(f"   Weather: {data['weather'][0]['description']}")
            return True
        elif response.status_code == 401:
            print(f"❌ INVALID API KEY")
            print(f"   Response: {response.text}")
            return False
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False


def test_plant_id_api():
    """Test Plant.id API"""
    api_key = os.getenv('PLANT_ID_API_KEY')
    print("\n" + "="*60)
    print("TESTING PLANT.ID API")
    print("="*60)
    print(f"API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'NOT SET'}")

    if not api_key or api_key == 'your_plant_id_api_key_here':
        print("❌ API key not configured")
        return False

    try:
        # Test with Crop.Kindwise endpoint
        url = "https://crop.kindwise.com/api/v1/usage_info"
        headers = {
            'Api-Key': api_key
        }

        print(f"Testing endpoint: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS!")
            print(f"   Credits Used: {data.get('used', 0)}")
            print(f"   Credits Remaining: {data.get('remaining', 0)}")
            print(f"   Total Credits: {data.get('total', 0)}")
            return True
        elif response.status_code == 401:
            print(f"❌ INVALID API KEY")
            print(f"   Response: {response.text}")
            return False
        elif response.status_code == 402:
            print(f"⚠️  QUOTA EXCEEDED")
            print(f"   Response: {response.text}")
            return False
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False


def test_claude_api():
    """Test Claude API (Anthropic)"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    print("\n" + "="*60)
    print("TESTING CLAUDE API (ANTHROPIC)")
    print("="*60)

    if not api_key:
        print("⚠️  API key not configured (this is optional)")
        print("   The system works in basic NLP mode without it")
        return None

    print(f"API Key: {api_key[:15]}...{api_key[-5:]}")
    print("ℹ️  Claude API configured but not actively tested")
    print("   (We don't want to consume credits unnecessarily)")
    return None


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# AGRIBOT API KEY VERIFICATION")
    print("#"*60)

    results = {
        'OpenWeatherMap': test_openweather_api(),
        'Plant.id': test_plant_id_api(),
        'Claude (Anthropic)': test_claude_api()
    }

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    for api_name, status in results.items():
        if status is True:
            print(f"✅ {api_name}: WORKING")
        elif status is False:
            print(f"❌ {api_name}: FAILED")
        else:
            print(f"⚠️  {api_name}: NOT CONFIGURED")

    print("\n")
