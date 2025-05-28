import streamlit as st
import requests
import json
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import formatResult, chatBubble, backendActivity
from config import Config

st.set_page_config(page_title="InferaRead - RAG PDF Query System",page_icon="",layout="wide",initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .success-card {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    
    .error-card {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
    
    .info-card {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
    }
    
    .warning-card {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.8rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: right;
    }
    
    .bot-message {
        background-color: #e9ecef;
        color: #495057;
        padding: 0.8rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 0.5rem;
    }
    
    .upload-section {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        border-top: 1px solid #e0e0e0;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'document_uploaded' not in st.session_state:
    st.session_state.document_uploaded = False
if 'current_document' not in st.session_state:
    st.session_state.current_document = None
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0
if 'upload_stats' not in st.session_state:
    st.session_state.upload_stats = {}

def main():
    st.markdown("""
    <div class="main-header">
        <h1>INFERAREAD</h1>
        <h3>Advanced RAG PDF Query System</h3>
        <p>Powered by Groq API & LLaMA3/ Gemma-7b-It </p>
    </div>""", unsafe_allow_html=True)
    with st.sidebar:
        st.header("System Control")
        if st.button("Check Backend Status", use_container_width=True):
            with st.spinner("Checking backend..."):
                health_status = backendActivity()
                if health_status['status'] == 'healthy':
                    st.success("Backend is succesfully running! Just waiting for your queries!")
                else:
                    st.error("Backend is not responding!")
        
        st.divider()
        
        st.header("System Info")
        try:
            response = requests.get(f"{Config.BACKEND_URL}/api/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                st.info(f"**Model:** {status_data.get('model', 'Unknown')}")
                st.info(f"**Embedding:** {status_data.get('embedding_model', 'Unknown').split('/')[-1]}")
                if status_data.get('document_loaded'):
                    st.success(f"**Document:** {status_data.get('current_document', 'Unknown')}")
                else:
                    st.warning("**No document loaded**")
            else:
                st.error("Unable to fetch system status")
        except:
            st.error("Backend connection failed")
        st.divider()
        
        st.header("Model Session Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Queries", st.session_state.query_count)
        with col2:
            st.metric("Documents", 1 if st.session_state.document_uploaded else 0)
        if st.button("Delete Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.query_count = 0
            st.rerun()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Upload Docx & Query", "Chat History", "Analytics", "More About InferaRead"])
    
    with tab1:
        st.header("Document Upload")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Choose a PDF file",type=['pdf'],help="Upload a PDF document to query against")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if uploaded_file is not None:
                if st.button("Upload & Process the chunks", use_container_width=True, type="primary"):
                    uploadDocx(uploaded_file)
        
        with col2:
            st.markdown("### Upload Guidelines")
            st.markdown("""
            - **Format:** PDF files only
            - **Size:** Up to 200MB
            - **Content:** Text-based PDFs work best
            - **Language:** English preferred
            """)
        
        st.divider()
        st.header("Query Interface")
        
        if st.session_state.document_uploaded:
            st.markdown("### Some samples queries you can try (Note: They might be out of context):")
            col1, col2, col3 = st.columns(3)
            sample_queries = ["What are the features?","Summarize the key points","What are the applications?"]
            for i, (col, query) in enumerate(zip([col1, col2, col3], sample_queries)):
                with col:
                    if st.button(f"{query[:20]}...", key=f"sample_{i}", use_container_width=True):
                        process_query(query)
            st.divider()
            
            with st.form("query_form"):
                user_query = st.text_area("Enter your question:",placeholder="Ask anything about the uploaded document...",height=100)
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    submit_button = st.form_submit_button("Ask Question", use_container_width=True, type="primary")
                with col2:
                    complexity = st.selectbox("Complexity", ["Simple", "Detailed"], key="complexity")
                with col3:
                    sources = st.selectbox("Max Sources", [3, 5, 10], index=1, key="max_sources")
                
                if submit_button and user_query.strip():
                    process_query(user_query, complexity, sources)
        else:
            st.warning("Please upload a PDF document first to start querying.")
            st.info("Use the upload section above to get started!")
    
    with tab2:
        st.header("Chat History")
        if st.session_state.chat_history:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for i, chat in enumerate(st.session_state.chat_history):
                st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong> {chat['query']}
                    <br><small>{chat['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="bot-message">
                    <strong>InferaRead:</strong> {chat['response']}
                    <br><small>Sources: {chat.get('sources', 'N/A')} | Document: {chat.get('document', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("Export Chat History", use_container_width=True):
                exportChats()
        else:
            st.info("No chat history yet. Start asking questions to see them here!")
    
    with tab3:
        st.header("Analytics Dashboard")
        
        if st.session_state.chat_history:
            queries = [chat['query'] for chat in st.session_state.chat_history]
            query_lengths = [len(query.split()) for query in queries]
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.histogram(x=query_lengths,title="Query Length Distribution",labels={'x': 'Words in Query', 'y': 'Frequency'},color_discrete_sequence=['#667eea'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                response_times = [len(chat['response']) / 100 for chat in st.session_state.chat_history]
                fig = px.line(
                    x=list(range(1, len(response_times) + 1)),
                    y=response_times,
                    title="Response Complexity Over Time",
                    labels={'x': 'Query Number', 'y': 'Response Complexity Score'}
                )
                st.plotly_chart(fig, use_container_width=True)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{len(st.session_state.chat_history)}</h3>
                    <p>Total Queries</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_query_length = sum(query_lengths) / len(query_lengths) if query_lengths else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{avg_query_length:.1f}</h3>
                    <p>Avg Query Length</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                response_lengths = [len(chat['response'].split()) for chat in st.session_state.chat_history]
                avg_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{avg_response_length:.1f}</h3>
                    <p>Avg Response Length</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                success_rate = 100
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{success_rate}%</h3>
                    <p>Success Rate</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Analytics will appear here after you start querying documents.")
    
    with tab4:
        st.header("About InferaRead")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### What is InferaRead?
            InferaRead is an advanced **Retrieval-Augmented Generation (RAG)** system that allows you to:
            
            - **Upload PDF documents** and extract meaningful insights
            - **Query your documents** using natural language
            - **Get AI-powered answers** based on document content
            - **Lightning-fast responses** powered by Groq API
            
            ### Technology Stack
            
            - **Backend:** FastAPI + Python
            - **AI Model:** LLaMA 3 (8B parameters)
            - **Embeddings:** Sentence Transformers
            - **Vector Store:** FAISS
            - **API:** Groq (Ultra-fast inference)
            - **Frontend:** Streamlit
            
            ### Key Features
            
            - **Accurate Responses:** AI answers are grounded in your document content
            - **Fast Processing:** Optimized for speed and efficiency
            - **User-Friendly:** Intuitive interface for easy interaction
            - **Scalable:** Built with modern, scalable technologies
            """)
        
        with col2:
            st.markdown("""
            ### Contact Me?
                        
            If you're interested in contributing to InferaRead or have ideas for improvements, feel free to reach out!
            - **GitHub:** [InferaRead Repository](https://github.com/akshatrajsaxena/Inferaread-LLMBot)
            - **Email:** [Akshat Raj Saxena](mailto:rakshat2003@gmail.com)
            - **LinkedIn:** [@akshatrajsaxena](https://www.linkedin.com/in/akshat-raj-saxena-849423258/)
            - **Twitter:** [@InferaRead](https://x.com/akshatakshatraj)
            """)
    
    st.markdown("""
    <div class="footer">
        <p> InferaRead - Advanced RAG PDF Query System | Powered by AI & Built with </p>
        <p>© 2025 Akshat Raj Saxena. Licensed under the MIT License.</p>
    </div>
    """, unsafe_allow_html=True)

def uploadDocx(uploaded_file):
    try:
        with st.spinner("Uploading and processing the relevant Chunks..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            for i in range(0, 101, 20):
                progress_bar.progress(i)
                if i == 0:
                    status_text.text("Uploading file...")
                elif i == 20:
                    status_text.text("Extracting text...")
                elif i == 40:
                    status_text.text("Creating embeddings...")
                elif i == 60:
                    status_text.text("Building vector store...")
                elif i == 80:
                    status_text.text("Finalizing...")
                time.sleep(0.5)
            
            response = requests.post(f"{Config.BACKEND_URL}/api/upload", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'success':
                    st.session_state.document_uploaded = True
                    st.session_state.current_document = uploaded_file.name
                    st.session_state.upload_stats = {
                        'chunks': result.get('chunks_created', 0),
                        'text_length': result.get('text_length', 0),
                        'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    progress_bar.progress(100)
                    status_text.text("Processing complete!")
                    
                    st.success(f"""**Document processed successfully!**
                    - **File:** {uploaded_file.name}
                    - **Chunks Created:** {result.get('chunks_created', 0)}
                    - **Text Length:** {result.get('text_length', 0):,} characters
                    You can now start asking questions about your document!""")
                else:
                    st.error(f"Upload failed: {result.get('message', 'Unknown error')}")
            else:
                st.error(f"Server error: {response.status_code}")
                
    except requests.exceptions.Timeout:
        st.error("Upload timeout. Please try again with a smaller file.")
    except Exception as e:
        st.error(f"Upload error: {str(e)}")

def process_query(query, complexity="Simple", max_sources=5):
    try:
        with st.spinner("Thinking..."):
            data = {"question": query}
            response = requests.post(f"{Config.BACKEND_URL}/api/query", data=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'success':
                    chat_entry = {
                        'query': query,
                        'response': result['answer'],
                        'sources': result.get('sources', 0),
                        'document': result.get('document', 'Unknown'),
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    }
                    st.session_state.chat_history.append(chat_entry)
                    st.session_state.query_count += 1
                    st.success("**Query processed successfully!**")
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown("### Response:")
                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 10px; border-left: 4px solid #007bff;">
                            {result['answer']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("### Details:")
                        st.info(f"**Sources Used:** {result.get('sources', 0)}")
                        st.info(f"**Document:** {result.get('document', 'Unknown')}")
                        st.info(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")
                else:
                    st.error(f"Query failed: {result.get('message', 'Unknown error')}")
            else:
                st.error(f"Server error: {response.status_code}")
                
    except requests.exceptions.Timeout:
        st.error("Query timeout. Please try again.")
    except Exception as e:
        st.error(f"Query error: {str(e)}")

def exportChats():
    try:
        chat_data = {'session_info': {'document': st.session_state.current_document,'total_queries': len(st.session_state.chat_history),'export_time': datetime.now().isoformat()},'chat_history': st.session_state.chat_history}
        
        json_str = json.dumps(chat_data, indent=2)
        st.download_button(label="Download Chat History",data=json_str,file_name=f"inferaread_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",mime="application/json",use_container_width=True)
        st.success("Chat history ready for download!")
    except Exception as e:
        st.error(f"Export error: {str(e)}")

if __name__ == "__main__":
    main()