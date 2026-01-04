# Dream 100 Advantage - Prospect Intelligence

A beautiful Flask web application to capture and forward prospect intelligence data to N8N workflows.

## Features

- 🔐 **Login system** - Secure access with username/password
- 👤 **Single Prospect Input** - Add individual prospects with detailed information
- 📊 **Bulk CSV Upload** - Upload multiple prospects at once
- 🚀 **Send to N8N** - Test and production webhook modes
- 📄 **CSV template** - Download template for bulk uploads
- 💜 **Beautiful UI** - Modern purple gradient design

## Login Credentials

- **Username:** `emrgmedia`
- **Password:** `Mario`

## Installation

```bash
pip install -r requirements.txt
```

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

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | View Dream 100 Advantage dashboard |
| `/login` | GET/POST | Login page |
| `/logout` | GET | Logout |
| `/api/send/test` | POST | Send data to N8N test webhook |
| `/api/send/prod` | POST | Send data to N8N production webhook |
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

## N8N Webhooks

- **Test Mode:** `https://n8n.eventplanners.cloud/webhook-test/2af2ce4c-6c51-4935-9f0a-1a019d4bd466`
- **Production Mode:** `https://n8n.eventplanners.cloud/webhook/2af2ce4c-6c51-4935-9f0a-1a019d4bd466`

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Railway
- **Server:** Gunicorn
