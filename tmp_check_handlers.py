import json
from importlib import import_module

# Use the Flask app factory so we have an application context for DB access
from app.main import create_app

app = create_app()

print('Calling AnalyticsRepository.get_comprehensive_analytics inside app context...')
with app.app_context():
    try:
        from database.repositories.analytics_repository import AnalyticsRepository
        analytics = AnalyticsRepository.get_comprehensive_analytics(days=7)
        print('OK: analytics keys:', list(analytics.keys()))
        print(json.dumps(analytics.get('overview', {}), indent=2))
    except Exception as e:
        print('Analytics call failed:', repr(e))

print('\nCalling compatibility endpoints via test client...')
with app.test_client() as client:
    try:
        resp = client.get('/api/analytics')
        print('/api/analytics ->', resp.status_code)
        print(resp.get_data(as_text=True))
    except Exception as e:
        print('/api/analytics request failed:', repr(e))

    try:
        resp = client.get('/api/nlp-stats')
        print('/api/nlp-stats ->', resp.status_code)
        print(resp.get_data(as_text=True))
    except Exception as e:
        print('/api/nlp-stats request failed:', repr(e))
