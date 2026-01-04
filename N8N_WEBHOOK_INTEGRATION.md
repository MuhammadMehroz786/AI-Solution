# N8N Webhook Integration - Final Setup

## ✅ Configuration Complete

I've updated the application to use your existing n8n webhooks instead of calling APIs directly. This is much simpler and leverages your existing n8n workflows!

## 🔗 Configured Webhooks

### 1. Document Generation Webhook
**URL:** `https://n8n.eventplanners.cloud/webhook/2af2ce4c-6c51-4935-9f0a-1a019d4bd466`

**Purpose:** Creates both documents (Pre-Brief and Sales Snapshot)

**Request Format:**
```json
{
  "prospect": {
    "Company_Name": "Acme Corp",
    "First_Name": "John",
    "Last_Name": "Doe",
    "Job_Title": "CEO",
    "Email": "john@acmecorp.com",
    "Website": "acmecorp.com",
    "LinkedIn_URL": "https://linkedin.com/in/johndoe"
  },
  "website_data": {
    // Scraped website content from Apify
  }
}
```

**Expected Response:**
Your n8n workflow should return the document URLs. The Flask app will handle various response formats:
```json
{
  "document1_url": "https://docs.google.com/document/d/...",
  "document2_url": "https://docs.google.com/document/d/...",
  "Document 1": "https://docs.google.com/document/d/...",
  "Document 2": "https://docs.google.com/document/d/..."
}
```

### 2. Google Sheet Creation Webhook
**URL:** `https://n8n.eventplanners.cloud/webhook/f8be2ba7-036c-4c0a-9a9b-0efc29654626`

**Purpose:** Creates Google Sheet and appends rows

**Request Format (Create Sheet):**
```json
{
  "sheet_name": "Dream 100 Prospects - 2026-01-04 14:30"
}
```

**Expected Response:**
```json
[{
  "json": {
    "Date": "",
    "Company Name": "",
    "First Name": "",
    "Last Name": "",
    "Email": "",
    "LinkedIn URL": "",
    "Document 1": "",
    "Document 2": "",
    "spreadsheet_id": "your-sheet-id",
    "spreadsheet_url": "https://docs.google.com/spreadsheets/d/..."
  }
}]
```

**Request Format (Append Row):**
```json
{
  "sheet_id": "spreadsheet-id-from-creation",
  "row_data": {
    "Date": "2026-01-04 14:30:00",
    "Company Name": "Acme Corp",
    "First Name": "John",
    "Last Name": "Doe",
    "Email": "john@acmecorp.com",
    "LinkedIn URL": "https://linkedin.com/in/johndoe",
    "Document 1": "https://docs.google.com/document/d/...",
    "Document 2": "https://docs.google.com/document/d/..."
  }
}
```

## 📊 How the Workflow Works Now

### User Submits Prospect Data
1. Flask receives prospect data from UI
2. **Extracts website from email** (e.g., `john@acmecorp.com` → `acmecorp.com`)
3. **Scrapes website** using Apify API (direct call)
4. **Sends to n8n Document Webhook** with prospect data + scraped content
5. N8N generates both documents and returns URLs
6. **Sends to n8n Sheet Webhook** to create/update Google Sheet
7. Returns results to UI with links to documents and sheet

### Data Flow Diagram
```
User Form
    ↓
Flask Backend
    ↓
Extract Website from Email
    ↓
Apify Web Scraping (Direct API)
    ↓
N8N Document Webhook → Creates 2 Google Docs
    ↓
N8N Sheet Webhook → Creates/Updates Google Sheet
    ↓
UI Shows Results (Document Links + Sheet Link)
```

## 🎯 What Your N8N Workflows Need to Do

### Document Generation Workflow
Your n8n workflow at `2af2ce4c-6c51-4935-9f0a-1a019d4bd466` should:

1. Receive the payload with prospect + website_data
2. Use the website_data to analyze the company
3. Generate "Revenue Intelligence Pre-Brief" (Document 1)
4. Generate "Internal Sales Snapshot" (Document 2)
5. Return both document URLs

**Important:** The Flask app will look for these fields in your response:
- `document1_url` or `Document 1`
- `document2_url` or `Document 2`

### Sheet Management Workflow
Your n8n workflow at `f8be2ba7-036c-4c0a-9a9b-0efc29654626` should:

1. **On Create Request** (when `sheet_name` is provided):
   - Create new Google Sheet with the name
   - Add headers: Date, Company Name, First Name, Last Name, Email, LinkedIn URL, Document 1, Document 2
   - Return sheet ID and URL in the format shown above

2. **On Append Request** (when `sheet_id` and `row_data` are provided):
   - Append the row_data to the specified sheet
   - Return success status

## 📝 Environment Variables Configured

The `.env` file now contains:
```env
# Apify for web scraping
APIFY_API_TOKEN=apify_api_sk-uU1Di...

# N8N Webhooks
N8N_WEBHOOK_DOC_GENERATION=https://n8n.eventplanners.cloud/webhook/2af2ce4c-6c51-4935-9f0a-1a019d4bd466
N8N_WEBHOOK_SHEET_CREATION=https://n8n.eventplanners.cloud/webhook/f8be2ba7-036c-4c0a-9a9b-0efc29654626
```

## 🚀 Ready to Test

The application is running at **http://localhost:8000**

### Test Single Prospect:
1. Go to http://localhost:8000
2. Login: `emrgmedia` / `Mario`
3. Fill in prospect form with email (website will be extracted from email)
4. Click "Process Intelligence"
5. Watch real-time status updates
6. Get links to documents and sheet when complete

### Test Bulk CSV:
1. Download CSV template from dashboard
2. Fill in multiple prospects
3. Upload and process
4. All prospects will be in one Google Sheet

## 🔧 Simplified Architecture

**Removed:**
- ❌ Direct OpenAI API calls
- ❌ Direct Manus AI integration
- ❌ Direct Google API (Sheets, Docs, Drive, Gmail) dependencies
- ❌ Google Cloud credentials
- ❌ Service account setup

**Kept:**
- ✅ Apify API (web scraping)
- ✅ Flask backend orchestration
- ✅ Real-time status polling
- ✅ Beautiful UI with progress updates
- ✅ Email-to-website extraction

**Now Using:**
- ✅ N8N webhook for document generation
- ✅ N8N webhook for Google Sheets
- ✅ Much simpler setup - no Google credentials needed in Flask!

## 📦 Updated Files

1. **workflow.py** - Completely rewritten to use n8n webhooks
2. **.env** - Added n8n webhook URLs
3. **requirements.txt** - Removed Google API dependencies
4. **README.md** - Updated architecture documentation

## ✨ Benefits of This Approach

1. **Simpler Setup** - No Google Cloud configuration in Flask
2. **Leverage Existing N8N** - Uses your proven workflows
3. **Easier Debugging** - See everything in n8n UI
4. **More Flexible** - Change workflow in n8n without touching Flask
5. **Better Separation** - Flask handles UI/orchestration, n8n handles business logic

## 🎯 Next Steps

1. **Test the document webhook** - Make sure it returns document URLs correctly
2. **Test the sheet webhook** - Verify it creates sheets and appends rows
3. **Verify response formats** - Ensure n8n returns data in expected format
4. **Process a test prospect** - End-to-end test with real data

The application is ready to use with your n8n workflows!
