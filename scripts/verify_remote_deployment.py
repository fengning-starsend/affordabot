import requests
import sys
import json
import time

BASE_URL = "https://backend-dev-3d99.up.railway.app"

def test_endpoint(name, url_path, expected_status=200):
    url = f"{BASE_URL}{url_path}"
    print(f"Testing {name} ({url})...", end=" ")
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        duration = time.time() - start
        
        if response.status_code == expected_status:
            print(f"✅ PASS ({duration:.2f}s)")
            try:
                data = response.json()
                # print(f"   Response: {json.dumps(data, indent=2)[:200]}...") # Truncated
                return True, data
            except:
                print("   Response not JSON")
                return True, response.text
        else:
            print(f"❌ FAIL (Status: {response.status_code})")
            print(f"   Response: {response.text[:200]}")
            return False, None
    except Exception as e:
        print(f"❌ FAIL (Exception: {e})")
        return False, None

def run_verification():
    print(f"🚀 Verifying Remote Deployment at {BASE_URL}\n")
    
    # 1. Global Health
    pass1, data1 = test_endpoint("Global Health", "/health")
    if pass1 and data1.get('status') == 'healthy':
        print("   -> Status verified: healthy")
    else:
        print("   -> ⚠️ Unexpected health status")

    # 2. Detailed Health (checks services)
    pass2, data2 = test_endpoint("Detailed Health", "/admin/health/detailed")
    if pass2:
        db_status = data2.get('database', {}).get('status')
        print(f"   -> DB Status: {db_status}")
    
    # 3. Jurisdictions (checks DB query)
    pass3, data3 = test_endpoint("Jurisdictions List", "/admin/jurisdictions")
    if pass3:
        count = len(data3) if isinstance(data3, list) else 0
        print(f"   -> Found {count} jurisdictions")

    # 4. Model Configs (checks SupabaseDB logic)
    pass4, data4 = test_endpoint("Model Configs", "/admin/models")
    if pass4:
        count = len(data4) if isinstance(data4, list) else 0
        print(f"   -> Found {count} model configs")

    if all([pass1, pass2, pass3, pass4]):
        print("\n✨ ALL TESTS PASSED! Deployment is operational.")
        sys.exit(0)
    else:
        print("\n💥 SOME TESTS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    run_verification()
