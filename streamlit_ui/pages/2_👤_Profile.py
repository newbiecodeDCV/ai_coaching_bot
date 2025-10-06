"""
Profile Page - User profile, skills management và assessments.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.api_client import get_api_client
from utils.helpers import (
    init_session_state, apply_custom_css, display_backend_status,
    show_error, show_success, render_metric_card, render_gap_card,
    get_level_color, format_datetime
)

st.set_page_config(page_title="Profile - AI Coaching Bot", page_icon="👤", layout="wide")
apply_custom_css()
init_session_state()
api_client = get_api_client()

# Sidebar
st.sidebar.title("👤 Profile Settings")
st.sidebar.markdown("---")
st.sidebar.info(f"**User:** {st.session_state.user_id}")
st.sidebar.markdown("---")
display_backend_status(api_client)

# Main content
st.title("👤 User Profile & Skills")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🎯 Skills & Assessments", "📈 Performance"])

# TAB 1: Overview
with tab1:
    with st.spinner("Loading profile..."):
        result = api_client.get_user_overview(st.session_state.user_id)
    
    if not result.get("success"):
        show_error(f"Cannot load profile: {result.get('error')}")
    else:
        data = result.get("data", {})
        profile = data.get("profile", {})
        stats = data.get("stats", {})
        gaps = data.get("gaps", [])
        
        # Profile info
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https://via.placeholder.com/150", width=150)
        with col2:
            st.markdown(f"### {profile.get('name', 'Unknown')}")
            st.markdown(f"**Email:** {profile.get('email', 'N/A')}")
            st.markdown(f"**Role:** {profile.get('role', 'N/A')}")
            st.markdown(f"**Level:** {profile.get('level', 'N/A')}")
            st.markdown(f"**Time Budget:** {profile.get('time_budget_per_week', 0)}h/week")
        
        st.markdown("---")
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("Assessments", stats.get("total_assessments", 0), icon="📝")
        with col2:
            render_metric_card("Avg Score", f"{stats.get('average_score', 0):.1f}", icon="⭐")
        with col3:
            render_metric_card("Active Courses", stats.get("active_courses", 0), icon="📚")
        with col4:
            render_metric_card("Study Hours", f"{stats.get('total_study_hours', 0):.1f}h", icon="⏱️")
        
        st.markdown("---")
        st.markdown("### ⚠️ Skill Gaps")
        if gaps:
            for gap in gaps:
                render_gap_card(gap)
        else:
            st.success("No skill gaps!")

# TAB 2: Skills & Assessments
with tab2:
    st.markdown("### 🎯 Your Skills")
    
    # Load user skills
    result = api_client.get_user_skills(st.session_state.user_id)
    
    if result.get("success"):
        skills = result.get("data", [])
        
        # Category filter
        categories = list(set([s.get("skill_category") for s in skills if s.get("skill_category")]))
        selected_cat = st.selectbox("Filter by Category", ["All"] + categories)
        
        filtered_skills = skills if selected_cat == "All" else [s for s in skills if s.get("skill_category") == selected_cat]
        
        st.markdown("---")
        
        for skill in filtered_skills:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{skill.get('skill_name', 'Unknown')}**")
                    st.caption(skill.get('skill_description', '')[:100])
                
                with col2:
                    level = skill.get('current_level')
                    if level:
                        color = get_level_color(level)
                        st.markdown(f"<span style='color: {color}; font-size: 20px;'>{'⭐' * level}</span>", unsafe_allow_html=True)
                        st.caption(f"Level {level}")
                    else:
                        st.caption("Not assessed")
                
                with col3:
                    score = skill.get('current_score')
                    if score:
                        st.metric("Score", f"{score}/100")
                    else:
                        if st.button("Assess", key=f"assess_{skill.get('skill_id')}"):
                            st.session_state.assess_skill_id = skill.get('skill_id')
                
                st.markdown("---")
        
        # Assessment modal
        if hasattr(st.session_state, 'assess_skill_id'):
            st.markdown("### 📝 Create Assessment")
            skill_id = st.session_state.assess_skill_id
            
            score_input = st.slider("Score (0-100)", 0, 100, 50)
            
            if st.button("Submit Assessment"):
                result = api_client.create_assessment(skill_id, st.session_state.user_id, score_input)
                if result.get("success"):
                    show_success("Assessment created successfully!")
                    del st.session_state.assess_skill_id
                    st.rerun()
                else:
                    show_error(f"Failed: {result.get('error')}")
    else:
        show_error(f"Cannot load skills: {result.get('error')}")

# TAB 3: Performance
with tab3:
    st.markdown("### 📈 Performance Analysis")
    
    result = api_client.get_user_assessments(st.session_state.user_id, recent_days=90)
    
    if result.get("success"):
        assessments = result.get("data", [])
        
        if assessments:
            # Chart data
            import pandas as pd
            df = pd.DataFrame(assessments)
            
            st.line_chart(df.set_index('skill_name')['score'])
            
            st.markdown("---")
            st.markdown("### Recent Assessments")
            st.dataframe(df[['skill_name', 'score', 'level', 'taken_at']], use_container_width=True)
        else:
            st.info("No assessments found")
    else:
        show_error(f"Cannot load assessments: {result.get('error')}")

# Quick actions
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Chat with AI", use_container_width=True):
        st.switch_page("pages/1_💬_Chat.py")
with col2:
    if st.button("📚 View Plans", use_container_width=True):
        st.switch_page("pages/3_📚_Plans.py")