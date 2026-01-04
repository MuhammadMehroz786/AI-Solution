#!/usr/bin/env python3
"""
Test script to verify OpenAI → N8N workflow
"""

from workflow import WorkflowProcessor

# Test prospect data
test_prospect = {
    'Company_Name': 'Anthropic',
    'First_Name': 'Claude',
    'Last_Name': 'AI',
    'Job_Title': 'AI Assistant',
    'Email': 'claude@anthropic.com',
    'Website': 'anthropic.com',
    'LinkedIn_URL': 'https://linkedin.com/company/anthropic'
}

print("🧪 Testing OpenAI → N8N Workflow\n")
print("=" * 60)

# Initialize processor
processor = WorkflowProcessor()

# Step 1: Test website scraping (limited to save time)
print("\n📥 Step 1: Scraping website...")
website_result = processor.scrape_website_apify('anthropic.com')
if website_result.get('success'):
    print("✅ Website scraped successfully")
    website_data = website_result.get('data', {})
else:
    print(f"❌ Scraping failed: {website_result.get('error')}")
    website_data = {}

# Step 2: Generate Pre-Brief with OpenAI
print("\n🤖 Step 2: Generating Pre-Brief with OpenAI...")
pre_brief = processor.generate_pre_brief_openai(test_prospect, website_data)
print(f"✅ Generated ({len(pre_brief)} characters)")
print(f"Preview: {pre_brief[:200]}...")

# Step 3: Generate Sales Snapshot with OpenAI
print("\n🤖 Step 3: Generating Sales Snapshot with OpenAI...")
sales_snapshot = processor.generate_sales_snapshot_openai(test_prospect, website_data)
print(f"✅ Generated ({len(sales_snapshot)} characters)")
print(f"Preview: {sales_snapshot[:200]}...")

# Step 4: Send to N8N (will use test webhook)
print("\n📤 Step 4: Sending to N8N webhook...")
print("⚠️  Make sure you've activated the test webhook in N8N first!")
print("   (Click 'Execute workflow' in N8N canvas)")

input("\nPress Enter when webhook is ready, or Ctrl+C to skip...")

doc_result = processor.send_documents_to_n8n(
    pre_brief,
    sales_snapshot,
    test_prospect,
    is_test_mode=True
)

if doc_result.get('success'):
    print("✅ N8N webhook successful!")
    print(f"Response: {doc_result.get('documents')}")
else:
    print(f"❌ N8N webhook failed: {doc_result.get('error')}")

print("\n" + "=" * 60)
print("🎯 Test complete!")
