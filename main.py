import streamlit as st
import os
from llm_handler import LLMHandler
from dotenv import load_dotenv
import tempfile

load_dotenv()

def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def main():
    # Page config
    st.set_page_config(
        page_title="Universal Data Analyst AI",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .top-info-bar {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin-bottom: 1rem;
    }
    .data-summary {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .conversation-area {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        min-height: 500px;
        max-height: 600px;
        overflow-y: auto;
    }
    .stButton > button {
        width: 100%;
        margin-top: 1rem;
        background-color: #dc3545;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #c82333;
    }
    .sidebar-section {
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e9ecef;
    }
    .example-questions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    .example-question {
        background-color: #e3f2fd;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        color: #1976d2;
        border: 1px solid #bbdefb;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'file_path' not in st.session_state:
        st.session_state.file_path = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Universal Data Analyst AI</h1>
        <p>Upload your data and start asking intelligent questions</p>
    </div>
    """, unsafe_allow_html=True)


    # Create columns for top info
    info_col1, info_col2 = st.columns([1, 1])
    
    with info_col1:
        if st.session_state.analyzer:
            st.markdown("**📋 Current Data Structure:**")
            for sheet_name, sheet in st.session_state.analyzer.analyzer.sheets.items():
                st.markdown(f"• **{sheet_name}**: {len(sheet.data)} rows, {len(sheet.data.columns)} columns")
                # Show first few column names
                cols_preview = list(sheet.data.columns)[:5]
                if len(sheet.data.columns) > 5:
                    cols_preview.append(f"... (+{len(sheet.data.columns) - 5} more)")
                st.markdown(f"  Columns: {', '.join(f'`{col}`' for col in cols_preview)}")
        else:
            st.info("📤 Upload a file to see data structure")

    with info_col2:
        st.markdown("**💡 Example Questions:**")
        example_questions = [
            "What are the top 5 categories?",
            "Show me trends over time",
            "What's the correlation between variables?",
            "Create a summary of the data",
            "Find outliers in the dataset",
            "Calculate average by group"
        ]
        
        # Display example questions as tags
        questions_html = ""
        for q in example_questions:
            questions_html += f'<span class="example-question">{q}</span>'
        
        st.markdown(f'<div class="example-questions">{questions_html}</div>', unsafe_allow_html=True)

    # Sidebar for file upload, data summary, and controls
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown(" 📁 Data Upload")
        
        # File upload section
        
        st.markdown("**Drop your file here**")
        uploaded_file = st.file_uploader(
            "Choose a file", 
            type=["csv", "xlsx", "xls"],
            help="Upload CSV or Excel files"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Process uploaded file
        if uploaded_file and st.session_state.file_path != uploaded_file.name:
            with st.spinner("Processing file..."):
                file_path = save_uploaded_file(uploaded_file)
                if file_path:
                    st.session_state.file_path = uploaded_file.name
                    try:
                        st.session_state.analyzer = LLMHandler(file_path)
                        st.success("✅ File loaded!")
                        st.session_state.conversation = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")


                    # Data types summary
                    if hasattr(sheet.data, 'dtypes'):
                        numeric_cols = len([col for col in sheet.data.columns if sheet.data[col].dtype in ['int64', 'float64']])
                        text_cols = len(sheet.data.columns) - numeric_cols
                        
                        st.markdown("**Data Types:**")
                        st.markdown(f"• Numeric: {numeric_cols}")
                        st.markdown(f"• Text: {text_cols}")
                    
                    # Quick preview
                    if st.button(f"Preview {sheet_name}", key=f"preview_{sheet_name}"):
                        st.dataframe(sheet.data.head(3))
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Controls section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Controls")
        
        # Status indicator
        if st.session_state.analyzer:
            st.success("🟢 AI Ready")
        else:
            st.warning("🟡 Upload data to begin")
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation"):
            if 'analyzer' in st.session_state and st.session_state.analyzer:
                st.session_state.analyzer.clear_history()
            st.session_state.conversation = []
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Conversation history in sidebar
        if st.session_state.conversation:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("### 📜 Conversation History")
            
            # Show recent conversations (last 5)
            recent_conversations = st.session_state.conversation[-10:]
            for i, message in enumerate(recent_conversations):
                if message["role"] == "user":
                    st.markdown(f"**Q{len(recent_conversations)-i}:** {message['content'][:50]}...")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Main area - Conversation
    st.markdown("💬 AI Analysis & Conversation")
    
    
    
    if st.session_state.conversation:
        for message in st.session_state.conversation:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    else:
        # Welcome message
        if st.session_state.analyzer:
            st.info("👋 Your data is ready! Ask me anything about it using the input below.")
        else:
            st.info("📤 Please upload a file in the sidebar to start analyzing your data.")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Question input at the bottom
    if st.session_state.analyzer and not st.session_state.processing:
        question = st.chat_input("Ask a question about your data...", key="main_chat_input")
        
        if question:
            st.session_state.processing = True
            st.session_state.conversation.append({"role": "user", "content": question})
            st.rerun()

    # Process question
    if st.session_state.processing and st.session_state.analyzer:
        # Get the last question
        last_question = next((msg["content"] for msg in reversed(st.session_state.conversation) if msg["role"] == "user"), None)
        
        if last_question:
            with st.spinner("🤔 Analyzing your data..."):
                try:
                    answer = st.session_state.analyzer.get_answer(last_question)
                    st.session_state.conversation.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.session_state.conversation.append({"role": "assistant", "content": f"❌ Error: {str(e)}"})
                finally:
                    st.session_state.processing = False
                    st.rerun()

if __name__ == "__main__":
    main()