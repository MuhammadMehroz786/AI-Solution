from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import requests
import json
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'mario-n8n-webhook-secret-key-2026'  # Change this in production

# Login credentials
USERNAME = 'emrgmedia'
PASSWORD = 'Mario'

# Webhook URLs for sending data to n8n
WEBHOOK_TEST = "https://n8n.eventplanners.cloud/webhook-test/2af2ce4c-6c51-4935-9f0a-1a019d4bd466"
WEBHOOK_PROD = "https://n8n.eventplanners.cloud/webhook/2af2ce4c-6c51-4935-9f0a-1a019d4bd466"

# Database setup
DATABASE = 'webhook_data.db'

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS received_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            summary TEXT,
            document_link_1 TEXT,
            document_link_2 TEXT,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_all_data():
    """Get all received data from database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM received_data ORDER BY received_at DESC')
    rows = c.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'summary': row[3],
            'document_link_1': row[4],
            'document_link_2': row[5],
            'received_at': row[6]
        })
    return data

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

# Route 1: Homepage - Display all received data
@app.route('/')
def index():
    """Display all received webhook data in a nice HTML interface"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    data = get_all_data()
    return render_template('index.html', data=data, total=len(data))

# Route 2: Receive webhook data (incoming from external sources)
@app.route('/api/receive', methods=['POST'])
def receive_webhook():
    """
    Receive webhook data from external sources
    Expected format:
    {
        "Name": "John Doe",
        "Email": "user@example.com",
        "Summary": "Document summary...",
        "Document_Link_1": "https://...",
        "Document_Link_2": "https://..."
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        # Validate required fields
        required_fields = ["Name", "Email", "Summary", "Document_Link_1", "Document_Link_2"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Store in database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO received_data (name, email, summary, document_link_1, document_link_2)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['Name'], data['Email'], data['Summary'], data['Document_Link_1'], data['Document_Link_2']))
        conn.commit()
        record_id = c.lastrowid
        conn.close()

        return jsonify({
            "success": True,
            "message": "Data received and stored successfully",
            "record_id": record_id,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Route 3: Send data to n8n (test mode)
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

# Route 4: Send data to n8n (production mode)
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

# Route 5: Get all data as JSON
@app.route('/api/data', methods=['GET'])
def get_data_api():
    """Get all received data as JSON"""
    data = get_all_data()
    return jsonify({
        "success": True,
        "total": len(data),
        "data": data
    })

# Route 6: Delete a record
@app.route('/api/delete/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """Delete a specific record"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('DELETE FROM received_data WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": f"Record {record_id} deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Route 7: Health check
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "N8N Webhook Manager",
        "database": "connected" if os.path.exists(DATABASE) else "not initialized"
    }), 200

if __name__ == '__main__':
    # Initialize database
    init_db()
    # Run the app
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
