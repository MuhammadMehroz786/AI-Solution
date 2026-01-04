#!/usr/bin/env python3
"""
Test the complete workflow: Flask → N8N → OpenAI → Google Docs → Callback
"""

import requests
import time
import uuid

# Test prospect data
test_prospect = {
    'Company_Name': 'Test Company Inc',
    'First_Name': 'John',
    'Last_Name': 'Doe',
    'Job_Title': 'CEO',
    'Email': 'john@testcompany.com',
    'Website': 'testcompany.com',
    'LinkedIn_URL': 'https://linkedin.com/in/johndoe'
}

print("🧪 Testing Full Workflow: Flask → N8N → Callback\n")
print("=" * 60)

# Generate unique job ID
job_id = str(uuid.uuid4())
print(f"\n📝 Job ID: {job_id}")

# Step 1: Send to Flask processing endpoint
print("\n📤 Step 1: Sending prospect to Flask...")

response = requests.post(
    'http://localhost:8000/api/process/test',
    json=test_prospect,
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    job_id = result.get('job_id')
    print(f"✅ Processing started")
    print(f"   Job ID: {job_id}")
else:
    print(f"❌ Failed: {response.status_code}")
    print(f"   {response.text}")
    exit(1)

# Step 2: Poll status
print("\n🔄 Step 2: Polling status...")
max_polls = 30  # 30 polls = 30 seconds
poll_count = 0

while poll_count < max_polls:
    time.sleep(1)
    poll_count += 1

    status_response = requests.get(f'http://localhost:8000/api/status/{job_id}')

    if status_response.status_code == 200:
        status_data = status_response.json()
        status_info = status_data.get('status', {})
        current_status = status_info.get('status', 'unknown')

        print(f"   [{poll_count}] Status: {current_status}")

        if status_info.get('completed'):
            print(f"\n✅ Workflow completed!")
            print(f"\n📄 Results:")
            print(f"   Pre-Brief: {status_info.get('pre_brief_url', 'N/A')}")
            print(f"   Sales Snapshot: {status_info.get('sales_snapshot_url', 'N/A')}")
            print(f"   Document 1: {status_info.get('document1_url', 'N/A')}")
            print(f"   Document 2: {status_info.get('document2_url', 'N/A')}")
            break

        if 'error' in status_info:
            print(f"\n❌ Error: {status_info.get('error')}")
            break
    else:
        print(f"   [{poll_count}] Failed to get status")

if poll_count >= max_polls:
    print(f"\n⏱️  Timeout after {max_polls} seconds")
    print("   N8N may still be processing - check manually")

print("\n" + "=" * 60)
print("🎯 Test complete!")
