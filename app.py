from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import requests
import json
from datetime import datetime
import os
import threading
from workflow import WorkflowProcessor

app = Flask(__name__)
app.secret_key = 'mario-n8n-webhook-secret-key-2026'  # Change this in production

# Initialize workflow processor
workflow_processor = WorkflowProcessor()

# Store processing status in memory (use Redis/database for production)
processing_status = {}

# Store batch processing results
batch_results = {}  # batch_id -> {'prospects': [], 'results': [], 'total': n, 'completed': 0}

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

# Route: Process workflow (test mode)
@app.route('/api/process/test', methods=['POST'])
def process_workflow_test():
    """Process prospects through complete workflow (test mode)"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        # Parse prospects from data
        prospects = []

        # Check if it's a bulk CSV upload
        if 'items' in data and isinstance(data['items'], list):
            prospects = data['items']
        else:
            # Single prospect
            prospects = [data]

        # Generate unique batch ID
        import uuid
        batch_id = str(uuid.uuid4())
        is_batch = len(prospects) > 1

        # Generate callback URL before thread (must be in request context)
        callback_url = request.url_root.rstrip('/') + '/api/webhook/callback'

        # Store initial status
        processing_status[batch_id] = {
            'status': 'processing',
            'total': len(prospects),
            'processed': 0,
            'message': 'Starting workflow...',
            'is_batch': is_batch
        }

        # Initialize batch results storage if batch mode
        if is_batch:
            batch_results[batch_id] = {
                'prospects': prospects,
                'results': [],
                'total': len(prospects),
                'completed': 0
            }

        # Process in background thread
        def process_in_background():
            if len(prospects) > 0:
                if is_batch:
                    # BATCH MODE: Process all prospects individually
                    print(f"📦 Batch processing {len(prospects)} prospects...")

                    for idx, prospect in enumerate(prospects):
                        prospect_job_id = f"{batch_id}-{idx}"

                        print(f"🎯 Processing prospect {idx+1}/{len(prospects)}")

                        # Process each prospect through complete workflow
                        result = workflow_processor.process_prospect(
                            prospect_data=prospect,
                            job_id=prospect_job_id,
                            callback_url=callback_url,
                            is_test_mode=True
                        )

                        # Store prospect info with job_id for callback matching
                        batch_results[batch_id]['results'].append({
                            'job_id': prospect_job_id,
                            'company': prospect.get('Company_Name', 'N/A'),
                            'first_name': prospect.get('First_Name', 'N/A'),
                            'last_name': prospect.get('Last_Name', 'N/A'),
                            'title': prospect.get('Title', 'N/A'),
                            'email': prospect.get('Email', 'N/A'),
                            'website': prospect.get('Website', 'N/A'),
                            'document1_url': None,  # Will be filled by callback
                            'document2_url': None   # Will be filled by callback
                        })

                    processing_status[batch_id]['message'] = f'All {len(prospects)} prospects sent to N8N, waiting for callbacks...'

                else:
                    # SINGLE MODE: Process the first prospect
                    prospect = prospects[0]

                    # Process the prospect through complete workflow
                    result = workflow_processor.process_prospect(
                        prospect_data=prospect,
                        job_id=batch_id,
                        callback_url=callback_url,
                        is_test_mode=True
                    )

                    processing_status[batch_id] = {
                        'status': 'processing' if result.get('success') else 'failed',
                        'result': result,
                        'message': result.get('message', ''),
                        'is_batch': False
                    }
            else:
                processing_status[batch_id] = {
                    'status': 'failed',
                    'error': 'No prospects to process'
                }

        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()

        return jsonify({
            "success": True,
            "job_id": batch_id,
            "message": f"Processing {len(prospects)} prospect(s) in test mode...",
            "status_url": f"/api/status/{batch_id}",
            "is_batch": is_batch
        }), 202

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Route: Process workflow (production mode)
@app.route('/api/process/prod', methods=['POST'])
def process_workflow_prod():
    """Process prospects through complete workflow (production mode)"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        # Parse prospects from data
        prospects = []

        # Check if it's a bulk CSV upload
        if 'items' in data and isinstance(data['items'], list):
            prospects = data['items']
        else:
            # Single prospect
            prospects = [data]

        # Generate unique batch ID
        import uuid
        batch_id = str(uuid.uuid4())
        is_batch = len(prospects) > 1

        # Generate callback URL before thread (must be in request context)
        callback_url = request.url_root.rstrip('/') + '/api/webhook/callback'

        # Store initial status
        processing_status[batch_id] = {
            'status': 'processing',
            'total': len(prospects),
            'processed': 0,
            'message': 'Starting workflow...',
            'is_batch': is_batch
        }

        # Initialize batch results storage if batch mode
        if is_batch:
            batch_results[batch_id] = {
                'prospects': prospects,
                'results': [],
                'total': len(prospects),
                'completed': 0
            }

        # Process in background thread
        def process_in_background():
            if len(prospects) > 0:
                if is_batch:
                    # BATCH MODE: Process all prospects individually
                    print(f"📦 Batch processing {len(prospects)} prospects...")

                    for idx, prospect in enumerate(prospects):
                        prospect_job_id = f"{batch_id}-{idx}"

                        print(f"🎯 Processing prospect {idx+1}/{len(prospects)}")

                        # Process each prospect through complete workflow
                        result = workflow_processor.process_prospect(
                            prospect_data=prospect,
                            job_id=prospect_job_id,
                            callback_url=callback_url,
                            is_test_mode=False
                        )

                        # Store prospect info with job_id for callback matching
                        batch_results[batch_id]['results'].append({
                            'job_id': prospect_job_id,
                            'company': prospect.get('Company_Name', 'N/A'),
                            'first_name': prospect.get('First_Name', 'N/A'),
                            'last_name': prospect.get('Last_Name', 'N/A'),
                            'title': prospect.get('Title', 'N/A'),
                            'email': prospect.get('Email', 'N/A'),
                            'website': prospect.get('Website', 'N/A'),
                            'document1_url': None,  # Will be filled by callback
                            'document2_url': None   # Will be filled by callback
                        })

                    processing_status[batch_id]['message'] = f'All {len(prospects)} prospects sent to N8N, waiting for callbacks...'

                else:
                    # SINGLE MODE: Process the first prospect
                    prospect = prospects[0]

                    # Process the prospect through complete workflow
                    result = workflow_processor.process_prospect(
                        prospect_data=prospect,
                        job_id=batch_id,
                        callback_url=callback_url,
                        is_test_mode=False
                    )

                    processing_status[batch_id] = {
                        'status': 'processing' if result.get('success') else 'failed',
                        'result': result,
                        'message': result.get('message', ''),
                        'is_batch': False
                    }
            else:
                processing_status[batch_id] = {
                    'status': 'failed',
                    'error': 'No prospects to process'
                }

        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()

        return jsonify({
            "success": True,
            "job_id": batch_id,
            "message": f"Processing {len(prospects)} prospect(s) in production mode...",
            "status_url": f"/api/status/{batch_id}",
            "is_batch": is_batch
        }), 202

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Route: N8N Callback - receives document URLs after processing
@app.route('/api/webhook/callback', methods=['POST'])
def n8n_callback():
    """Receive callback from N8N with document URLs"""
    try:
        data = request.json
        job_id = data.get('job_id')

        print(f"📞 Received callback for job_id: {job_id}")
        print(f"   Doc 1: {data.get('document1_url')}")
        print(f"   Doc 2: {data.get('document2_url')}")

        # Extract batch_id from job_id (format: batch_id or batch_id-idx)
        batch_id = job_id.split('-')[0] if '-' in job_id else job_id

        # Check if this is a batch job
        if batch_id in batch_results:
            # BATCH MODE: Update the specific prospect's document URLs
            print(f"📦 Batch mode callback for batch {batch_id}")

            # Find the result entry for this job_id
            for result in batch_results[batch_id]['results']:
                if result['job_id'] == job_id:
                    result['document1_url'] = data.get('document1_url', 'N/A')
                    result['document2_url'] = data.get('document2_url', 'N/A')
                    batch_results[batch_id]['completed'] += 1
                    print(f"✅ Updated docs for {result['company']} ({batch_results[batch_id]['completed']}/{batch_results[batch_id]['total']})")
                    break

            # Check if all prospects have been processed
            if batch_results[batch_id]['completed'] >= batch_results[batch_id]['total']:
                print(f"🎉 All {batch_results[batch_id]['total']} prospects completed!")
                print(f"📊 Generating results CSV...")

                # Generate CSV
                csv_content = workflow_processor.generate_results_csv(batch_results[batch_id]['results'])

                # Send CSV via email
                recipient_email = os.getenv('BATCH_RESULTS_EMAIL', 'mehroz.muneer@gmail.com')
                email_result = workflow_processor.send_results_csv_email(csv_content, recipient_email, batch_id)

                if email_result.get('success'):
                    print(f"✅ Results CSV sent to {recipient_email}")
                    processing_status[batch_id]['status'] = 'completed'
                    processing_status[batch_id]['message'] = f'Batch complete. CSV sent to {recipient_email}'
                    processing_status[batch_id]['completed'] = True
                else:
                    print(f"⚠️  Failed to send CSV: {email_result.get('error')}")
                    processing_status[batch_id]['status'] = 'completed with errors'
                    processing_status[batch_id]['message'] = 'Batch complete but email failed'

            return jsonify({
                "success": True,
                "message": "Batch callback received"
            }), 200

        # SINGLE MODE: Original behavior
        elif batch_id in processing_status:
            print(f"👤 Single mode callback")

            # Update job status with document URLs
            processing_status[batch_id]['document1_url'] = data.get('document1_url', 'N/A')
            processing_status[batch_id]['document2_url'] = data.get('document2_url', 'N/A')
            processing_status[batch_id]['status'] = 'sending email'

            # Send email with document links via n8n
            email_webhook = os.getenv('N8N_WEBHOOK_EMAIL', '')
            if email_webhook:
                try:
                    email_payload = {
                        'document1_url': data.get('document1_url'),
                        'document2_url': data.get('document2_url')
                    }

                    print(f"📧 Sending email via n8n...")
                    email_response = requests.post(email_webhook, json=email_payload, timeout=30)

                    if email_response.status_code == 200:
                        print(f"✅ Email sent successfully")
                        processing_status[batch_id]['email_sent'] = True
                    else:
                        print(f"⚠️  Email webhook failed: {email_response.status_code}")
                        processing_status[batch_id]['email_sent'] = False

                except Exception as email_error:
                    print(f"⚠️  Email error: {str(email_error)}")
                    processing_status[batch_id]['email_sent'] = False

            # Mark as completed
            processing_status[batch_id]['status'] = 'completed'
            processing_status[batch_id]['completed'] = True

            return jsonify({
                "success": True,
                "message": "Callback received"
            }), 200

        else:
            print(f"⚠️  Job ID not found: {job_id}")
            return jsonify({
                "success": False,
                "error": "Invalid job_id"
            }), 400

    except Exception as e:
        print(f"❌ Callback error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Route: Check processing status
@app.route('/api/status/<job_id>', methods=['GET'])
def check_status(job_id):
    """Check the status of a processing job"""
    if job_id not in processing_status:
        return jsonify({
            "success": False,
            "error": "Job not found"
        }), 404

    status = processing_status[job_id]

    return jsonify({
        "success": True,
        "status": status
    }), 200

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
