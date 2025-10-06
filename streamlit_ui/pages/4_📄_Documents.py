"""
Documents Page - Document library with upload và search.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.api_client import get_api_client
from utils.helpers import (
    init_session_state, apply_custom_css, display_backend_status,
    show_error, show_success, show_info, format_datetime
)

st.set_page_config(page_title="Documents - AI Coaching Bot", page_icon="📄", layout="wide")
apply_custom_css()
init_session_state()
api_client = get_api_client()

# Sidebar
st.sidebar.title("📄 Documents Library")
st.sidebar.markdown("---")
st.sidebar.info(f"**User:** {st.session_state.user_id}")
st.sidebar.markdown("---")
display_backend_status(api_client)

# Main
st.title("📄 Documents Library")

# Tabs
tab1, tab2, tab3 = st.tabs(["📚 Library", "🔍 Search", "📤 Upload"])

# TAB 1: Library
with tab1:
    st.markdown("### 📚 Document Library")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Search by title", placeholder="Enter search term...")
    with col2:
        doc_type_filter = st.selectbox("Filter by Type", ["All", "tutorial", "guide", "reference", "other"])
    
    # Load documents
    with st.spinner("Loading documents..."):
        result = api_client.list_documents(
            doc_type=None if doc_type_filter == "All" else doc_type_filter,
            search=search_term if search_term else None
        )
    
    if result.get("success"):
        documents = result.get("data", [])
        
        if documents:
            for doc in documents:
                with st.expander(f"📄 {doc.get('title', 'Untitled')}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Type:** {doc.get('doc_type', 'N/A')}")
                        st.markdown(f"**Description:** {doc.get('description', 'N/A')}")
                        st.caption(f"Created: {format_datetime(doc.get('created_at', ''))}")
                        st.caption(f"Size: {doc.get('file_size', 0) // 1024} KB")
                        
                        # Tags
                        tags = doc.get('tags', [])
                        if tags:
                            st.markdown("**Tags:** " + ", ".join([f"`{tag}`" for tag in tags]))
                    
                    with col2:
                        indexed_status = "✅ Indexed" if doc.get('is_indexed') else "❌ Not Indexed"
                        st.info(indexed_status)
                        
                        # Actions
                        if not doc.get('is_indexed'):
                            if st.button("🔄 Reindex", key=f"reindex_{doc['id']}"):
                                result = api_client.reindex_document(doc['id'])
                                if result.get('success'):
                                    show_success("Document reindexed!")
                                    st.rerun()
                        
                        if st.button("🗑 Delete", key=f"del_{doc['id']}"):
                            result = api_client.delete_document(doc['id'])
                            if result.get('success'):
                                show_success("Document deleted!")
                                st.rerun()
                            else:
                                show_error(f"Failed: {result.get('error')}")
        else:
            show_info("No documents found")
    else:
        show_error(f"Cannot load documents: {result.get('error')}")

# TAB 2: Search
with tab2:
    st.markdown("### 🔍 Search Documents (Vector Search)")
    
    query = st.text_input("Enter your question", placeholder="VD: How to use SQL JOIN?")
    
    col1, col2 = st.columns(2)
    with col1:
        top_k = st.slider("Number of results", 1, 10, 5)
    with col2:
        score_threshold = st.slider("Score threshold", 0.0, 1.0, 0.3, 0.1)
    
    if st.button("🔍 Search", use_container_width=True):
        if not query:
            show_error("Please enter a query!")
        else:
            with st.spinner("Searching..."):
                result = api_client.search_documents(query, top_k, score_threshold)
            
            if result.get("success"):
                data = result.get("data", {})
                results = data.get("results", [])
                documents = data.get("documents", [])
                
                st.success(f"Found {len(results)} results")
                
                # Show results
                for i, res in enumerate(results):
                    with st.container():
                        st.markdown(f"**Result {i+1}** (Score: {res.get('score', 0):.3f})")
                        st.markdown(f"```\n{res.get('content', '')}\n```")
                        st.caption(f"Document ID: {res.get('document_id', 'N/A')}")
                        st.markdown("---")
                
                # Show related documents
                if documents:
                    st.markdown("### 📚 Related Documents")
                    for doc in documents:
                        st.markdown(f"- **{doc.get('title')}** ({doc.get('doc_type')})")
            else:
                show_error(f"Search failed: {result.get('error')}")

# TAB 3: Upload
with tab3:
    st.markdown("### 📤 Upload New Document")
    
    with st.form("upload_form"):
        title = st.text_input("Title*", placeholder="Document title")
        description = st.text_area("Description", placeholder="Brief description")
        doc_type = st.selectbox("Type*", ["tutorial", "guide", "reference", "other"])
        tags = st.text_input("Tags (comma-separated)", placeholder="python, sql, beginner")
        
        uploaded_file = st.file_uploader("Choose file", type=["pdf", "txt", "md", "docx"])
        
        submit = st.form_submit_button("📤 Upload")
        
        if submit:
            if not title or not uploaded_file:
                show_error("Title and file are required!")
            else:
                with st.spinner("Uploading and indexing..."):
                    result = api_client.upload_document(
                        file=uploaded_file,
                        title=title,
                        doc_type=doc_type,
                        description=description,
                        tags=tags
                    )
                
                if result.get("success"):
                    show_success("Document uploaded and indexed successfully!")
                    st.rerun()
                else:
                    show_error(f"Upload failed: {result.get('error')}")

# Quick actions
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Chat with AI", use_container_width=True):
        st.switch_page("pages/1_💬_Chat.py")
with col2:
    if st.button("👤 View Profile", use_container_width=True):
        st.switch_page("pages/2_👤_Profile.py")