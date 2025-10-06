"""
UI Helpers - Styling và utility functions cho Streamlit UI.
"""
import streamlit as st
from typing import Optional, Dict, Any
from datetime import datetime


def init_session_state():
    """Initialize session state variables."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = "user_001"  # Default user
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "current_plan" not in st.session_state:
        st.session_state.current_plan = None


def show_success(message: str):
    """Display success message."""
    st.success(f"✅ {message}")


def show_error(message: str):
    """Display error message."""
    st.error(f"❌ {message}")


def show_warning(message: str):
    """Display warning message."""
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    """Display info message."""
    st.info(f"ℹ️ {message}")


def format_datetime(dt_str: str) -> str:
    """
    Format datetime string to readable format.
    
    Args:
        dt_str: ISO format datetime string
        
    Returns:
        Formatted datetime string
    """
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return dt_str


def render_metric_card(title: str, value: Any, delta: Optional[str] = None, icon: str = "📊"):
    """
    Render metric card.
    
    Args:
        title: Metric title
        value: Metric value
        delta: Delta value (optional)
        icon: Icon emoji
    """
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<div style='font-size: 40px;'>{icon}</div>", unsafe_allow_html=True)
    with col2:
        if delta:
            st.metric(label=title, value=value, delta=delta)
        else:
            st.metric(label=title, value=value)


def render_progress_bar(progress: float, label: str = "Progress"):
    """
    Render progress bar.
    
    Args:
        progress: Progress value (0-100)
        label: Label for progress bar
    """
    st.markdown(f"**{label}**")
    st.progress(progress / 100)
    st.caption(f"{progress:.1f}%")


def render_skill_badge(skill_name: str, level: int, color: str = "blue"):
    """
    Render skill badge.
    
    Args:
        skill_name: Name of skill
        level: Skill level (1-5)
        color: Badge color
    """
    stars = "⭐" * level
    st.markdown(
        f"<span style='background-color: {color}; color: white; padding: 5px 10px; "
        f"border-radius: 15px; margin: 5px;'>{skill_name} {stars}</span>",
        unsafe_allow_html=True
    )


def get_level_color(level: int) -> str:
    """
    Get color based on skill level.
    
    Args:
        level: Skill level (1-5)
        
    Returns:
        Color hex code
    """
    colors = {
        1: "#FF4B4B",  # Red
        2: "#FFA500",  # Orange
        3: "#FFD700",  # Yellow
        4: "#90EE90",  # Light green
        5: "#00C853"   # Green
    }
    return colors.get(level, "#808080")


def render_status_badge(status: str):
    """
    Render status badge.
    
    Args:
        status: Status string
    """
    status_colors = {
        "active": "#00C853",
        "completed": "#1976D2",
        "paused": "#FFA500",
        "enrolled": "#9C27B0",
        "in_progress": "#2196F3"
    }
    
    color = status_colors.get(status.lower(), "#808080")
    st.markdown(
        f"<span style='background-color: {color}; color: white; padding: 3px 8px; "
        f"border-radius: 10px; font-size: 12px;'>{status.upper()}</span>",
        unsafe_allow_html=True
    )


def render_course_card(course: Dict[str, Any]):
    """
    Render course card.
    
    Args:
        course: Course dictionary
    """
    with st.container():
        st.markdown(
            f"""
            <div style='border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; margin: 10px 0;'>
                <h4>{course.get('title', 'Unknown Course')}</h4>
                <p><b>Provider:</b> {course.get('provider', 'N/A')}</p>
                <p><b>Duration:</b> {course.get('duration_hours', 0)} hours</p>
                <p><b>Level:</b> {course.get('level', 'N/A')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_gap_card(gap: Dict[str, Any]):
    """
    Render skill gap card.
    
    Args:
        gap: Gap dictionary
    """
    skill_name = gap.get("skill_name", gap.get("skill_id", "Unknown"))
    current = gap.get("current_level", 0)
    expected = gap.get("expected_level", 0)
    gap_value = gap.get("gap", expected - current)
    
    st.markdown(
        f"""
        <div style='border-left: 4px solid #FF4B4B; padding: 10px; margin: 10px 0; background-color: #FFF3F3;'>
            <b>{skill_name}</b><br>
            Current: Level {current} | Expected: Level {expected} | Gap: {gap_value} levels
        </div>
        """,
        unsafe_allow_html=True
    )


def apply_custom_css():
    """Apply custom CSS styling."""
    st.markdown(
        """
        <style>
        /* Main container */
        .main {
            padding: 2rem;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #f8f9fa;
        }
        
        /* Buttons */
        .stButton>button {
            border-radius: 20px;
            border: none;
            padding: 0.5rem 2rem;
            font-weight: 600;
        }
        
        /* Cards */
        .element-container {
            margin-bottom: 1rem;
        }
        
        /* Headers */
        h1 {
            color: #1976D2;
            padding-bottom: 1rem;
            border-bottom: 3px solid #1976D2;
        }
        
        h2 {
            color: #424242;
            margin-top: 2rem;
        }
        
        /* Chat messages */
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        
        .user-message {
            background-color: #E3F2FD;
            margin-left: 20%;
        }
        
        .bot-message {
            background-color: #F5F5F5;
            margin-right: 20%;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
        }
        
        /* Progress bars */
        .stProgress > div > div {
            background-color: #1976D2;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background-color: #f8f9fa;
            border-radius: 10px;
            font-weight: 600;
        }
        
        /* Dataframes */
        .dataframe {
            font-size: 14px;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def check_backend_connection(api_client) -> bool:
    """
    Check if backend is reachable.
    
    Args:
        api_client: APIClient instance
        
    Returns:
        True if connected, False otherwise
    """
    result = api_client.health_check()
    return result.get("success", False)


def display_backend_status(api_client):
    """
    Display backend connection status.
    
    Args:
        api_client: APIClient instance
    """
    result = api_client.health_check()
    
    if result.get("success"):
        data = result.get("data", {})
        status = data.get("status", "unknown")
        
        if status == "healthy":
            st.sidebar.success("🟢 Backend: Connected")
        else:
            st.sidebar.warning("🟡 Backend: Degraded")
    else:
        st.sidebar.error("🔴 Backend: Disconnected")
        st.sidebar.caption("Make sure FastAPI server is running on port 8000")


def paginate_results(items: list, page: int, per_page: int = 10):
    """
    Paginate list of items.
    
    Args:
        items: List of items
        page: Current page (1-indexed)
        per_page: Items per page
        
    Returns:
        Tuple of (paginated_items, total_pages)
    """
    total_pages = (len(items) + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return items[start_idx:end_idx], total_pages