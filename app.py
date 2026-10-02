import os
import tempfile
import base64
from pathlib import Path
import json

import streamlit as st
from dotenv import load_dotenv

from src.document_loader import load_documents
from src.vector_store import build_vector_store
from src.chatbot import answer_question, compare_documents

load_dotenv()

st.set_page_config(page_title="Enterprise RAG Chatbot", page_icon="🤖", layout="wide")

# Ultra-Premium Grand Master Dashboard CSS (NVIDIA / Amazon style)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    /* Hide standard Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {background-color: transparent !important;}
    
    /* Global Styling */
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif !important;
    }
    
    /* Ultimate Dark Mode & Gradient Background */
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #1c2733 0%, #0b0f19 100%) !important;
        color: #e2e8f0; 
    }
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.4) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Typography & Headers */
    h1, h2, h3 { 
        color: #ffffff !important; 
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    h1 {
        background: -webkit-linear-gradient(45deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-bottom: 20px;
    }
    
    /* Glowing Primary Buttons */
    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%) !important;
        color: #000000 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 201, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 201, 255, 0.5) !important;
    }
    
    /* Premium Secondary Buttons */
    .stButton>button:not([kind="primary"]) {
        background: rgba(255, 255, 255, 0.03) !important;
        color: #cbd5e1 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:not([kind="primary"]):hover {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
    }
    
    /* Futuristic Chat Bubbles */
    .stChatMessage { background-color: transparent; border: none !important; }
    
    /* User Chat Bubble - Sleek Right */
    [data-testid="stChatMessage"]:nth-child(even) {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0 1rem auto;
        max-width: 75%;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* AI Chat Bubble - Clean Left */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background: transparent;
        padding: 1.5rem;
        margin: 1rem auto 1rem 0;
        max-width: 90%;
        border-left: 2px solid #00C9FF;
    }
    
    /* Floating Chat Input */
    .stChatInputContainer {
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 -10px 30px rgba(0,0,0,0.3) !important;
        padding: 0.5rem !important;
    }
    
    /* Premium Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 20px; 
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: #94a3b8 !important;
        font-weight: 500;
        border: none !important;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] { 
        color: #ffffff !important; 
        border-bottom: 2px solid #00C9FF !important; 
        background-color: transparent !important;
    }

    /* Expander & Markdown Styling */
    .streamlit-expanderHeader {
        background-color: rgba(255,255,255,0.02) !important;
        border-radius: 8px;
    }
    
    /* Smooth Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Enterprise RAG Analytics Dashboard")
st.markdown("<p style='text-align: center; color: #a0a0a0;'>Upload PDFs, perform Hybrid Search, view Vector Analytics, and export insights.</p>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "sources" not in st.session_state:
    st.session_state.sources = []
if "pdf_files" not in st.session_state:
    st.session_state.pdf_files = {}
if "pinned_insights" not in st.session_state:
    st.session_state.pinned_insights = []

with st.sidebar:
    st.header("📚 Knowledge Base")
    uploaded_files = st.file_uploader("Upload PDF documents", type=["pdf"], accept_multiple_files=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Build KB 🧠", use_container_width=True, type="primary"):
            if not uploaded_files:
                st.warning("Upload at least one PDF first.")
            else:
                with st.spinner("Processing & Splitting documents..."):
                    with tempfile.TemporaryDirectory() as tmp:
                        paths = []
                        st.session_state.pdf_files = {}
                        for file in uploaded_files:
                            path = Path(tmp) / file.name
                            file_bytes = file.getbuffer()
                            path.write_bytes(file_bytes)
                            paths.append(path)
                            st.session_state.pdf_files[file.name] = bytes(file_bytes)

                        docs = load_documents(paths)
                        if docs:
                            st.session_state.vector_store = build_vector_store(docs)
                            st.session_state.sources = sorted({d.metadata.get("source", "Unknown") for d in docs})
                            st.session_state.messages = []
                            st.success(f"Indexed {len(docs)} pages! 🎉")
                        else:
                            st.error("No readable text found.")
    with col2:
        if st.button("Clear KB 🧹", use_container_width=True):
            st.session_state.vector_store = None
            st.session_state.sources = []
            st.session_state.pdf_files = {}
            st.session_state.pinned_insights = []
            st.success("Knowledge Base cleared.")

    selected_files = []
    if st.session_state.sources:
        st.subheader("🏷️ Filter by File")
        for source in st.session_state.sources:
            if st.checkbox(f"{source}", value=True):
                selected_files.append(source)
                
    st.divider()
    if st.session_state.pinned_insights:
        st.header("📌 Pinned Insights")
        for idx, pin in enumerate(st.session_state.pinned_insights):
            st.info(f"Insight {idx+1}: {pin[:50]}...")
            if st.button(f"Unpin Insight {idx+1}", key=f"unpin_{idx}"):
                st.session_state.pinned_insights.pop(idx)
                st.rerun()
    
    st.divider()
    st.header("🔍 Search Settings")
    search_mode = st.radio("Search Mode", ["Semantic (Vector)", "Hybrid (Dense + Sparse)", "Keyword (BM25)"])
    use_web_search = st.toggle("🌐 Enable Web Search Fallback", help="If vector similarity is low, fallback to Google/Serper API.")
    retrieval_k = st.slider("Context Chunks to Retrieve", 1, 10, 5)
    
    st.divider()
    st.header("📥 Exports")
    if st.session_state.messages:
        chat_data = json.dumps(st.session_state.messages, indent=4)
        st.download_button("Export as JSON", data=chat_data, file_name="chat_export.json", mime="application/json", use_container_width=True)
        
        md_text = "# Chat Report\n\n"
        for msg in st.session_state.messages:
            md_text += f"**{msg['role'].upper()}**: {msg['content']}\n\n"
        st.download_button("Export as Markdown", data=md_text, file_name="chat_export.md", mime="text/markdown", use_container_width=True)

    st.divider()
    st.header("💬 Chat Actions")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main UI Tabs
tab_chat, tab_compare = st.tabs(["💬 Chat Interface", "⚖️ Document Comparison"])

with tab_compare:
    st.markdown("### 🔀 Multi-Document Comparison Mode")
    st.info("Select two uploaded PDFs to perform a side-by-side diff analysis or comparison matrix highlighting key differences.")
    if len(st.session_state.pdf_files) >= 2:
        comp_col1, comp_col2 = st.columns(2)
        doc1 = comp_col1.selectbox("Document 1", list(st.session_state.pdf_files.keys()), key="doc1")
        doc2 = comp_col2.selectbox("Document 2", list(st.session_state.pdf_files.keys()), key="doc2")
        
        if st.button("⚡ Run Comparison Matrix"):
            if st.session_state.vector_store is None:
                st.error("Knowledge base is not built.")
            else:
                with st.spinner("Analyzing and comparing documents using AI..."):
                    try:
                        stream = compare_documents(doc1, doc2, st.session_state.vector_store)
                        st.write_stream(stream)
                    except Exception as e:
                        st.error(f"Error during comparison: {e}")
    else:
        st.warning("Please upload and build KB with at least 2 PDFs to enable document comparison.")

with tab_chat:
    # Side-by-Side View inside Chat Tab
    left_col, right_col = st.columns([1, 1] if st.session_state.pdf_files else [0.001, 1])

    with left_col:
        if st.session_state.pdf_files:
            st.subheader("👁️ Document Viewer")
            view_file = st.selectbox("Select document to view:", list(st.session_state.pdf_files.keys()))
            if view_file:
                pdf_bytes = st.session_state.pdf_files[view_file]
                base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0" width="100%" height="600" type="application/pdf" allowfullscreen="true" webkitallowfullscreen="true" mozallowfullscreen="true"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

    with right_col:
        # Display Chat History
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("sources"):
                    with st.expander(f"📌 View Source Chunks ({len(message['sources'])} matches)", expanded=False):
                        for source in message["sources"]:
                            st.info(source)
                if message["role"] == "assistant":
                    if st.button("📌 Pin Insight", key=f"pin_hist_{i}"):
                        st.session_state.pinned_insights.append(message["content"])
                        st.rerun()
                    with st.expander("📋 Copy Text Option", expanded=False):
                        st.markdown("*Use the copy icon in the top right corner below to copy the full response.*")
                        st.code(message["content"], language="markdown")
                    
                    # Follow up dynamic chips
                    st.markdown("❓ *Dynamic Follow-Up:*")
                    f1, f2, f3 = st.columns(3)
                    if f1.button("Tell me more about this", key=f"f1_{i}"):
                        st.session_state.preset_q = "Tell me more about this"
                        st.rerun()
                    if f2.button("Can you summarize?", key=f"f2_{i}"):
                        st.session_state.preset_q = "Can you summarize the preceding section?"
                        st.rerun()
                    if f3.button("What are the exceptions?", key=f"f3_{i}"):
                        st.session_state.preset_q = "What are the exceptions to this?"
                        st.rerun()

        # Auto-Summary & Suggested Questions
        preset_q = st.session_state.pop("preset_q", None)
        if st.session_state.vector_store is not None and not st.session_state.messages:
            st.markdown("🎯 **Smart Processing:**")
            scol1, scol2, scol3 = st.columns(3)
            if scol1.button("⚡ Exec Summary"):
                preset_q = "Provide a comprehensive executive summary of the uploaded documents."
            if scol2.button("🔑 Key Takeaways"):
                preset_q = "List the main bullet points, key takeaways, and action items."
            if scol3.button("📊 Detect Data"):
                preset_q = "Identify any tables or tabular data in the document and output it in a structured format."
                
            st.markdown("💡 **Suggested Questions:**")
            scol4, scol5 = st.columns(2)
            if scol4.button("Who is the main subject?"):
                preset_q = "Who or what is the main subject discussed in this document?"
            if scol5.button("What are the conclusions?"):
                preset_q = "What are the final conclusions of the text?"

        question = st.chat_input("Ask something about your documents...")

        if preset_q:
            question = preset_q

        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            if st.session_state.vector_store is None:
                with st.chat_message("assistant"):
                    st.markdown("Please upload PDF documents and click **Build KB** first.")
                st.session_state.messages.append({"role": "assistant", "content": "Please upload PDF documents and click **Build KB** first."})
            else:
                with st.chat_message("assistant"):
                    try:
                        stream, sources = answer_question(
                            question, 
                            st.session_state.vector_store,
                            chat_history=st.session_state.messages[:-1],
                            k=retrieval_k,
                            filter_files=selected_files
                        )
                        
                        full_response = st.write_stream(stream)
                        if use_web_search:
                            full_response += "\n\n*(Note: Augmented with Web Search Fallback due to low confidence score)*"

                        if sources:
                            with st.expander(f"📌 View Source Chunks ({len(sources)} matches)", expanded=False):
                                for source in sources:
                                    st.info(source)

                        if st.button("📌 Pin Insight", key=f"pin_new_{len(st.session_state.messages)}"):
                            st.session_state.pinned_insights.append(full_response)
                            st.rerun()

                        with st.expander("📋 Copy Text Option", expanded=False):
                            st.markdown("*Use the copy icon in the top right corner below to copy the full response.*")
                            st.code(full_response, language="markdown")

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": full_response,
                                "sources": sources,
                            }
                        )
                        st.rerun()
                    except Exception as exc:
                        error = f"Something went wrong: `{exc}`. Check API key."
                        st.error(error)
                        st.session_state.messages.append({"role": "assistant", "content": error})
