"""
Pydantic schemas cho FastAPI requests và responses.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema cho chat request."""
    user_id: str = Field(..., description="ID của user")
    message: str = Field(..., min_length=1, description="Message từ user")
    session_id: Optional[str] = Field(None, description="Session ID (optional)")


class ChatResponse(BaseModel):
    """Schema cho chat response."""
    success: bool = Field(..., description="Trạng thái thành công")
    mode: str = Field(..., description="Mode được phân loại")
    answer: str = Field(..., description="Câu trả lời từ bot")
    citations: List[str] = Field(default_factory=list, description="Trích dẫn nguồn")
    plan: Optional[Dict[str, Any]] = Field(None, description="Kế hoạch học (nếu có)")
    error: Optional[str] = Field(None, description="Thông báo lỗi")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata bổ sung")


class UserProfile(BaseModel):
    """Schema cho user profile."""
    id: str
    name: str
    email: Optional[str] = None
    role: Optional[str] = None
    level: int = Field(ge=1, le=5, description="Level từ 1-5")
    time_budget_per_week: int = Field(ge=1, description="Số giờ/tuần")
    created_at: Optional[datetime] = None


class UserOverview(BaseModel):
    """Schema cho user overview."""
    profile: UserProfile
    assessments: List[Dict[str, Any]] = Field(default_factory=list)
    enrollments: List[Dict[str, Any]] = Field(default_factory=list)
    gaps: List[Dict[str, Any]] = Field(default_factory=list)
    active_plan: Optional[Dict[str, Any]] = None
    stats: Dict[str, Any] = Field(default_factory=dict)


class SkillSearchResponse(BaseModel):
    """Schema cho skill search response."""
    id: str
    name: str
    synonyms: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")


class DocumentUploadRequest(BaseModel):
    """Schema cho document upload request."""
    title: str = Field(..., min_length=1, description="Tên tài liệu")
    skill_id: Optional[str] = Field(None, description="Skill liên quan")


class DocumentUploadResponse(BaseModel):
    """Schema cho document upload response."""
    document_id: int = Field(..., description="ID của document")
    title: str = Field(..., description="Tên tài liệu")
    message: str = Field(..., description="Thông báo")


class DocumentIngestResponse(BaseModel):
    """Schema cho document ingest response."""
    status: str = Field(..., description="Trạng thái ingest")
    chunks_count: int = Field(..., description="Số chunks được tạo")
    message: str = Field(..., description="Thông báo")


class DocumentQueryRequest(BaseModel):
    """Schema cho document query request."""
    query: str = Field(..., min_length=1, description="Câu hỏi tra cứu")
    skill_id: Optional[str] = Field(None, description="Lọc theo skill")
    top_k: int = Field(default=5, ge=1, le=20, description="Số kết quả trả về")


class DocumentQueryResult(BaseModel):
    """Schema cho một kết quả document query."""
    text: str = Field(..., description="Nội dung")
    score: float = Field(..., description="Điểm similarity")
    document_title: str = Field(..., description="Tên tài liệu")
    document_id: int = Field(..., description="ID tài liệu")
    page: Optional[int] = Field(None, description="Số trang")
    citation: str = Field(..., description="Trích dẫn")


class DocumentQueryResponse(BaseModel):
    """Schema cho document query response."""
    results: List[DocumentQueryResult] = Field(default_factory=list)
    total_found: int = Field(..., description="Tổng số kết quả")


class DocumentListItem(BaseModel):
    """Schema cho item trong danh sách documents."""
    id: int
    title: str
    skill_name: Optional[str] = None
    ingested_at: Optional[datetime] = None
    created_at: datetime


class PlanConfirmRequest(BaseModel):
    """Schema cho confirm learning plan."""
    title: str = Field(..., min_length=1, description="Tên kế hoạch")
    items: List[Dict[str, Any]] = Field(..., description="Chi tiết kế hoạch")


class PlanConfirmResponse(BaseModel):
    """Schema cho plan confirm response."""
    plan_id: int = Field(..., description="ID của plan")
    message: str = Field(..., description="Thông báo xác nhận")


class ErrorResponse(BaseModel):
    """Schema cho error response."""
    error: str = Field(..., description="Thông báo lỗi")
    detail: Optional[str] = Field(None, description="Chi tiết lỗi")
    code: Optional[str] = Field(None, description="Mã lỗi")


# Additional schemas for the API routers
class SkillResponse(BaseModel):
    """Schema cho skill response."""
    id: str
    name: str
    description: str
    category: str
    level_descriptions: dict
    created_at: datetime


class SkillWithStats(SkillResponse):
    """Schema cho skill với stats."""
    stats: dict


class AssessmentRequest(BaseModel):
    """Schema cho assessment request."""
    user_id: str
    score: int = Field(ge=0, le=100, description="Score từ 0-100")


class AssessmentResponse(BaseModel):
    """Schema cho assessment response."""
    id: str
    user_id: str
    skill_id: str
    skill_name: str
    score: int
    level: int
    taken_at: datetime
    success: bool
    message: str


class DocumentResponse(BaseModel):
    """Schema cho document response."""
    id: str
    title: str
    description: str
    doc_type: str
    file_path: str
    file_size: int
    is_indexed: bool
    tags: List[str]
    created_at: datetime
    updated_at: datetime


class DocumentSearchRequest(BaseModel):
    """Schema cho document search request."""
    query: str = Field(..., min_length=3, description="Query string")
    top_k: int = Field(5, ge=1, le=20, description="Number of results")
    score_threshold: float = Field(0.3, ge=0.0, le=1.0, description="Score threshold")


class DocumentSearchResponse(BaseModel):
    """Schema cho document search response."""
    query: str
    total_results: int
    results: List[dict]
    documents: List[dict]
    success: bool
    message: str


class ExecuteResponse(BaseModel):
    """Schema cho execute response."""
    response: str
    metadata: dict
    success: bool
    error: Optional[str] = None
    route_info: dict


class RouteResponse(BaseModel):
    """Schema cho route response."""
    intent: str
    confidence: float
    success: bool
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Schema cho health check response."""
    status: str = Field(..., description="Trạng thái service")
    timestamp: datetime = Field(..., description="Thời gian check")
    version: str = Field(..., description="Phiên bản")
    components: Dict[str, str] = Field(default_factory=dict, description="Trạng thái các component")
