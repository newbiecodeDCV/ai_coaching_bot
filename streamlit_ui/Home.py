"""
AI Coaching Bot - Streamlit UI Home Page.
"""
import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.api_client import get_api_client
from utils.helpers import (
    init_session_state, apply_custom_css, display_backend_status,
    render_metric_card, show_error, show_info, render_gap_card
)

# Page config
st.set_page_config(
    page_title="AI Coaching Bot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# Initialize
init_session_state()
api_client = get_api_client()

# ===== SIDEBAR =====
st.sidebar.title("🎓 AI Coaching Bot")
st.sidebar.markdown("---")

# User selection
user_options = {
    "user_001": "Nguyễn Văn An (Data Analyst)",
    "user_002": "Trần Thị Bình (Junior Developer)",
    "user_003": "Lê Văn Cường (Business Analyst)"
}

selected_user = st.sidebar.selectbox(
    "Chọn User",
    options=list(user_options.keys()),
    format_func=lambda x: user_options[x],
    index=0
)

st.session_state.user_id = selected_user

st.sidebar.markdown("---")
display_backend_status(api_client)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Navigation:**
    - 🏠 Home: Dashboard overview
    - 💬 Chat: Talk with AI Coach
    - 👤 Profile: View skills & progress
    - 📚 Plans: Learning plans
    - 📄 Documents: Knowledge base
    """
)

# ===== MAIN CONTENT =====
st.title("🏠 Dashboard - Tổng Quan")
st.markdown("Chào mừng đến với AI Coaching Bot! Hệ thống hỗ trợ học tập cá nhân hóa với AI.")

# Load user data
with st.spinner("Đang tải dữ liệu..."):
    result = api_client.get_user_overview(st.session_state.user_id)

if not result.get("success"):
    show_error(f"Không thể tải dữ liệu: {result.get('error')}")
    st.stop()

data = result.get("data", {})
profile = data.get("profile", {})
stats = data.get("stats", {})
assessments = data.get("assessments", [])
gaps = data.get("gaps", [])
enrollments = data.get("enrollments", [])

# ===== USER INFO =====
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"### {profile.get('name', 'Unknown')}")
    st.caption(f"**Role:** {profile.get('role', 'N/A')}")
    st.caption(f"**Level:** {profile.get('level', 'N/A')}")

with col2:
    st.metric("⏰ Thời gian/tuần", f"{profile.get('time_budget_per_week', 0)}h")

with col3:
    st.metric("📧 Email", profile.get('email', 'N/A'))

with col4:
    if profile.get('created_at'):
        from utils.helpers import format_datetime
        st.caption(f"**Joined:** {format_datetime(profile['created_at'])}")

# ===== KEY METRICS =====
st.markdown("---")
st.markdown("## 📊 Chỉ Số Chính")

col1, col2, col3, col4 = st.columns(4)

with col1:
    render_metric_card(
        "Total Assessments",
        stats.get("total_assessments", 0),
        icon="📝"
    )

with col2:
    render_metric_card(
        "Average Score",
        f"{stats.get('average_score', 0):.1f}/100",
        icon="⭐"
    )

with col3:
    render_metric_card(
        "Active Courses",
        stats.get("active_courses", 0),
        icon="📚"
    )

with col4:
    render_metric_card(
        "Study Hours",
        f"{stats.get('total_study_hours', 0):.1f}h",
        icon="⏱️"
    )

# ===== SKILL GAPS =====
st.markdown("---")
st.markdown("## ⚠️ Skill Gaps Cần Cải Thiện")

if gaps:
    st.info(f"Bạn có **{len(gaps)} skill gaps** cần được khắc phục để đạt mục tiêu.")
    
    # Show top 5 gaps
    for gap in gaps[:5]:
        render_gap_card(gap)
    
    if len(gaps) > 5:
        with st.expander(f"Xem thêm {len(gaps) - 5} gaps khác"):
            for gap in gaps[5:]:
                render_gap_card(gap)
else:
    st.success("🎉 Tuyệt vời! Bạn không có skill gaps. Hãy tiếp tục duy trì!")

# ===== RECENT ASSESSMENTS =====
st.markdown("---")
st.markdown("## 📝 Assessments Gần Đây")

if assessments:
    # Show latest 5 assessments
    for assessment in assessments[:5]:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"**{assessment.get('skill_name', 'Unknown')}**")
        
        with col2:
            level = assessment.get('level', 0)
            stars = "⭐" * level
            st.markdown(f"Level: {stars}")
        
        with col3:
            st.caption(f"Score: {assessment.get('score', 0)}/100")
    
    if len(assessments) > 5:
        st.caption(f"... và {len(assessments) - 5} assessments khác")
else:
    show_info("Chưa có assessment nào. Hãy bắt đầu đánh giá kỹ năng!")

# ===== ACTIVE ENROLLMENTS =====
st.markdown("---")
st.markdown("## 📚 Khóa Học Đang Tham Gia")

active_enrollments = [e for e in enrollments if e.get("status") == "in_progress"]

if active_enrollments:
    for enrollment in active_enrollments[:3]:
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                st.markdown(f"**{enrollment.get('course_title', 'Unknown')}**")
                st.caption(f"Provider: {enrollment.get('course_provider', 'N/A')}")
            
            with col2:
                progress = enrollment.get('progress_percent', 0)
                st.progress(progress / 100)
                st.caption(f"{progress}%")
            
            with col3:
                st.caption(f"{enrollment.get('duration_hours', 0)}h")
            
            st.markdown("---")
    
    if len(active_enrollments) > 3:
        st.caption(f"... và {len(active_enrollments) - 3} khóa học khác")
else:
    show_info("Chưa có khóa học nào đang tham gia. Chat với AI để nhận gợi ý!")

# ===== QUICK ACTIONS =====
st.markdown("---")
st.markdown("## 🚀 Thao Tác Nhanh")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💬 Chat với AI Coach", use_container_width=True):
        st.switch_page("pages/1_💬_Chat.py")

with col2:
    if st.button("👤 Xem Profile Chi Tiết", use_container_width=True):
        st.switch_page("pages/2_👤_Profile.py")

with col3:
    if st.button("📚 Quản Lý Learning Plans", use_container_width=True):
        st.switch_page("pages/3_📚_Plans.py")

# ===== FOOTER =====
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>AI Coaching Bot v1.0 | Powered by LangGraph + OpenAI + RAG</p>
        <p><small>Built with ❤️ using Streamlit + FastAPI</small></p>
    </div>
    """,
    unsafe_allow_html=True
)