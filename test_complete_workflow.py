#!/usr/bin/env python3
"""Complete end-to-end test of Dream 100 batch workflow"""

import requests
import json
import csv
import time

# CSV file path
csv_file = '/Users/apple/Downloads/Dream 100 csv.  - Sheet1.csv'

print("=" * 80)
print("DREAM 100 ADVANTAGE - COMPLETE END-TO-END TEST")
print("=" * 80)

# Read CSV file and convert to proper format
prospects = []
with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        prospect = {
            'Company_Name': row['Company'].strip(),
            'First_Name': row['First Name'].strip(),
            'Last_Name': row['Last Name'].strip(),
            'Title': row.get('Title ', '').strip(),
            'Email': row.get('Email ', '').strip(),
            'Website': row['Website'].strip()
        }
        prospects.append(prospect)

print(f"\n📦 Loaded {len(prospects)} prospects from CSV:")
print("-" * 80)
for i, p in enumerate(prospects, 1):
    print(f"{i}. {p['First_Name']} {p['Last_Name']} @ {p['Company_Name']}")
    print(f"   Email: {p['Email']}, Website: {p['Website']}")
print("-" * 80)

# Prepare payload
payload = {
    'items': prospects
}

print(f"\n🚀 Sending batch to Flask endpoint...")
print(f"   Endpoint: http://localhost:8000/api/process/test")
print(f"   Total prospects: {len(prospects)}")

# Send to Flask
response = requests.post(
    'http://localhost:8000/api/process/test',
    json=payload,
    headers={'Content-Type': 'application/json'}
)

print(f"\n📥 Response ({response.status_code}):")
result = response.json()
print(json.dumps(result, indent=2))

if response.status_code == 202:
    job_id = result['job_id']
    is_batch = result.get('is_batch', False)

    print(f"\n✅ Batch processing started!")
    print(f"   Job ID: {job_id}")
    print(f"   Batch mode: {is_batch}")
    print(f"   Status URL: http://localhost:8000/api/status/{job_id}")

    print(f"\n⏳ Processing workflow (this will take several minutes)...")
    print(f"\nEach prospect goes through:")
    print(f"   1. Website scraping (Apify)")
    print(f"   2. AI analysis (Manus AI)")
    print(f"   3. Document generation (OpenAI GPT-4o)")
    print(f"   4. Google Docs creation (N8N)")
    print(f"   5. Callback with document URLs")
    print(f"\nAfter all {len(prospects)} prospects are complete:")
    print(f"   6. Generate results CSV")
    print(f"   7. Send email to mehroz.muneer@gmail.com")

    print(f"\n" + "=" * 80)
    print("MONITORING PROGRESS")
    print("=" * 80)

    # Monitor progress
    last_status = None
    completed = False

    while not completed:
        time.sleep(10)  # Check every 10 seconds

        try:
            status_response = requests.get(f'http://localhost:8000/api/status/{job_id}')
            status_data = status_response.json()

            if status_data.get('success'):
                current_status = status_data['status']

                # Only print if status changed
                if current_status != last_status:
                    print(f"\n[{time.strftime('%H:%M:%S')}] Status: {current_status.get('status', 'unknown')}")
                    print(f"   Message: {current_status.get('message', 'N/A')}")

                    if 'processed' in current_status and 'total' in current_status:
                        print(f"   Progress: {current_status['processed']}/{current_status['total']}")

                    last_status = current_status

                # Check if completed
                if current_status.get('status') == 'completed':
                    completed = True
                    print(f"\n" + "=" * 80)
                    print("✅ WORKFLOW COMPLETED!")
                    print("=" * 80)
                    print(f"\n📧 Results CSV has been sent to: mehroz.muneer@gmail.com")
                    print(f"\n📬 Check your inbox for:")
                    print(f"   • Subject: Dream 100 Batch Processing Results")
                    print(f"   • Attachment: dream100_results_[timestamp].csv")
                    print(f"   • Contains: All {len(prospects)} prospects with document links")
                    break

        except Exception as e:
            print(f"\n⚠️  Error checking status: {e}")
            time.sleep(5)

else:
    print(f"\n❌ Failed to start batch processing")
    print(f"   Error: {result.get('error', 'Unknown error')}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
