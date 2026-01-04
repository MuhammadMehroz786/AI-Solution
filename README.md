# Dream 100 Advantage - Prospect Intelligence

A powerful Flask web application that provides complete prospect intelligence automation. Instead of just sending data to n8n webhooks, this application now processes the entire workflow in-house:

- Website scraping (Apify)
- AI analysis (Manus AI)
- Document generation (OpenAI)
- Google Docs/Sheets creation
- Email notifications

## Features

- 🔐 **Login system** - Secure access with username/password
- 👤 **Single Prospect Input** - Add individual prospects with detailed information
- 📊 **Bulk CSV Upload** - Upload multiple prospects at once
- 🤖 **Complete AI Workflow** - Automated prospect intelligence pipeline
- 📄 **Document Generation** - Revenue Intelligence Pre-Brief & Sales Snapshot
- 📧 **Email Notifications** - Automatic alerts when processing completes
- 💙 **Beautiful UI** - Modern blue gradient design with real-time status updates

## Login Credentials

- **Username:** `emrgmedia`
- **Password:** `Mario`

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the root directory with your API keys:

```bash
cp .env.example .env
```

Then edit `.env` and add your credentials:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Apify API
APIFY_API_TOKEN=your_apify_api_token_here

# Manus AI API
MANUS_API_KEY=your_manus_api_key_here

# Email Configuration
SENDER_EMAIL=your_sender_email@gmail.com
RECIPIENT_EMAIL=your_recipient_email@gmail.com

# Workflow Settings
GOOGLE_SHEET_NAME=Dream 100 Prospects
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id
```

### 3. Setup Google API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - Google Sheets API
   - Google Docs API
   - Google Drive API
   - Gmail API
4. Create a Service Account
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place in the root directory

### 4. Get API Keys

**OpenAI API Key:**
- Sign up at [platform.openai.com](https://platform.openai.com/)
- Go to API Keys section
- Create new secret key

**Apify API Token:**
- Sign up at [apify.com](https://apify.com/)
- Go to Settings → Integrations
- Copy your API token

**Manus AI API Key:**
- Sign up at [manus.ai](https://manus.ai/)
- Get your API key from the dashboard

## Running the Application

```bash
python app.py
```

The app will start on **http://localhost:8000**

## Usage

### 1. View Dashboard
Open your browser and go to:
```
http://localhost:8000
```

Login with the credentials above to access the Dream 100 Advantage dashboard.

### 2. Single Prospect Input

Add individual prospects with the following information:
- Company Name
- First Name
- Last Name
- LinkedIn Profile URL
- Email Address

Choose between Test Mode and Production Mode before submitting.

When you submit, the system will:
1. Create a Google Sheet for tracking
2. Scrape the company website
3. Analyze the website with AI
4. Generate a Revenue Intelligence Pre-Brief
5. Generate an Internal Sales Snapshot
6. Create Google Docs for both documents
7. Add the data to Google Sheets
8. Send an email notification

### 3. Bulk CSV Upload

1. Click "Download CSV Template" to get the correct format
2. Fill in prospect data:
   - Company Name
   - First Name
   - Last Name
   - Job Title
   - Email Address
   - Website
3. Upload the CSV file
4. Choose Test or Production mode
5. Click "Upload Prospects"

The system will process all prospects through the complete workflow and provide a link to the results spreadsheet.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | View Dream 100 Advantage dashboard |
| `/login` | GET/POST | Login page |
| `/logout` | GET | Logout |
| `/api/process/test` | POST | Process prospects through workflow (test mode) |
| `/api/process/prod` | POST | Process prospects through workflow (production mode) |
| `/api/status/<job_id>` | GET | Check processing job status |
| `/api/send/test` | POST | Legacy: Send data to N8N test webhook |
| `/api/send/prod` | POST | Legacy: Send data to N8N production webhook |
| `/health` | GET | Health check |

## Data Format

### Single Prospect Input

```json
{
  "Company_Name": "Acme Corp",
  "First_Name": "John",
  "Last_Name": "Doe",
  "LinkedIn_URL": "https://linkedin.com/in/johndoe",
  "Email": "john.doe@acme.com"
}
```

### Bulk CSV Upload

```json
{
  "Company_Name": "Acme Corp",
  "First_Name": "John",
  "Last_Name": "Doe",
  "Job_Title": "CEO",
  "Email": "john.doe@acme.com",
  "Website": "https://acme.com"
}
```

## Security

- Session-based authentication
- Input validation
- SQL injection prevention (no database used)
- Secure password handling

## Deployment

### Railway Deployment

1. Push code to GitHub:
```bash
cd "/Users/apple/Desktop/Bot/Mario - N8N"
git add .
git commit -m "Update to Dream 100 Advantage design"
git push origin main
```

2. Railway will automatically detect changes and redeploy

3. Your app is live at: `https://web-production-6dc3.up.railway.app`

### Manual Deployment

For other platforms:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:$PORT app:app
```

Or use Docker, Heroku, or any cloud platform that supports Flask applications.

## Workflow Architecture

The application orchestrates the workflow using n8n webhooks and Apify:

1. **Web Scraping** - Apify API scrapes company websites (direct integration)
2. **Document Generation** - N8N webhook creates both documents:
   - Revenue Intelligence Pre-Brief
   - Internal Sales Snapshot
3. **Google Sheet Management** - N8N webhook:
   - Creates Google Sheet for tracking
   - Returns empty sheet with column headers
   - Appends prospect data with document links

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Integrations:**
  - Apify API (Web Scraping)
  - N8N Webhooks (Document Generation & Google Sheets)
- **Deployment:** Railway
- **Server:** Gunicorn

## Legacy N8N Webhooks (Still Supported)

The old webhook endpoints are still available:
- **Test Mode:** `https://n8n.eventplanners.cloud/webhook-test/2af2ce4c-6c51-4935-9f0a-1a019d4bd466`
- **Production Mode:** `https://n8n.eventplanners.cloud/webhook/2af2ce4c-6c51-4935-9f0a-1a019d4bd466`
