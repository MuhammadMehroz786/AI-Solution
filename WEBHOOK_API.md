# Webhook API Documentation

This Flask API allows you to receive webhook data and automatically forward it to your n8n workflows.

## Installation

```bash
pip install flask
```

## Running the Webhook API

```bash
python webhook_api.py
```

The API will start on `http://localhost:5000`

## Endpoints

### 1. `/webhook/test` (POST)
Forward data to n8n **test** webhook endpoint.

**Example Request:**
```bash
curl -X POST http://localhost:5000/webhook/test \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "John Doe",
    "Email": "john@example.com",
    "Meeting brief": "Initial consultation"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Data forwarded to n8n successfully",
  "n8n_response": "{\"message\":\"Workflow was started\"}"
}
```

### 2. `/webhook/prod` (POST)
Forward data to n8n **production** webhook endpoint.

**Example Request:**
```bash
curl -X POST http://localhost:5000/webhook/prod \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "Jane Smith",
    "Email": "jane@example.com",
    "Meeting brief": "Follow-up meeting"
  }'
```

### 3. `/webhook/batch` (POST)
Forward multiple items to n8n at once.

**Example Request:**
```bash
curl -X POST http://localhost:5000/webhook/batch \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "prod",
    "items": [
      {
        "Name": "John Doe",
        "Email": "john@example.com",
        "Meeting brief": "Initial consultation"
      },
      {
        "Name": "Jane Smith",
        "Email": "jane@example.com",
        "Meeting brief": "Follow-up meeting"
      }
    ]
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Forwarded 2 items to n8n successfully",
  "total_items": 2,
  "mode": "prod",
  "n8n_response": "{\"message\":\"Workflow was started\"}"
}
```

### 4. `/health` (GET)
Health check endpoint.

**Example Request:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "N8N Webhook Forwarder"
}
```

## Use Cases

### 1. Receive webhooks from external services
Other applications can send data to your webhook API, which then forwards it to n8n.

### 2. Integration with automation tools
Use tools like Zapier, Make.com, or custom scripts to send data through this API.

### 3. Centralized webhook management
All webhook requests go through this API, providing a single point of control.

## Running Both Services Together

### Terminal 1 - Streamlit Dashboard:
```bash
streamlit run dashboard.py
```
Access at: http://localhost:8501

### Terminal 2 - Webhook API:
```bash
python webhook_api.py
```
Access at: http://localhost:5000

## Deployment

For production deployment, consider using:
- **Gunicorn** for the Flask API
- **Streamlit Cloud** or **Heroku** for the Streamlit dashboard
- **Nginx** as a reverse proxy

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 webhook_api:app
```
