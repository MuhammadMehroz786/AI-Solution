#!/usr/bin/env python3
"""Test batch CSV processing"""

import requests
import json
import csv

# Read CSV file
csv_file = 'test_batch.csv'
prospects = []

with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        prospects.append({
            'Company_Name': row['Company'],
            'First_Name': row['First Name'],
            'Last_Name': row['Last Name'],
            'Title': row['Title'],
            'Email': row['Email'],
            'Website': row['Website']
        })

print(f"📦 Loaded {len(prospects)} prospects from CSV:")
for p in prospects:
    print(f"   - {p['First_Name']} {p['Last_Name']} @ {p['Company_Name']}")

# Send batch to test endpoint
payload = {
    'items': prospects
}

print(f"\n🚀 Sending batch to test endpoint...")
response = requests.post(
    'http://localhost:8000/api/process/test',
    json=payload,
    headers={'Content-Type': 'application/json'}
)

print(f"\n✅ Response ({response.status_code}):")
print(json.dumps(response.json(), indent=2))

if response.status_code == 202:
    job_id = response.json()['job_id']
    print(f"\n📊 Job ID: {job_id}")
    print(f"💡 Check status at: http://localhost:8000/api/status/{job_id}")
