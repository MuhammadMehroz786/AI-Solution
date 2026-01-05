import requests
import json
import time

# Test data for batch CSV
test_data = {
    "Company_Name": "Test Company Inc",
    "First_Name": "John",
    "Last_Name": "Doe",
    "Title": "CEO",
    "Email": "john.doe@testcompany.com",
    "Website": "https://testcompany.com",
    "batch_id": f"batch_{int(time.time())}_test123",
    "row_number": 1
}

print("=" * 60)
print("Testing Batch CSV Workflow")
print("=" * 60)
print(f"\n📤 Sending test data to Flask:")
print(json.dumps(test_data, indent=2))

# Send to Flask endpoint
flask_url = "http://localhost:8000/api/send-to-n8n"

try:
    print(f"\n🔄 Sending request to: {flask_url}")
    print("⏳ Waiting for N8N to process (timeout: 10 minutes)...\n")

    response = requests.post(
        flask_url,
        json=test_data,
        headers={'Content-Type': 'application/json'},
        timeout=610  # Slightly more than 10 minutes
    )

    print(f"✅ Response Status: {response.status_code}")
    print(f"📥 Response Body:")
    print(json.dumps(response.json(), indent=2))

    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("\n🎉 SUCCESS! Received document URLs:")
            print(f"   - Document 1: {result.get('data', {}).get('document1_url', 'N/A')}")
            print(f"   - Document 2: {result.get('data', {}).get('document2_url', 'N/A')}")
        else:
            print(f"\n❌ Error: {result.get('error')}")
    else:
        print(f"\n❌ Request failed with status {response.status_code}")

except requests.exceptions.Timeout:
    print("\n⏱️  Request timed out after 10 minutes")
except requests.exceptions.ConnectionError:
    print("\n❌ Connection error - is Flask running on port 8000?")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "=" * 60)
