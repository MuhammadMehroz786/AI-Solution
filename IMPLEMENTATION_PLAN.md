# Implementation Plan - Single Entry Workflow with Manus AI & OpenAI

## Current Status
- ✅ Flask app running with login
- ✅ N8N document webhook working (a86cbd9b-cb98-4fdb-b451-43102f2e39b8)
- ✅ N8N email webhook working (d3ce78b4-3da7-4efd-92aa-b0c154f5858b)
- ✅ Ngrok callback URL active
- ✅ Apify integration for website scraping
- ❌ Manus AI integration (needs API key)
- ❌ OpenAI Pre-Brief HTML generation (needs full prompt implementation)

## Required Workflow

### Step-by-Step Process:
1. **User Input** → Form: Company, First Name, Last Name, Email, LinkedIn
2. **Extract Website** → From email domain (e.g., `john@company.com` → `company.com`)
3. **Scrape Website** → Apify API (get all content)
4. **Analyze with Manus AI** → Send website URL + content with analysis prompt
5. **Generate HTML Pre-Brief** → OpenAI GPT-4 with Manus output + full template prompt
6. **Create Google Doc** → N8N webhook receives HTML content
7. **N8N Callback** → Returns Google Doc link to Flask
8. **Send Email** → N8N email webhook receives document link only
9. **Complete** → User sees document link in UI

## Key Changes Needed

### 1. Add Manus AI Integration
**File:** `workflow.py`

```python
def analyze_with_manus(self, website_url: str, company_name: str, website_data: Dict) -> str:
    """Analyze company with Manus AI"""
    if not self.manus_api_key:
        return "Error: Manus API not configured"

    # Manus AI API call with your analysis prompt
    # Returns strategic analysis
```

### 2. Update OpenAI Integration
**File:** `workflow.py`

Change from:
- Two separate documents (Pre-Brief + Sales Snapshot)

To:
- ONE HTML document (Revenue Intelligence Pre-Brief)
- Use GPT-4 or o1 model
- Full HTML template with all 10 sections
- Must output raw HTML (no markdown)

### 3. Update N8N Webhook Payload
**Current:**
```json
{
  "pre_brief": "content...",
  "sales_snapshot": "content...",
  "prospect_info": {...}
}
```

**New:**
```json
{
  "job_id": "uuid",
  "callback_url": "https://...",
  "html_content": "<h1>Revenue Intelligence Pre-Brief</h1>...",
  "document_title": "Revenue Intelligence Pre-Brief - [Company Name]"
}
```

### 4. Update N8N Document Workflow
**Required changes in n8n:**
- Create ONE Google Doc (not two)
- Use the HTML content directly
- Return single document URL
- Callback format:
```json
{
  "job_id": "uuid",
  "success": true,
  "document_url": "https://docs.google.com/document/d/..."
}
```

### 5. Update Email Webhook
**Current payload is correct:**
```json
{
  "document1_url": "...",
  "document2_url": "..."
}
```

**New (single document):**
```json
{
  "document_url": "https://docs.google.com/document/d/..."
}
```

## API Requirements

### Manus AI API
- **Endpoint:** (Need to confirm from you)
- **Authentication:** API Key in header
- **Request format:** (Need API docs)
- **Response format:** (Need API docs)

**Please provide:**
1. Manus AI API key
2. API endpoint URL
3. Request/response format

### OpenAI API
- **Model:** `gpt-4` or `o1-preview` (which do you prefer?)
- **Max tokens:** 16000 (for full HTML output)
- **Temperature:** 0.7
- **System prompt:** "You are an elite pre-call revenue intelligence analyst."

## Prompt Template

Your full Pre-Brief prompt is ~5000+ lines. I can:

**Option A:** Store it in a separate file (`prompts.py`)
**Option B:** Store it in a text file and read it
**Option C:** Hard-code it in workflow.py

Which do you prefer?

## Testing Plan

Once implemented:

1. **Test Manus AI** → Verify analysis output
2. **Test OpenAI** → Verify HTML generation
3. **Test N8N Doc** → Verify Google Doc creation
4. **Test Callback** → Verify Flask receives link
5. **Test Email** → Verify email sent with link
6. **End-to-End** → Full workflow test

## Next Steps

To proceed, I need from you:

1. ✅ Manus AI API key
2. ✅ Manus AI API endpoint and docs
3. ✅ Confirm OpenAI model (gpt-4 or o1-preview)
4. ✅ Confirm prompt storage method
5. ✅ Update recipient email in .env

Once I have these, I can implement the complete workflow!
