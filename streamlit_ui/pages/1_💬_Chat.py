"""
Chat Page - Interactive chat với AI Coaching Bot powered by LangGraph.
"""
import streamlit as st
import sys
from pathlib import Path
import uuid

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.api_client import get_api_client
from utils.helpers import (
    init_session_state, apply_custom_css, display_backend_status,
    show_error, show_success, show_info
)

# Page config
st.set_page_config(
    page_title="Chat - AI Coaching Bot",
    page_icon="💬",
    layout="wide"
)

# Apply styling
apply_custom_css()

# Initialize
init_session_state()
api_client = get_api_client()

# Generate session ID if not exists
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ===== SIDEBAR =====
st.sidebar.title("💬 Chat Settings")
st.sidebar.markdown("---")

# Show current user
st.sidebar.info(f"**User:** {st.session_state.user_id}")

st.sidebar.markdown("---")
display_backend_status(api_client)

st.sidebar.markdown("---")

# Chat controls
if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.session_id = str(uuid.uuid4())
    show_success("Chat history đã được xóa!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Gợi ý câu hỏi:")
st.sidebar.markdown("""
- *"Tôi muốn học Python từ đầu"*
- *"Kỹ năng SQL của tôi thế nào?"*
- *"Tạo learning plan cho tôi"*
- *"Cách sử dụng JOIN trong SQL?"*
- *"Đánh giá tiến độ của tôi"*
""")

st.sidebar.markdown("---")
st.sidebar.caption("**Session ID:**")
st.sidebar.code(st.session_state.session_id[:8] + "...", language=None)

# ===== MAIN CONTENT =====
st.title("💬 Chat với AI Coach")
st.markdown("Hỏi bất kỳ điều gì về học tập, kỹ năng, khóa học và nhận phản hồi cá nhân hóa!")

st.markdown("---")

# Display chat history
chat_container = st.container()

with chat_container:
    if st.session_state.chat_history:
        for i, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                st.markdown(
                    f"""
                    <div class='chat-message user-message'>
                        <b>👤 Bạn:</b><br>
                        {msg['content']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class='chat-message bot-message'>
                        <b>🤖 AI Coach:</b><br>
                        {msg['content']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Show metadata if available
                if msg.get("metadata"):
                    with st.expander("📊 Chi tiết phản hồi"):
                        metadata = msg["metadata"]
                        
                        # Show mode
                        if metadata.get("mode"):
                            st.info(f"**Mode:** {metadata['mode']}")
                        
                        # Show citations
                        if metadata.get("citations"):
                            st.markdown("**📚 Trích dẫn:**")
                            for citation in metadata["citations"]:
                                st.caption(f"- {citation}")
                        
                        # Show plan if available
                        if metadata.get("plan"):
                            st.markdown("**📋 Learning Plan:**")
                            plan = metadata["plan"]
                            st.json(plan)
                        
                        # Show raw metadata
                        with st.expander("🔍 Raw Metadata"):
                            st.json(metadata)
                
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("👋 Chào bạn! Tôi là AI Coach. Hãy bắt đầu cuộc trò chuyện bằng cách nhập câu hỏi bên dưới.")

# Chat input at bottom
st.markdown("---")

# Create form for chat input
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Nhập câu hỏi của bạn:",
            placeholder="VD: Tôi muốn học Python từ đầu...",
            label_visibility="collapsed"
        )
    
    with col2:
        submit_button = st.form_submit_button("Gửi 📤", use_container_width=True)

# Process chat
if submit_button and user_input:
    if not user_input.strip():
        show_error("Vui lòng nhập câu hỏi!")
    else:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Show processing
        with st.spinner("🤔 AI Coach đang suy nghĩ..."):
            # Call API
            result = api_client.chat_execute(
                user_id=st.session_state.user_id,
                message=user_input,
                session_id=st.session_state.session_id
            )
        
        if result.get("success"):
            data = result.get("data", {})
            
            # Extract response
            answer = data.get("answer", "Xin lỗi, tôi không thể trả lời câu hỏi này.")
            mode = data.get("mode", "unknown")
            citations = data.get("citations", [])
            plan = data.get("plan")
            metadata_dict = data.get("metadata", {})
            
            # Add bot response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer,
                "metadata": {
                    "mode": mode,
                    "citations": citations,
                    "plan": plan,
                    **metadata_dict
                }
            })
            
            # Show success notification
            show_success("Đã nhận phản hồi từ AI Coach!")
        else:
            error_msg = result.get("error", "Unknown error")
            show_error(f"Lỗi: {error_msg}")
            
            # Add error message to chat
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"⚠️ Xin lỗi, đã xảy ra lỗi: {error_msg}"
            })
        
        # Rerun to update chat display
        st.rerun()

# ===== QUICK ACTIONS =====
st.markdown("---")
st.markdown("### 🚀 Thao Tác Nhanh")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👤 Xem Profile", use_container_width=True):
        st.switch_page("pages/2_👤_Profile.py")

with col2:
    if st.button("📚 Learning Plans", use_container_width=True):
        st.switch_page("pages/3_📚_Plans.py")

with col3:
    if st.button("📄 Documents", use_container_width=True):
        st.switch_page("pages/4_📄_Documents.py")

# ===== STATISTICS =====
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("### 📊 Thống Kê Chat")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_messages = len(st.session_state.chat_history)
        st.metric("Tổng tin nhắn", total_messages)
    
    with col2:
        user_messages = len([m for m in st.session_state.chat_history if m["role"] == "user"])
        st.metric("Câu hỏi", user_messages)
    
    with col3:
        bot_messages = len([m for m in st.session_state.chat_history if m["role"] == "assistant"])
        st.metric("Phản hồi", bot_messages)

# ===== EXPORT CHAT =====
if st.session_state.chat_history:
    st.markdown("---")
    
    if st.button("💾 Export Chat History", use_container_width=False):
        # Create export text
        export_text = f"# Chat History - {st.session_state.session_id}\n\n"
        export_text += f"User: {st.session_state.user_id}\n\n"
        export_text += "=" * 50 + "\n\n"
        
        for msg in st.session_state.chat_history:
            role = "User" if msg["role"] == "user" else "AI Coach"
            export_text += f"**{role}:**\n{msg['content']}\n\n"
            export_text += "-" * 50 + "\n\n"
        
        # Provide download button
        st.download_button(
            label="📥 Download Chat",
            data=export_text,
            file_name=f"chat_{st.session_state.session_id[:8]}.txt",
            mime="text/plain"
        )