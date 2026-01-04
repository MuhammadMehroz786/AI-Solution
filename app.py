from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'mario-n8n-webhook-secret-key-2026'  # Change this in production

# Login credentials
USERNAME = 'emrgmedia'
PASSWORD = 'Mario'

# Webhook URLs for sending data to n8n
WEBHOOK_TEST = "https://n8n.eventplanners.cloud/webhook-test/2af2ce4c-6c51-4935-9f0a-1a019d4bd466"
WEBHOOK_PROD = "https://n8n.eventplanners.cloud/webhook/2af2ce4c-6c51-4935-9f0a-1a019d4bd466"

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

# Route: Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

# Route: Logout
@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Route: Homepage - Dream 100 Advantage Dashboard
@app.route('/')
def index():
    """Display Dream 100 Advantage dashboard"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('index.html')

# Route: Send single prospect to n8n (test mode)
@app.route('/api/send/test', methods=['POST'])
def send_to_n8n_test():
    """Send data to n8n test webhook"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        result = send_to_n8n(WEBHOOK_TEST, data)

        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Data sent to n8n test webhook successfully",
                "n8n_response": result["response"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to send to n8n"),
                "details": result
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Route: Send data to n8n (production mode)
@app.route('/api/send/prod', methods=['POST'])
def send_to_n8n_prod():
    """Send data to n8n production webhook"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        result = send_to_n8n(WEBHOOK_PROD, data)

        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Data sent to n8n production webhook successfully",
                "n8n_response": result["response"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to send to n8n"),
                "details": result
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Route: Health check
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Dream 100 Advantage - Prospect Intelligence"
    }), 200

if __name__ == '__main__':
    # Run the app
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
