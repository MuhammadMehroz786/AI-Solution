# N8N Webhook Manager

A beautiful Flask web application to receive webhook data and forward it to N8N workflows.

## Features

- 🔐 **Login system** - Secure access with username/password
- ✅ **Receive webhooks** from external sources
- 📊 **Beautiful tabbed interface** to view received data
- 🗄️ **SQLite database** to store all incoming data
- 🚀 **Send data to N8N** (test and production modes)
- 📄 **CSV upload** support with template download
- 🔄 **Auto-refresh** every 30 seconds
- 🗑️ **Delete records** with one click

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

The app will start on **http://localhost:5000**

## Usage

### 1. View Dashboard
Open your browser and go to:
```
http://localhost:5000
```

You'll see a beautiful interface showing all received webhook data.

### 2. Receive Webhook Data
Send POST requests to receive endpoint:

```bash
curl -X POST http://localhost:5000/api/receive \
  -H "Content-Type: application/json" \
  -d '{
    "Email": "user@example.com",
    "Summary": "This is a summary of the document",
    "Document_Link_1": "https://example.com/doc1.pdf",
    "Document_Link_2": "https://example.com/doc2.pdf"
  }'
```

### 3. Send Data to N8N

**Test Mode:**
```bash
curl -X POST http://localhost:5000/api/send/test \
  -H "Content-Type: application/json" \
  -d '{
    "Email": "user@example.com",
    "Summary": "Document summary",
    "Document_Link_1": "https://example.com/doc1.pdf",
    "Document_Link_2": "https://example.com/doc2.pdf"
  }'
```

**Production Mode:**
```bash
curl -X POST http://localhost:5000/api/send/prod \
  -H "Content-Type: application/json" \
  -d '{
    "Email": "user@example.com",
    "Summary": "Document summary",
    "Document_Link_1": "https://example.com/doc1.pdf",
    "Document_Link_2": "https://example.com/doc2.pdf"
  }'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | View dashboard with all received data |
| `/api/receive` | POST | Receive webhook data from external sources |
| `/api/send/test` | POST | Send data to N8N test webhook |
| `/api/send/prod` | POST | Send data to N8N production webhook |
| `/api/data` | GET | Get all data as JSON |
| `/api/delete/<id>` | DELETE | Delete a specific record |
| `/health` | GET | Health check |

## Data Format

All webhook data must include these fields:

```json
{
  "Email": "user@example.com",
  "Summary": "Document summary text",
  "Document_Link_1": "https://link-to-document-1",
  "Document_Link_2": "https://link-to-document-2"
}
```

## Database

The app uses SQLite database (`webhook_data.db`) to store all received data.

**Schema:**
- `id` - Auto-increment primary key
- `email` - User email
- `summary` - Document summary
- `document_link_1` - First document link
- `document_link_2` - Second document link
- `received_at` - Timestamp when data was received

## Features

### Dashboard
- Clean, modern interface
- Real-time data display
- Auto-refresh every 30 seconds
- Click to delete records
- Responsive design

### Validation
- Automatic validation of required fields
- Email format validation
- Error handling and reporting

### Security
- Input validation
- SQL injection prevention (parameterized queries)
- Error logging

## Deployment

### Railway Deployment

1. Push code to GitHub:
```bash
cd "/Users/apple/Desktop/Bot/Mario - N8N"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/MuhammadMehroz786/AI-Solution.git
git push -u origin main
```

2. Deploy on Railway:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `MuhammadMehroz786/AI-Solution`
   - Railway will automatically detect the `Procfile` and deploy

3. Your app will be live at: `https://your-app.up.railway.app`

### Manual Deployment

For other platforms:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:$PORT app:app
```

Or use Docker, Heroku, or any cloud platform that supports Flask applications.
