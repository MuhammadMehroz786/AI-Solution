from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# Webhook URLs
WEBHOOK_TEST = "https://n8n.eventplanners.cloud/webhook-test/2af2ce4c-6c51-4935-9f0a-1a019d4bd466"
WEBHOOK_PROD = "https://n8n.eventplanners.cloud/webhook/2af2ce4c-6c51-4935-9f0a-1a019d4bd466"

def validate_data(data):
    """Validate incoming data has required fields"""
    required_fields = ["Email", "Summary", "Document_Link_1", "Document_Link_2"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    # Basic email validation
    if "@" not in data.get("Email", ""):
        return False, "Invalid email format"

    return True, None

def send_to_n8n(webhook_url, data):
    """Send data to n8n webhook"""
    try:
        response = requests.post(webhook_url, json=data, timeout=30)
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.text
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.route('/webhook/test', methods=['POST'])
def webhook_test():
    """Receive webhook data and forward to n8n test endpoint"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        # Forward to n8n
        result = send_to_n8n(WEBHOOK_TEST, data)

        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Data forwarded to n8n successfully",
                "n8n_response": result["response"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to forward to n8n"),
                "details": result
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/webhook/prod', methods=['POST'])
def webhook_prod():
    """Receive webhook data and forward to n8n production endpoint"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        # Forward to n8n
        result = send_to_n8n(WEBHOOK_PROD, data)

        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Data forwarded to n8n successfully",
                "n8n_response": result["response"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to forward to n8n"),
                "details": result
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/webhook/batch', methods=['POST'])
def webhook_batch():
    """
    Receive multiple items and forward to n8n
    Expected format: {"items": [...], "mode": "test" or "prod"}
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        items = data.get("items", [])
        mode = data.get("mode", "prod")

        if not items:
            return jsonify({
                "success": False,
                "error": "No items provided"
            }), 400

        # Select webhook URL based on mode
        webhook_url = WEBHOOK_TEST if mode == "test" else WEBHOOK_PROD

        # Forward to n8n
        payload = {"items": items}
        result = send_to_n8n(webhook_url, payload)

        if result["success"]:
            return jsonify({
                "success": True,
                "message": f"Forwarded {len(items)} items to n8n successfully",
                "total_items": len(items),
                "mode": mode,
                "n8n_response": result["response"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to forward to n8n"),
                "details": result
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "N8N Webhook Forwarder"
    }), 200

@app.route('/', methods=['GET'])
def home():
    """API documentation"""
    return jsonify({
        "service": "N8N Webhook Forwarder API",
        "version": "1.0",
        "endpoints": {
            "/webhook/test": {
                "method": "POST",
                "description": "Forward data to n8n test webhook",
                "example": {
                    "Name": "John Doe",
                    "Email": "john@example.com",
                    "Meeting brief": "Initial consultation"
                }
            },
            "/webhook/prod": {
                "method": "POST",
                "description": "Forward data to n8n production webhook",
                "example": {
                    "Name": "John Doe",
                    "Email": "john@example.com",
                    "Meeting brief": "Initial consultation"
                }
            },
            "/webhook/batch": {
                "method": "POST",
                "description": "Forward multiple items to n8n",
                "example": {
                    "mode": "prod",
                    "items": [
                        {
                            "Name": "John Doe",
                            "Email": "john@example.com",
                            "Meeting brief": "Initial consultation"
                        }
                    ]
                }
            },
            "/health": {
                "method": "GET",
                "description": "Health check"
            }
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
