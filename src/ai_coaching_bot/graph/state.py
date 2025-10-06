"""
State schema cho LangGraph workflow.
"""
from typing import TypedDict, Optional, List, Dict, Any


class GraphState(TypedDict):
    """
    State cho LangGraph workflow.
    
    Attributes:
        user_id: ID của user
        mode: Chế độ hoạt động (coach_general|coach_skill|performance|docs_qa)
        message: Message từ user
        user_profile: Thông tin profile user
        assessments: Danh sách đánh giá kỹ năng
        enrollments: Danh sách khóa học đã/đang học
        skill_query: Skill user muốn học (nếu có)
        target_level: Target level mong muốn
        time_budget: Số giờ/tuần có thể học
        gaps: Danh sách gaps cần cải thiện
        recommendations: Danh sách khóa học đề xuất
        plan: Kế hoạch học được tạo
        docs_results: Kết quả tra cứu tài liệu
        answer: Câu trả lời cuối cùng
        citations: Danh sách trích dẫn
        error: Thông báo lỗi (nếu có)
    """
    # Core
    user_id: str
    mode: str
    message: str
    
    # User data
    user_profile: Optional[Dict[str, Any]]
    assessments: List[Dict[str, Any]]
    enrollments: List[Dict[str, Any]]
    
    # Coaching specific
    skill_query: Optional[str]
    target_level: Optional[int]
    time_budget: Optional[int]
    
    # Analysis
    gaps: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    plan: Optional[Dict[str, Any]]
    
    # Docs QA
    docs_results: List[Dict[str, Any]]
    
    # Output
    answer: str
    citations: List[str]
    error: Optional[str]
