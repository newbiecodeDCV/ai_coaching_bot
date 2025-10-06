"""
Plans Page - Learning plans management.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.api_client import get_api_client
from utils.helpers import (
    init_session_state, apply_custom_css, display_backend_status,
    show_error, show_success, show_info, render_status_badge, format_datetime
)

st.set_page_config(page_title="Plans - AI Coaching Bot", page_icon="📚", layout="wide")
apply_custom_css()
init_session_state()
api_client = get_api_client()

# Sidebar
st.sidebar.title("📚 Plans Management")
st.sidebar.markdown("---")
st.sidebar.info(f"**User:** {st.session_state.user_id}")
st.sidebar.markdown("---")
display_backend_status(api_client)

# Main
st.title("📚 Learning Plans")
st.markdown("Quản lý và theo dõi learning plans của bạn")

# Load plans
with st.spinner("Loading plans..."):
    result = api_client.get_user_plans(st.session_state.user_id)

if not result.get("success"):
    show_error(f"Cannot load plans: {result.get('error')}")
    st.stop()

plans = result.get("data", [])

# Filters
col1, col2 = st.columns([1, 3])
with col1:
    status_filter = st.selectbox("Filter by Status", ["All", "active", "completed", "paused"])

filtered_plans = plans if status_filter == "All" else [p for p in plans if p.get("status") == status_filter]

st.markdown("---")

if filtered_plans:
    for plan in filtered_plans:
        with st.expander(f"📋 {plan.get('title', 'Untitled Plan')}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {plan.get('description', 'N/A')}")
                st.caption(f"Created: {format_datetime(plan.get('created_at', ''))}")
                st.caption(f"Total Hours: {plan.get('total_hours', 0)}h")
            
            with col2:
                render_status_badge(plan.get('status', 'unknown'))
                
                # Actions
                if plan.get('status') == 'active':
                    if st.button("⏸ Pause", key=f"pause_{plan['id']}"):
                        result = api_client.update_plan_status(plan['id'], 'paused')
                        if result.get('success'):
                            show_success("Plan paused!")
                            st.rerun()
                elif plan.get('status') == 'paused':
                    if st.button("▶ Resume", key=f"resume_{plan['id']}"):
                        result = api_client.update_plan_status(plan['id'], 'active')
                        if result.get('success'):
                            show_success("Plan resumed!")
                            st.rerun()
            
            # Plan details
            plan_data = plan.get('plan_data', {})
            if plan_data:
                st.json(plan_data)
            
            # Delete button
            if st.button("🗑 Delete Plan", key=f"delete_{plan['id']}"):
                result = api_client.delete_plan(plan['id'])
                if result.get('success'):
                    show_success("Plan deleted!")
                    st.rerun()
                else:
                    show_error(f"Failed: {result.get('error')}")
else:
    show_info("No learning plans found. Chat with AI to create one!")

# Quick actions
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Chat to Create Plan", use_container_width=True):
        st.switch_page("pages/1_💬_Chat.py")
with col2:
    if st.button("👤 View Profile", use_container_width=True):
        st.switch_page("pages/2_👤_Profile.py")