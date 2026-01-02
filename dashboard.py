import streamlit as st
import pandas as pd
import requests
import json
from typing import Dict, List

# Webhook URLs
WEBHOOK_TEST = "https://n8n.eventplanners.cloud/webhook-test/2af2ce4c-6c51-4935-9f0a-1a019d4bd466"
WEBHOOK_PROD = "https://n8n.eventplanners.cloud/webhook/2af2ce4c-6c51-4935-9f0a-1a019d4bd466"

def send_to_webhook(url: str, data: Dict) -> tuple[bool, str]:
    """
    Send JSON data to webhook URL.

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            return True, f"Success: {response.status_code}"
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.Timeout:
        return False, "Error: Request timed out"
    except requests.exceptions.RequestException as e:
        return False, f"Error: {str(e)}"

def process_csv_to_webhook(df: pd.DataFrame, webhook_url: str) -> Dict:
    """
    Process DataFrame and send all rows to webhook in a single request.

    Returns:
        Dict with result information
    """
    status_text = st.empty()
    status_text.text(f"Preparing {len(df)} rows for webhook...")

    # Convert entire DataFrame to list of dictionaries
    data_list = []
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        # Convert NaN to None for proper JSON serialization
        row_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
        data_list.append(row_dict)

    # Send all data in one request
    status_text.text(f"Sending {len(data_list)} items to webhook...")

    payload = {"items": data_list}
    success, message = send_to_webhook(webhook_url, payload)

    result = {
        "total_items": len(data_list),
        "success": success,
        "message": message,
        "data": payload
    }

    if success:
        status_text.text("✅ Successfully sent all data to webhook!")
    else:
        status_text.text("❌ Failed to send data to webhook")

    return result

def main():
    st.set_page_config(
        page_title="N8N Webhook Manager",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for clean white theme
    st.markdown("""
        <style>
        /* Main background */
        .stApp {
            background-color: #ffffff;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Title styling */
        h1 {
            color: #1f2937 !important;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.5rem !important;
            text-align: center;
        }

        /* Subtitle styling */
        .subtitle {
            text-align: center;
            color: #6b7280;
            font-size: 1rem;
            margin-bottom: 2rem;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-panel"] {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 1.5rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            border-bottom: 2px solid #e5e7eb;
        }

        .stTabs [data-baseweb="tab"] {
            color: #6b7280;
            font-weight: 500;
            padding: 0.75rem 1.5rem;
        }

        .stTabs [aria-selected="true"] {
            color: #2563eb;
            border-bottom: 2px solid #2563eb;
        }

        /* Input field styling */
        .stTextInput > div > div > input,
        .stTextArea textarea {
            background-color: #ffffff !important;
            border: 1px solid #d1d5db !important;
            border-radius: 6px !important;
            color: #1f2937 !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea textarea:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        }

        /* Button styling */
        .stButton > button {
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.6rem 1.5rem;
            font-weight: 500;
            transition: all 0.2s;
        }

        .stButton > button:hover {
            background-color: #1d4ed8;
        }

        /* Metric styling */
        [data-testid="stMetricValue"] {
            font-size: 1.875rem;
            color: #1f2937;
            font-weight: 600;
        }

        [data-testid="stMetricLabel"] {
            color: #6b7280;
            font-size: 0.875rem;
        }

        /* Dataframe styling */
        .stDataFrame {
            border: 1px solid #e5e7eb;
            border-radius: 6px;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #f9fafb;
            border-right: 1px solid #e5e7eb;
        }

        /* File uploader styling */
        [data-testid="stFileUploader"] {
            background-color: #f9fafb;
            border: 2px dashed #d1d5db;
            border-radius: 6px;
            padding: 2rem;
        }

        /* Success/Error message styling */
        .stSuccess {
            background-color: #f0fdf4;
            border: 1px solid #86efac;
            border-radius: 6px;
            color: #166534;
        }

        .stError {
            background-color: #fef2f2;
            border: 1px solid #fca5a5;
            border-radius: 6px;
            color: #991b1b;
        }

        .stInfo {
            background-color: #eff6ff;
            border: 1px solid #93c5fd;
            border-radius: 6px;
            color: #1e40af;
        }

        /* Number input styling */
        .stNumberInput > div > div > input {
            background-color: #ffffff !important;
            border: 1px solid #d1d5db !important;
            border-radius: 6px !important;
            color: #1f2937 !important;
        }

        /* Headers */
        h2, h3, h4 {
            color: #1f2937 !important;
            font-weight: 600 !important;
        }

        /* Code blocks */
        code {
            background-color: #f3f4f6 !important;
            color: #1f2937 !important;
            padding: 0.2rem 0.4rem !important;
            border-radius: 3px !important;
        }

        /* Labels */
        label {
            color: #374151 !important;
            font-weight: 500 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Hero section
    st.markdown("<h1>🚀 N8N Webhook Manager</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Seamlessly send your data to N8N workflows with style</p>", unsafe_allow_html=True)

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Mode selection
        mode = st.radio(
            "Select Mode",
            options=["Test", "Production"],
            help="Test mode uses webhook-test endpoint, Production uses the main webhook endpoint"
        )

        webhook_url = WEBHOOK_TEST if mode == "Test" else WEBHOOK_PROD

        st.info(f"**Selected URL:**\n`{webhook_url}`")

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This dashboard allows you to:
        - Input data manually
        - Upload CSV files
        - Convert each row to JSON
        - Send to N8N webhook endpoints
        - Track processing status
        """)

    # Initialize df as None
    df = None

    # Use tabs for input methods
    tab1, tab2 = st.tabs(["✍️ Manual Input", "📁 CSV Upload"])

    with tab1:
        st.markdown("### Enter Client Data")

        # Initialize session state for json_data if not exists
        if 'json_data' not in st.session_state:
            st.session_state['json_data'] = ""

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("Enter your JSON data below (one JSON object per row):")

            # Text area for manual JSON input - using session state
            json_input = st.text_area(
                "JSON Data",
                value=st.session_state['json_data'],
                height=300,
                placeholder='{"Name": "John Doe", "Email": "john@example.com", "Meeting brief": "Discuss project timeline"}\n{"Name": "Jane Smith", "Email": "jane@example.com", "Meeting brief": "Review budget proposal"}',
                help="Enter one JSON object per line. Each line will be sent as a separate webhook request.",
                key="json_input_area"
            )

            # Update session state when text area changes
            st.session_state['json_data'] = json_input

            # Form-based input - Always visible
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📋 Quick Add Form")

            with st.form("manual_entry_form"):
                # Ask how many entries to add
                num_entries = st.number_input("Number of entries to add", min_value=1, max_value=10, value=1)

                st.markdown("<br>", unsafe_allow_html=True)

                # Create fields for each entry
                entries = []
                for i in range(int(num_entries)):
                    if num_entries > 1:
                        st.markdown(f"**Entry {i+1}**")

                    col_a, col_b = st.columns(2)

                    with col_a:
                        name = st.text_input(f"Name", placeholder="John Doe", key=f"name_{i}", label_visibility="visible" if i == 0 else "collapsed")
                        email = st.text_input(f"Email", placeholder="john@example.com", key=f"email_{i}", label_visibility="visible" if i == 0 else "collapsed")

                    with col_b:
                        meeting_brief = st.text_area(f"Meeting brief", placeholder="Discuss project timeline", height=80, key=f"brief_{i}", label_visibility="visible" if i == 0 else "collapsed")

                    entries.append({
                        "Name": name,
                        "Email": email,
                        "Meeting brief": meeting_brief
                    })

                    if i < int(num_entries) - 1:
                        st.markdown("---")

                col_submit, col_space = st.columns([1, 3])
                with col_submit:
                    submitted = st.form_submit_button("➕ Add Entries", use_container_width=True)

                if submitted:
                    # Filter out empty entries (where name is not provided)
                    valid_entries = [e for e in entries if e["Name"]]

                    if valid_entries:
                        # Append all entries to JSON input
                        new_entries = "\n".join([json.dumps(e) for e in valid_entries])

                        if st.session_state['json_data']:
                            st.session_state['json_data'] = st.session_state['json_data'] + "\n" + new_entries
                        else:
                            st.session_state['json_data'] = new_entries

                        st.success(f"✅ Added {len(valid_entries)} entries!")
                        st.rerun()
                    else:
                        st.error("Please enter at least one name.")

        with col2:
            st.header("📊 Statistics")
            stats_placeholder = st.empty()

        # Process manual input
        if json_input:
            try:
                # Parse JSON input (one object per line)
                lines = [line.strip() for line in json_input.split('\n') if line.strip()]
                data_list = []

                for line in lines:
                    try:
                        data_list.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid JSON on line: {line[:50]}... - Error: {str(e)}")

                if data_list:
                    # Convert to DataFrame for processing
                    df = pd.DataFrame(data_list)

                    st.success(f"✅ Parsed {len(df)} entries successfully!")

                    # Display preview
                    st.subheader("📋 Data Preview")
                    st.dataframe(df, use_container_width=True)

                    # Sample JSON preview
                    with st.expander("🔍 Sample JSON Format"):
                        st.json(data_list[0])

            except Exception as e:
                st.error(f"Error parsing input: {str(e)}")

    with tab2:
        st.markdown("### Upload CSV File")

        # Add download template button
        col_template, col_space = st.columns([1, 3])
        with col_template:
            # Create sample CSV template
            template_data = pd.DataFrame({
                "Name": ["John Doe", "Jane Smith", "Bob Johnson"],
                "Email": ["john@example.com", "jane@example.com", "bob@example.com"],
                "Meeting brief": ["Initial consultation", "Follow-up meeting", "Project review"]
            })

            csv_template = template_data.to_csv(index=False)

            st.download_button(
                label="📥 Download CSV Template",
                data=csv_template,
                file_name="webhook_template.csv",
                mime="text/csv",
                use_container_width=True,
                help="Download a sample CSV file with the correct format"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Drop your CSV file here or click to browse",
            type=['csv'],
            help="CSV file should have columns: Name, Email, Meeting brief"
        )

        if uploaded_file is not None:
            try:
                # Read CSV
                df = pd.read_csv(uploaded_file)

                st.success(f"✅ File uploaded successfully! Found **{len(df)}** rows and **{len(df.columns)}** columns")

                # Create two columns for better layout
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Display preview
                    st.markdown("#### 📋 Data Preview")
                    st.dataframe(df.head(10), use_container_width=True)

                with col2:
                    # Show column info
                    st.markdown("#### ℹ️ Column Info")
                    st.metric("Total Columns", len(df.columns))
                    st.metric("Total Rows", len(df))

                    with st.expander("View Column Names"):
                        for col in df.columns:
                            st.code(col)

                # Sample JSON preview
                with st.expander("🔍 Sample JSON Format"):
                    if len(df) > 0:
                        sample_row = df.iloc[0].to_dict()
                        sample_row = {k: (None if pd.isna(v) else v) for k, v in sample_row.items()}
                        st.json(sample_row)

            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.exception(e)

    # Common processing section for both input methods
    if df is not None and len(df) > 0:
        # Process button
        st.markdown("<br>", unsafe_allow_html=True)

        col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 2])

        with col_btn1:
            process_button = st.button(
                "🚀 Send to Webhook",
                type="primary",
                use_container_width=True
            )

        with col_btn2:
            if st.button("🔄 Clear Results", use_container_width=True):
                if 'result' in st.session_state:
                    del st.session_state['result']
                st.rerun()

        # Process the data
        if process_button:
            with st.spinner("⚡ Sending data to webhook..."):
                result = process_csv_to_webhook(df, webhook_url)
                st.session_state['result'] = result

                if result['success']:
                    st.balloons()
                    st.success(f"✅ Successfully sent **{result['total_items']}** items to webhook!")
                else:
                    st.error(f"❌ Failed to send data: {result['message']}")

        # Display results if available
        if 'result' in st.session_state and st.session_state['result']:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📈 Processing Results")

            result = st.session_state['result']

            # Show summary metrics with enhanced styling
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("📦 Total Items", result['total_items'])
            with metric_col2:
                status_icon = "✅" if result['success'] else "❌"
                status_text = "Success" if result['success'] else "Failed"
                st.metric("🎯 Status", f"{status_icon} {status_text}")
            with metric_col3:
                st.metric("💬 Response", result['message'].split(':')[0] if ':' in result['message'] else result['message'])

            # Show the payload that was sent
            with st.expander("📤 View Complete Payload"):
                st.json(result['data'])

            # Show individual items in a nice table
            with st.expander(f"📋 View All {result['total_items']} Items"):
                items_df = pd.DataFrame(result['data']['items'])
                st.dataframe(items_df, use_container_width=True, height=400)

if __name__ == "__main__":
    main()
