# Complete Workflow - Dream 100 Advantage

## 🎯 Workflow Overview

```
User submits prospect
    ↓
Flask: Extract website from email
    ↓
Flask: Scrape website (Apify)
    ↓
Flask: Generate content (OpenAI)
    ↓
Flask → N8N: Send content + job_id + callback_url
    ↓
N8N: Create 2 Google Docs
    ↓
N8N → Flask: Callback with document URLs
    ↓
Flask → N8N: Send email with document links
    ↓
N8N: Send email notification
    ↓
User sees document links in UI
```

## 📋 Configuration

### Environment Variables (.env)
```env
# Email Configuration
RECIPIENT_EMAIL=your-email@example.com

# OpenAI API
OPENAI_API_KEY=sk-proj-...

# Apify API
APIFY_API_TOKEN=apify_api_sk-...

# N8N Webhooks
N8N_WEBHOOK_DOC_GENERATION=https://n8n.eventplanners.cloud/webhook/a86cbd9b-cb98-4fdb-b451-43102f2e39b8
N8N_WEBHOOK_EMAIL=https://n8n.eventplanners.cloud/webhook-test/d3ce78b4-3da7-4efd-92aa-b0c154f5858b
```

### Ngrok Callback URL
```
https://lovesome-nonclinically-carri.ngrok-free.dev/api/webhook/callback
```

## 🔗 N8N Webhook 1: Document Generation

**URL:** `https://n8n.eventplanners.cloud/webhook/a86cbd9b-cb98-4fdb-b451-43102f2e39b8`

**Receives from Flask:**
```json
{
  "job_id": "uuid-here",
  "callback_url": "https://lovesome-nonclinically-carri.ngrok-free.dev/api/webhook/callback",
  "pre_brief": "OpenAI generated Pre-Brief content...",
  "sales_snapshot": "OpenAI generated Sales Snapshot content...",
  "prospect_info": {
    "company": "Test Company Inc",
    "name": "John Doe"
  }
}
```

**N8N Workflow Steps:**
1. **Webhook Trigger** - Receive data (Respond: Immediately)
2. **Google Docs Node 1** - Create Pre-Brief document with `pre_brief` content
3. **Google Docs Node 2** - Create Sales Snapshot document with `sales_snapshot` content
4. **HTTP Request Node** - Send results back to Flask

**HTTP Request Configuration:**
- Method: `POST`
- URL: `{{ $node['Webhook'].json.body.callback_url }}`
- Body (Using Fields Below):
  - `job_id`: `{{ $node['Webhook'].json.body.job_id }}`
  - `success`: `true`
  - `document1_url`: `{{ $node['Google Docs'].json.documentUrl }}`
  - `document2_url`: `{{ $node['Google Docs1'].json.documentUrl }}`

## 📧 N8N Webhook 2: Email Notification

**URL:** `https://n8n.eventplanners.cloud/webhook-test/d3ce78b4-3da7-4efd-92aa-b0c154f5858b`

**Receives from Flask:**
```json
{
  "company_name": "Test Company Inc",
  "prospect_name": "John Doe",
  "document1_url": "https://docs.google.com/document/d/...",
  "document2_url": "https://docs.google.com/document/d/...",
  "recipient_email": "your-email@example.com"
}
```

**N8N Workflow Steps:**
1. **Webhook Trigger** - Receive email data
2. **Gmail/SendGrid Node** - Send email with document links

**Email Template:**
```
Subject: New Prospect Intelligence: {{ $node['Webhook'].json.body.company_name }}

Hi,

New prospect intelligence documents have been generated for:

Company: {{ $node['Webhook'].json.body.company_name }}
Contact: {{ $node['Webhook'].json.body.prospect_name }}

Documents:
- Revenue Intelligence Pre-Brief: {{ $node['Webhook'].json.body.document1_url }}
- Internal Sales Snapshot: {{ $node['Webhook'].json.body.document2_url }}

Best regards,
Dream 100 Advantage System
```

## 🚀 Testing

### 1. Start Services

```bash
# Terminal 1: Start ngrok
ngrok http 8000

# Terminal 2: Start Flask
cd "/Users/apple/Desktop/Bot/Mario - N8N"
python app.py
```

### 2. Activate N8N Workflows

- Workflow `a86cbd9b-cb98-4fdb-b451-43102f2e39b8` - Document Generation (ACTIVE)
- Workflow `d3ce78b4-3da7-4efd-92aa-b0c154f5858b` - Email Notification (ACTIVATE)

### 3. Test End-to-End

1. Open http://localhost:8000
2. Login: `emrgmedia` / `Mario`
3. Enter prospect data:
   - Company: Test Company Inc
   - First Name: John
   - Last Name: Doe
   - Email: john@testcompany.com
   - LinkedIn: https://linkedin.com/in/johndoe
4. Click "Process Intelligence"
5. Watch the status updates
6. Verify:
   - ✅ Website scraped
   - ✅ Content generated (OpenAI)
   - ✅ Documents created (Google Docs)
   - ✅ Email sent
   - ✅ Links displayed in UI

## 📊 Status Flow

```
Flask Job Status:
  initializing
    ↓
  scraping website
    ↓
  generating content
    ↓
  creating documents (waiting for n8n)
    ↓
  sending email
    ↓
  completed
```

## ✅ Success Indicators

- Flask logs show: "✅ Received callback for job {id}"
- Flask logs show: "✅ Email sent successfully"
- N8N execution log shows successful document creation
- N8N execution log shows successful email send
- UI displays both document URLs
- Email received with document links

## 🔧 Troubleshooting

**Callback returns 400 "Invalid job_id":**
- The job doesn't exist in Flask memory
- Make sure Flask created the job first before n8n calls back

**N8N webhook returns 404:**
- Workflow is not activated
- Toggle the switch in top-right of n8n editor

**Email not sent:**
- Check `N8N_WEBHOOK_EMAIL` is correct
- Activate the email workflow in n8n
- Check Flask logs for email errors

**Documents not created:**
- Check n8n execution log for errors
- Verify Google Docs OAuth connection in n8n
- Check HTTP Request node is sending callback correctly
