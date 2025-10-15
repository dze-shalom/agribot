"""
Test analytics API locally without running the server
"""
import os
os.environ['DATABASE_URL'] = 'sqlite:///instance/agribot.db'

from app.main import create_app
from database.repositories.analytics_repository import AnalyticsRepository

app = create_app()

with app.app_context():
    print("Testing Analytics Repository...")
    print("=" * 60)

    try:
        # Test satisfaction metrics
        print("\n1. Testing get_satisfaction_metrics()...")
        satisfaction = AnalyticsRepository.get_satisfaction_metrics(days=30)
        print(f"   Total feedback: {satisfaction['total_feedback']}")
        print(f"   Satisfaction rate: {satisfaction['satisfaction_rate']}%")
        print(f"   Avg rating: {satisfaction['avg_overall_rating']}/5")
        print(f"   ✓ SUCCESS")

    except Exception as e:
        print(f"   ✗ FAILED: {str(e)}")

    try:
        # Test comprehensive analytics
        print("\n2. Testing get_comprehensive_analytics()...")
        analytics = AnalyticsRepository.get_comprehensive_analytics(days=30)

        print(f"   Total users: {analytics['overview']['total_users']}")
        print(f"   Total conversations: {analytics['overview']['total_conversations']}")
        print(f"   AI Accuracy: {analytics['overview']['ai_accuracy']}%")
        print(f"   Satisfaction rate: {analytics['overview']['satisfaction_rate']}%")
        print(f"   User satisfaction score: {analytics['overview']['user_satisfaction_score']}/5")
        print(f"   Total feedback count: {analytics['overview']['total_feedback_count']}")
        print(f"   ✓ SUCCESS")

    except Exception as e:
        print(f"   ✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Test Complete!")
