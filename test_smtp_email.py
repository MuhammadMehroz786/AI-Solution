#!/usr/bin/env python3
"""Test SMTP email sending with CSV attachment"""

import os
from dotenv import load_dotenv
from workflow import WorkflowProcessor

# Load environment variables
load_dotenv()

# Create sample CSV content
sample_csv = """Company,First Name,Last Name,Title,Email,Website,Document 1,Document 2
EMRG Media,John,Doe,CEO,john@emrgmedia.com,https://emrgmedia.com,https://docs.google.com/document/d/1sa7BCnaU9mzCtDiQGbrqxuSPORuO5J-jbVp_X3hKNfo/,https://docs.google.com/document/d/1UjPRh_L-kGI6EO9I7kWBYs67qOI4Ve2aNpmIE-S1h2Q/
Tesla,Elon,Musk,CEO,elon@tesla.com,https://tesla.com,https://docs.google.com/document/d/test123/,https://docs.google.com/document/d/test456/
"""

print("=" * 60)
print("TESTING SMTP EMAIL WITH CSV ATTACHMENT")
print("=" * 60)

# Get email configuration
smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('SMTP_PASSWORD')
recipient = os.getenv('BATCH_RESULTS_EMAIL', 'mehroz.muneer@gmail.com')

print(f"\n📧 SMTP Configuration:")
print(f"   SMTP Host: {os.getenv('SMTP_HOST')}")
print(f"   SMTP Port: {os.getenv('SMTP_PORT')}")
print(f"   SMTP User: {smtp_user}")
print(f"   SMTP Password: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
print(f"   Recipient: {recipient}")

if not smtp_user or not smtp_password:
    print("\n❌ ERROR: SMTP credentials not configured in .env")
    print("\nPlease set:")
    print("   SMTP_USER=your-email@gmail.com")
    print("   SMTP_PASSWORD=your-app-password")
    exit(1)

print(f"\n📄 Sample CSV Content:")
print("-" * 60)
print(sample_csv[:200] + "...")
print("-" * 60)

# Initialize workflow processor
workflow = WorkflowProcessor()

# Send test email
print(f"\n🚀 Sending test email to {recipient}...")
print("   This may take a few seconds...")

result = workflow.send_results_csv_email(
    csv_content=sample_csv,
    recipient_email=recipient,
    batch_id='test-batch-12345'
)

print("\n" + "=" * 60)
if result['success']:
    print("✅ SUCCESS! Email sent successfully")
    print(f"   Filename: {result.get('filename')}")
    print(f"\n📬 Check your inbox at: {recipient}")
    print("\nThe email should contain:")
    print("   • HTML formatted body")
    print("   • CSV file attachment")
    print("   • Batch ID: test-batch-12345")
else:
    print("❌ FAILED! Email could not be sent")
    print(f"   Error: {result.get('error')}")
print("=" * 60)
