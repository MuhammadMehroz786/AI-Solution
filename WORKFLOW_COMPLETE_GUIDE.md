# Dream 100 Advantage - Complete Workflow Guide

## Implementation Complete ✅

The complete single-entry workflow has been implemented with Manus AI and OpenAI integration.

## Workflow Overview

```
User Input (Form)
    ↓
Extract Website from Email
    ↓
Scrape Website (Apify)
    ↓
Analyze with Manus AI
    ↓
Generate Pre-Brief (OpenAI GPT-4o)
    ↓
Generate Sales Snapshot (OpenAI GPT-4o)
    ↓
Send to N8N (Create 2 Google Docs)
    ↓
N8N Callback (Returns Document URLs)
    ↓
Send Email (N8N with Document Links)
    ↓
Complete (User sees document links)
```

## Files Created

### 1. Prompt Files
- **prompt_manus_analysis.txt** - Manus AI analysis prompt
- **prompt_pre_brief.txt** - Revenue Intelligence Pre-Brief template (10 sections)
- **prompt_sales_snapshot.txt** - Internal Executive Sales Snapshot template (11 sections)

### 2. Updated Files
- **workflow.py** - Complete implementation with:
  - `analyze_with_manus()` - Manus AI integration
  - `generate_pre_brief_openai()` - Pre-Brief HTML generation
  - `generate_sales_snapshot_openai()` - Sales Snapshot HTML generation
  - `process_prospect()` - Complete workflow orchestration
  - Prompt file loading system

- **app.py** - Updated background processing to call new workflow

## API Configuration

All APIs are configured in `.env`:

```env
# OpenAI API
OPENAI_API_KEY=sk-proj-Zn_kix2usW2mCBbM-...
Model: gpt-4o

# Manus AI API
MANUS_API_KEY=sk-uU1Di1LTkWVykqPcWxUIpcq1bef9Boc_...
MANUS_MODEL=manus-1.6-max
Endpoint: https://api.manus.im/v1/chat/completions

# Apify API
APIFY_API_TOKEN=apify_api_sk-uU1Di1LTkWVykqPcWxUIpcq1bef9Boc_...
Endpoint: https://api.apify.com/v2/acts/apify~website-content-crawler/run-sync-get-dataset-items

# N8N Webhooks
N8N_WEBHOOK_DOC_GENERATION=https://n8n.eventplanners.cloud/webhook/a86cbd9b-cb98-4fdb-b451-43102f2e39b8
N8N_WEBHOOK_DOC_GENERATION_TEST=https://n8n.eventplanners.cloud/webhook-test/a86cbd9b-cb98-4fdb-b451-43102f2e39b8
N8N_WEBHOOK_EMAIL=https://n8n.eventplanners.cloud/webhook-test/d3ce78b4-3da7-4efd-92aa-b0c154f5858b
```

## Workflow Steps in Detail

### Step 1: User Input
Form fields:
- Company Name
- First Name
- Last Name
- Email
- LinkedIn URL (optional)

### Step 2: Extract Website
- Extract domain from email (e.g., `john@company.com` → `company.com`)
- Skip common email providers (gmail, yahoo, etc.)
- Fallback to LinkedIn URL if no website

### Step 3: Scrape Website with Apify
- Uses Apify Website Content Crawler
- Scrapes up to 5 pages
- Synchronous endpoint (2 minute timeout)
- Returns structured website data

### Step 4: Analyze with Manus AI
**Endpoint:** `https://api.manus.im/v1/chat/completions`

**Prompt includes:**
- Company identity analysis
- Decision-maker intelligence
- Competitive reality
- Trust & social proof
- Market pressure points
- Strategic conversation anchors
- Hidden insights

**Returns:** Strategic analysis in bullet-driven format

### Step 5: Generate Pre-Brief with OpenAI
**Model:** `gpt-4o`
**Max Tokens:** 16,000

**Output Structure (Raw HTML):**
1. Company Snapshot
2. Decision-Maker Intelligence
3. Competitive Landscape
4. Trust & Social Proof
5. Market Pressure Points
6. Strategic Conversation Anchors
7. Hidden Insight
8. Recommended Opening Approach
9. Questions That Create Positioning
10. Executive Summary

### Step 6: Generate Sales Snapshot with OpenAI
**Model:** `gpt-4o`
**Max Tokens:** 16,000

**Output Structure (Raw HTML):**
1. Opportunity Assessment
2. Pain Signals
3. Buying Signals
4. Competitive Intelligence
5. Stakeholder Map
6. Objection Pre-emption
7. Value Proposition Positioning
8. Tactical Call Plan
9. Risk Assessment
10. Next Best Action
11. Executive Summary

### Step 7: Send to N8N for Document Creation
**Webhook:** `N8N_WEBHOOK_DOC_GENERATION`

**Payload:**
```json
{
  "job_id": "uuid-string",
  "callback_url": "https://your-ngrok-url.ngrok.io/api/webhook/callback",
  "pre_brief": "<h1>Revenue Intelligence Pre-Brief</h1>...",
  "sales_snapshot": "<h1>Internal Executive Sales Snapshot</h1>...",
  "prospect_info": {
    "company": "Company Name",
    "name": "First Last"
  }
}
```

**N8N Should:**
1. Create Google Doc 1 from `pre_brief` HTML
2. Create Google Doc 2 from `sales_snapshot` HTML
3. Return callback with both document URLs

### Step 8: N8N Callback
**Endpoint:** `/api/webhook/callback`

**Expected Payload:**
```json
{
  "job_id": "uuid-string",
  "success": true,
  "document1_url": "https://docs.google.com/document/d/...",
  "document2_url": "https://docs.google.com/document/d/..."
}
```

**Flask Action:**
- Updates processing_status with document URLs
- Triggers email webhook

### Step 9: Send Email via N8N
**Webhook:** `N8N_WEBHOOK_EMAIL`

**Payload:**
```json
{
  "document1_url": "https://docs.google.com/document/d/...",
  "document2_url": "https://docs.google.com/document/d/..."
}
```

**N8N Should:**
- Send email with both document links
- Email configured in n8n (not Flask)

### Step 10: Complete
- User sees document links in UI
- Status updates to "completed"

## Testing the Workflow

### 1. Start Flask App
```bash
cd "/Users/apple/Desktop/Bot/Mario - N8N"
python app.py
```
Flask runs on: http://localhost:8000

### 2. Start Ngrok (for N8N callback)
```bash
ngrok http 8000
```
Your callback URL will be: `https://your-subdomain.ngrok.io/api/webhook/callback`

### 3. Test with Sample Data

**Test Mode (recommended first):**
```bash
curl -X POST http://localhost:8000/api/process/test \
  -H "Content-Type: application/json" \
  -d '{
    "Company_Name": "EMRG Media",
    "First_Name": "John",
    "Last_Name": "Doe",
    "Email": "john@emrgmedia.com",
    "LinkedIn_URL": "https://linkedin.com/in/johndoe"
  }'
```

**Production Mode:**
```bash
curl -X POST http://localhost:8000/api/process/prod \
  -H "Content-Type: application/json" \
  -d '{
    "Company_Name": "EMRG Media",
    "First_Name": "John",
    "Last_Name": "Doe",
    "Email": "john@emrgmedia.com",
    "LinkedIn_URL": "https://linkedin.com/in/johndoe"
  }'
```

**Response:**
```json
{
  "success": true,
  "job_id": "uuid-string",
  "message": "Processing 1 prospect(s) in test mode...",
  "status_url": "/api/status/uuid-string"
}
```

### 4. Check Status
```bash
curl http://localhost:8000/api/status/uuid-string
```

### 5. Monitor Flask Logs
You'll see detailed progress:
```
============================================================
🎯 Processing: John Doe @ EMRG Media
============================================================
📧 Extracted website from email: emrgmedia.com
🔍 Scraping website: https://emrgmedia.com
✅ Website scraped successfully: 5 pages
🤖 Analyzing with Manus AI: EMRG Media
✅ Manus AI analysis completed
📄 Generating Pre-Brief with OpenAI...
✅ Pre-Brief generated successfully
📊 Generating Sales Snapshot with OpenAI...
✅ Sales Snapshot generated successfully
📤 Sending documents to N8N...
✅ Documents sent to N8N, job_id: uuid-string
✅ Workflow initiated for John Doe
⏳ Waiting for N8N callback with document URLs...
```

## N8N Configuration Required

### Document Generation Webhook
**URL:** `https://n8n.eventplanners.cloud/webhook/a86cbd9b-cb98-4fdb-b451-43102f2e39b8`

**Required Nodes:**
1. **Webhook** - Receives payload from Flask
2. **Function** - Extract job_id, callback_url, pre_brief, sales_snapshot
3. **Google Docs (Create from HTML)** - Create Doc 1 from pre_brief
4. **Google Docs (Create from HTML)** - Create Doc 2 from sales_snapshot
5. **HTTP Request** - Callback to Flask with:
   ```json
   {
     "job_id": "{{ $json.job_id }}",
     "success": true,
     "document1_url": "{{ $node['Google Docs 1'].json.documentUrl }}",
     "document2_url": "{{ $node['Google Docs 2'].json.documentUrl }}"
   }
   ```

### Email Webhook
**URL:** `https://n8n.eventplanners.cloud/webhook-test/d3ce78b4-3da7-4efd-92aa-b0c154f5858b`

**Required Nodes:**
1. **Webhook** - Receives document URLs
2. **Gmail/Email** - Sends email with document links

## Troubleshooting

### Error: "Manus AI API not configured"
Check `.env` has `MANUS_API_KEY`

### Error: "Apify request timed out"
- Increase timeout in workflow.py
- Check website URL is valid

### Error: "Could not load prompt_*.txt"
- Ensure all 3 prompt files are in the same directory as workflow.py
- Check file permissions

### N8N Callback 400 "Invalid job_id"
- Ensure n8n sends correct job_id from Flask payload
- Check n8n expression syntax: `{{ $json.job_id }}` (not `=job_id`)

### Documents not created
- Check n8n workflow is activated
- Verify Google Docs integration is connected
- Check HTML format is valid (no markdown, no code blocks)

### Email not sent
- Verify email webhook URL in `.env`
- Check n8n email workflow is activated
- Ensure Gmail/SMTP is configured in n8n

## Next Steps

1. **Configure N8N workflows** as described above
2. **Test with sample data** using test mode
3. **Verify all steps complete** by monitoring Flask logs
4. **Check Google Docs** are created correctly
5. **Verify email** is sent with document links
6. **Switch to production mode** once testing is complete

## Support

For issues:
1. Check Flask logs for detailed error messages
2. Check n8n execution logs
3. Verify all API keys are correct
4. Ensure ngrok is running for callbacks

## Files Reference

- `app.py` - Flask web server
- `workflow.py` - Complete workflow orchestration
- `prompt_manus_analysis.txt` - Manus AI prompt
- `prompt_pre_brief.txt` - Pre-Brief template
- `prompt_sales_snapshot.txt` - Sales Snapshot template
- `.env` - API keys and configuration
- `WORKFLOW_COMPLETE_GUIDE.md` - This file

---

**Status:** ✅ Complete and ready for testing
**Last Updated:** 2026-01-04
