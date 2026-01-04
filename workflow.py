"""
Dream 100 Advantage - Workflow Processing Module
Complete workflow: Apify → Manus AI → OpenAI (2 docs) → N8N → Email
"""

import os
import requests
import json
import csv
import io
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
MANUS_API_KEY = os.getenv('MANUS_API_KEY', '')
MANUS_MODEL = os.getenv('MANUS_MODEL', 'manus-1.6-max')
APIFY_API_TOKEN = os.getenv('APIFY_API_TOKEN', '')

# N8N Webhook Configuration
N8N_WEBHOOK_DOC_GENERATION = os.getenv('N8N_WEBHOOK_DOC_GENERATION', '')
N8N_WEBHOOK_DOC_GENERATION_TEST = os.getenv('N8N_WEBHOOK_DOC_GENERATION_TEST', '')
N8N_WEBHOOK_SHEET_CREATION = os.getenv('N8N_WEBHOOK_SHEET_CREATION', '')


class WorkflowProcessor:
    """Process prospects through the complete intelligence workflow"""

    def __init__(self):
        self.doc_webhook = N8N_WEBHOOK_DOC_GENERATION
        self.doc_webhook_test = N8N_WEBHOOK_DOC_GENERATION_TEST
        self.sheet_webhook = N8N_WEBHOOK_SHEET_CREATION
        self.openai_api_key = OPENAI_API_KEY
        self.manus_api_key = MANUS_API_KEY
        self.manus_model = MANUS_MODEL

        # Load prompts from files
        self.prompt_manus = self._load_prompt('prompt_manus_analysis.txt')
        self.prompt_pre_brief = self._load_prompt('prompt_pre_brief.txt')
        self.prompt_sales_snapshot = self._load_prompt('prompt_sales_snapshot.txt')

    def _load_prompt(self, filename: str) -> str:
        """Load prompt template from file"""
        try:
            filepath = os.path.join(os.path.dirname(__file__), filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Could not load {filename}: {e}")
            return ""

    def scrape_website_apify(self, website_url: str) -> Dict:
        """Scrape website using Apify API (sync endpoint)"""
        if not APIFY_API_TOKEN:
            return {'error': 'Apify API token not configured'}

        try:
            # Ensure URL has protocol
            if not website_url.startswith('http'):
                website_url = 'https://' + website_url

            # Use Apify Website Content Crawler with sync endpoint
            run_input = {
                'startUrls': [{'url': website_url}],
                'maxCrawlPages': 5,
                'crawlerType': 'playwright:firefox'
            }

            print(f"🔍 Scraping website: {website_url}")

            # Use the synchronous run endpoint
            response = requests.post(
                'https://api.apify.com/v2/acts/apify~website-content-crawler/run-sync-get-dataset-items',
                params={'token': APIFY_API_TOKEN},
                json=run_input,
                timeout=120  # 2 minutes timeout for sync call
            )

            if response.status_code == 200 or response.status_code == 201:
                results = response.json()
                print(f"✅ Website scraped successfully: {len(results)} pages")
                return {
                    'success': True,
                    'data': results
                }
            else:
                return {'error': f'Apify scraping failed: {response.status_code} - {response.text}'}

        except requests.exceptions.Timeout:
            return {'error': 'Apify request timed out'}
        except Exception as e:
            return {'error': f'Apify scraping error: {str(e)}'}

    def analyze_with_manus(self, website_url: str, company_name: str, website_data: Dict) -> str:
        """Analyze company with Manus AI"""
        if not self.manus_api_key:
            return "Error: Manus AI API not configured"

        try:
            print(f"🤖 Analyzing with Manus AI: {company_name}")

            # Format website data for Manus
            website_content = json.dumps(website_data, indent=2)

            # Fill in the prompt template
            prompt = self.prompt_manus.format(
                url=website_url,
                company_name=company_name
            )

            # Add website content to the prompt
            full_prompt = f"{prompt}\n\nWEBSITE DATA:\n{website_content}"

            # Call Manus AI API
            headers = {
                'Authorization': f'Bearer {self.manus_api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                "model": self.manus_model,
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": 0.7
            }

            response = requests.post(
                'https://api.manus.im/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                print(f"✅ Manus AI analysis completed")
                return analysis
            else:
                error_msg = f"Manus AI error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return f"Error: {error_msg}"

        except Exception as e:
            error_msg = f"Manus AI error: {str(e)}"
            print(f"❌ {error_msg}")
            return f"Error: {error_msg}"

    def generate_pre_brief_openai(self, url: str, first_name: str, last_name: str,
                                   website_content: str, manus_analysis: str) -> str:
        """Generate Revenue Intelligence Pre-Brief using OpenAI with full template"""
        if not self.openai_api_key:
            return "Error: OpenAI API not configured"

        try:
            print(f"📄 Generating Pre-Brief with OpenAI...")

            # Fill in the prompt template
            prompt = self.prompt_pre_brief.format(
                url=url,
                first_name=first_name,
                last_name=last_name,
                website_content=website_content,
                manus_analysis=manus_analysis
            )

            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are an elite pre-call revenue intelligence analyst. Output ONLY raw HTML with no markdown, no code blocks, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 16000
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                html_content = result['choices'][0]['message']['content']
                print(f"✅ Pre-Brief generated successfully")
                return html_content
            else:
                error_msg = f"OpenAI error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return f"Error generating pre-brief: {error_msg}"

        except Exception as e:
            error_msg = f"Error generating pre-brief: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

    def generate_sales_snapshot_openai(self, url: str, first_name: str, last_name: str,
                                       website_content: str, manus_analysis: str) -> str:
        """Generate Internal Sales Snapshot using OpenAI with full template"""
        if not self.openai_api_key:
            return "Error: OpenAI API not configured"

        try:
            print(f"📊 Generating Sales Snapshot with OpenAI...")

            # Fill in the prompt template
            prompt = self.prompt_sales_snapshot.format(
                url=url,
                first_name=first_name,
                last_name=last_name,
                website_content=website_content,
                manus_analysis=manus_analysis
            )

            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are an elite internal sales strategist. Output ONLY raw HTML with no markdown, no code blocks, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 16000
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                html_content = result['choices'][0]['message']['content']
                print(f"✅ Sales Snapshot generated successfully")
                return html_content
            else:
                error_msg = f"OpenAI error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return f"Error generating sales snapshot: {error_msg}"

        except Exception as e:
            error_msg = f"Error generating sales snapshot: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

    def send_documents_to_n8n(self, pre_brief_content: str, sales_snapshot_content: str,
                              prospect_data: Dict, job_id: str, callback_url: str,
                              is_test_mode: bool = False) -> Dict:
        """Send generated OpenAI content to n8n webhook for Google Doc creation (async)"""
        webhook_url = self.doc_webhook_test if is_test_mode else self.doc_webhook

        if not webhook_url:
            return {'error': 'Document generation webhook not configured'}

        try:
            print(f"📤 Sending documents to N8N...")

            # Send both HTML documents to n8n with callback info
            payload = {
                'job_id': job_id,
                'callback_url': callback_url,
                'pre_brief': pre_brief_content,
                'sales_snapshot': sales_snapshot_content,
                'prospect_info': {
                    'company': prospect_data.get('Company_Name', ''),
                    'name': f"{prospect_data.get('First_Name', '')} {prospect_data.get('Last_Name', '')}".strip()
                }
            }

            # Send to n8n webhook - it will process async and callback
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10  # Short timeout - we don't wait for completion
            )

            if response.status_code in [200, 201]:
                print(f"✅ Documents sent to N8N, job_id: {job_id}")
                # N8N received the request, will process in background
                return {
                    'success': True,
                    'message': 'Document generation started',
                    'job_id': job_id
                }
            else:
                return {'error': f'Failed to start document generation: {response.text}'}

        except requests.exceptions.Timeout:
            # Timeout is OK - n8n is processing
            print(f"⏱️  N8N webhook timeout (normal - processing in background)")
            return {
                'success': True,
                'message': 'Document generation started (async)',
                'job_id': job_id
            }
        except Exception as e:
            return {'error': f'Document generation error: {str(e)}'}

    def create_google_sheet(self, sheet_name: str) -> Optional[Dict]:
        """Create Google Sheet using n8n webhook"""
        if not self.sheet_webhook:
            return None

        try:
            # Send request to n8n webhook to create sheet
            response = requests.post(
                self.sheet_webhook,
                json={'sheet_name': sheet_name},
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                # n8n returns array with json object
                if isinstance(result, list) and len(result) > 0:
                    sheet_data = result[0].get('json', {})
                    # Extract sheet URL or ID from response
                    return {
                        'success': True,
                        'sheet_data': sheet_data,
                        'spreadsheet_url': sheet_data.get('spreadsheet_url', '')
                    }
                return {'success': True, 'data': result}
            else:
                return {'error': f'Failed to create sheet: {response.text}'}

        except Exception as e:
            return {'error': f'Sheet creation error: {str(e)}'}

    def append_to_sheet_n8n(self, sheet_id: str, row_data: Dict) -> bool:
        """Append row to Google Sheet via n8n webhook"""
        if not self.sheet_webhook:
            return False

        try:
            # Send data to n8n webhook for sheet append
            payload = {
                'sheet_id': sheet_id,
                'row_data': row_data
            }

            response = requests.post(
                self.sheet_webhook,
                json=payload,
                timeout=30
            )

            return response.status_code == 200

        except Exception as e:
            print(f"Error appending to sheet: {e}")
            return False

    def process_prospect(self, prospect_data: Dict, job_id: str, callback_url: str,
                        is_test_mode: bool = False, spreadsheet_id: str = None) -> Dict:
        """
        Process a single prospect through the complete workflow:
        1. Extract website from email
        2. Scrape website with Apify
        3. Analyze with Manus AI
        4. Generate Pre-Brief with OpenAI
        5. Generate Sales Snapshot with OpenAI
        6. Send both documents to N8N
        7. N8N will callback with document URLs
        8. N8N will send email with document links
        """
        try:
            company_name = prospect_data.get('Company_Name', 'Unknown')
            first_name = prospect_data.get('First_Name', '')
            last_name = prospect_data.get('Last_Name', '')
            prospect_name = f"{first_name} {last_name}".strip()

            print(f"\n{'='*60}")
            print(f"🎯 Processing: {prospect_name} @ {company_name}")
            print(f"{'='*60}")

            # Step 1: Determine website URL
            website_url = prospect_data.get('Website', '')

            # If no website provided, extract domain from email
            if not website_url:
                email = prospect_data.get('Email', '')
                if email and '@' in email:
                    domain = email.split('@')[1]
                    # Skip common email providers
                    common_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']
                    if domain.lower() not in common_providers:
                        website_url = domain
                        print(f"📧 Extracted website from email: {website_url}")

                # Fallback to LinkedIn URL if still no website
                if not website_url:
                    website_url = prospect_data.get('LinkedIn_URL', '')
                    print(f"🔗 Using LinkedIn URL: {website_url}")

            if not website_url:
                return {
                    'success': False,
                    'error': 'No website URL could be determined',
                    'prospect': prospect_name
                }

            # Step 2: Scrape website with Apify
            scrape_result = self.scrape_website_apify(website_url)
            if not scrape_result.get('success'):
                return {
                    'success': False,
                    'error': scrape_result.get('error', 'Website scraping failed'),
                    'prospect': prospect_name
                }

            website_data = scrape_result.get('data', {})
            website_content = json.dumps(website_data, indent=2)

            # Step 3: Analyze with Manus AI
            manus_analysis = self.analyze_with_manus(website_url, company_name, website_data)

            # Step 4: Generate Pre-Brief with OpenAI
            pre_brief_html = self.generate_pre_brief_openai(
                url=website_url,
                first_name=first_name,
                last_name=last_name,
                website_content=website_content,
                manus_analysis=manus_analysis
            )

            # Step 5: Generate Sales Snapshot with OpenAI
            sales_snapshot_html = self.generate_sales_snapshot_openai(
                url=website_url,
                first_name=first_name,
                last_name=last_name,
                website_content=website_content,
                manus_analysis=manus_analysis
            )

            # Step 6: Send both documents to N8N for Google Doc creation
            doc_result = self.send_documents_to_n8n(
                pre_brief_html,
                sales_snapshot_html,
                prospect_data,
                job_id,
                callback_url,
                is_test_mode=is_test_mode
            )

            if not doc_result.get('success'):
                return {
                    'success': False,
                    'error': doc_result.get('error', 'Document creation failed'),
                    'prospect': prospect_name
                }

            # N8N will process in background and callback with document URLs
            # Then N8N will send email with the document links
            print(f"✅ Workflow initiated for {prospect_name}")
            print(f"⏳ Waiting for N8N callback with document URLs...")

            return {
                'success': True,
                'prospect': prospect_name,
                'company': company_name,
                'job_id': job_id,
                'status': 'processing',
                'message': 'Documents being created by N8N'
            }

        except Exception as e:
            print(f"❌ Error processing {prospect_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'prospect': prospect_data.get('First_Name', '') + ' ' + prospect_data.get('Last_Name', '')
            }

    def process_workflow(self, prospects: List[Dict], is_test_mode: bool = False) -> Dict:
        """Process complete workflow for single or multiple prospects"""
        try:
            # Step 1: Create Google Sheet using n8n webhook (optional)
            sheet_name = f"Dream 100 Prospects - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            if is_test_mode:
                sheet_name += " (TEST)"

            sheet_result = self.create_google_sheet(sheet_name)

            if not sheet_result or not sheet_result.get('success'):
                # If sheet creation fails, continue without it
                spreadsheet_id = None
                sheet_url = None
            else:
                spreadsheet_id = sheet_result.get('sheet_data', {}).get('spreadsheet_id', None)
                sheet_url = sheet_result.get('spreadsheet_url', '')

            # Step 2: Process each prospect
            # Note: In the single-entry workflow, we typically process one at a time
            # but this supports batch processing if needed
            results = []
            for prospect in prospects:
                # This is handled by app.py which generates job_id and callback_url
                # This method is called from app.py's background thread
                pass

            return {
                'success': True,
                'message': 'Workflow processing - handled by individual prospect processing'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate_results_csv(self, results: List[Dict]) -> str:
        """Generate CSV content from batch processing results"""
        try:
            output = io.StringIO()
            writer = csv.writer(output)

            # CSV Headers
            writer.writerow([
                'Company',
                'First Name',
                'Last Name',
                'Title',
                'Email',
                'Website',
                'Document 1',
                'Document 2'
            ])

            # Write each result row
            for result in results:
                writer.writerow([
                    result.get('company', 'N/A'),
                    result.get('first_name', 'N/A'),
                    result.get('last_name', 'N/A'),
                    result.get('title', 'N/A'),
                    result.get('email', 'N/A'),
                    result.get('website', 'N/A'),
                    result.get('document1_url', 'N/A'),
                    result.get('document2_url', 'N/A')
                ])

            return output.getvalue()

        except Exception as e:
            print(f"❌ Error generating CSV: {str(e)}")
            return ""

    def send_results_csv_email(self, csv_content: str, recipient_email: str, batch_id: str = None) -> Dict:
        """Send results CSV via Gmail SMTP with attachment"""
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders

        # Get SMTP configuration
        smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')

        if not smtp_user or not smtp_password:
            return {'success': False, 'error': 'SMTP credentials not configured'}

        try:
            print(f"📧 Sending results CSV to {recipient_email} via SMTP")

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dream100_results_{timestamp}.csv"

            # Create email message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient_email
            msg['Subject'] = f'Dream 100 Batch Processing Results - {datetime.now().strftime("%Y-%m-%d %H:%M")}'

            # Email body (HTML)
            body = f"""
            <html>
            <body>
                <h2>🎯 Dream 100 Batch Processing Complete</h2>

                <p>Your batch processing has finished successfully!</p>

                {f'<p><strong>Batch ID:</strong> {batch_id}</p>' if batch_id else ''}

                <p>The attached CSV file contains:</p>
                <ul>
                    <li>✅ Company information</li>
                    <li>✅ Contact details (Name, Title, Email)</li>
                    <li>✅ Website URLs</li>
                    <li>📄 <strong>Pre-Brief Document Links</strong></li>
                    <li>📊 <strong>Sales Snapshot Document Links</strong></li>
                </ul>

                <p><strong>File:</strong> {filename}</p>

                <p>You can now access all the generated documents through the provided links in the CSV file.</p>

                <hr>
                <p style="color: #666; font-size: 12px;">
                    Generated by Dream 100 Advantage - Prospect Intelligence System
                </p>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            # Attach CSV file
            csv_attachment = MIMEBase('text', 'csv')
            csv_attachment.set_payload(csv_content.encode('utf-8'))
            encoders.encode_base64(csv_attachment)
            csv_attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(csv_attachment)

            # Connect to SMTP server and send email
            print(f"🔌 Connecting to {smtp_host}:{smtp_port}...")
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()

            print(f"🔐 Logging in as {smtp_user}...")
            server.login(smtp_user, smtp_password)

            print(f"📤 Sending email...")
            text = msg.as_string()
            server.sendmail(smtp_user, recipient_email, text)
            server.quit()

            print(f"✅ Results CSV email sent successfully to {recipient_email}")
            return {'success': True, 'filename': filename}

        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP authentication failed. Check your Gmail app password."
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Email error: {str(e)}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
