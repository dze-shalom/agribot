"""
Test Analytics Endpoints Performance
Run this script to test if analytics endpoints are timing out
"""
import requests
import time
import sys

# Your Render URL
RENDER_URL = input("Enter your Render URL (e.g., https://your-app.onrender.com): ").strip().rstrip('/')

def test_endpoint(endpoint_name, url, timeout=180):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    try:
        start_time = time.time()
        print(f"⏳ Sending request (timeout: {timeout}s)...")

        response = requests.get(url, timeout=timeout)
        elapsed = time.time() - start_time

        print(f"✅ Response received in {elapsed:.2f} seconds")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Valid JSON response")
                print(f"Response keys: {list(data.keys())[:10]}")
                return True, elapsed
            except:
                print(f"⚠️  Response is not JSON")
                print(f"First 200 chars: {response.text[:200]}")
                return False, elapsed
        elif response.status_code == 401:
            print(f"❌ Authentication required - You need to login first")
            return False, elapsed
        else:
            print(f"❌ Error status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False, elapsed

    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"❌ TIMEOUT after {elapsed:.2f} seconds")
        return False, elapsed
    except requests.exceptions.ConnectionError as e:
        elapsed = time.time() - start_time
        print(f"❌ Connection Error: {str(e)}")
        return False, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error: {str(e)}")
        return False, elapsed

def main():
    print("🔍 Analytics Endpoint Performance Tester")
    print("="*60)

    # Test endpoints
    endpoints = [
        ("Health Check", f"{RENDER_URL}/health"),
        ("Analytics Overview", f"{RENDER_URL}/api/auth/admin/analytics/overview"),
        ("Analytics Detailed", f"{RENDER_URL}/api/auth/admin/analytics/detailed"),
        ("Knowledge Transfer", f"{RENDER_URL}/admin/knowledge-transfer"),
    ]

    results = []

    for name, url in endpoints:
        success, elapsed = test_endpoint(name, url, timeout=180)
        results.append((name, success, elapsed))
        time.sleep(1)  # Small delay between requests

    # Summary
    print(f"\n\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")

    for name, success, elapsed in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {name:30s} | {elapsed:6.2f}s")

    print(f"\n{'='*60}")
    print("💡 DIAGNOSIS:")
    print(f"{'='*60}")

    # Check if any endpoint succeeded
    any_success = any(s for _, s, _ in results)
    all_timeout = all(not s and e > 30 for _, s, e in results[1:])  # Skip health check
    all_auth_error = all(not s for _, s, _ in results[1:])

    if not any_success and all_timeout:
        print("❌ ALL ENDPOINTS TIMING OUT")
        print("\nPossible causes:")
        print("1. Gunicorn config not being used")
        print("2. Database queries still too slow")
        print("3. Server not responding")
        print("\nRecommendations:")
        print("- Check Render logs for errors")
        print("- Verify gunicorn_config.py is in repo root")
        print("- Check render.yaml uses: 'gunicorn --config gunicorn_config.py run:app'")
    elif results[0][1] and not any(results[1:]):
        print("⚠️  Server is running but analytics endpoints failing")
        print("\nPossible causes:")
        print("1. Authentication required (401 errors)")
        print("2. Queries timing out on server side")
        print("3. Cache not working")
        print("\nRecommendations:")
        print("- Login to admin account in browser first")
        print("- Check if Redis cache is available")
        print("- Increase timeout in gunicorn_config.py to 180s")
    elif any_success:
        slow_endpoints = [(n, e) for n, s, e in results if s and e > 30]
        if slow_endpoints:
            print("⚠️  Some endpoints are SLOW (>30s)")
            for name, elapsed in slow_endpoints:
                print(f"   - {name}: {elapsed:.2f}s")
            print("\nThis will work but users will wait. Consider:")
            print("- Check if cache is working (2nd request should be fast)")
            print("- Add more aggressive query limits")
        else:
            print("✅ All endpoints responding quickly!")
            print("Analytics pages should work fine.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(1)
