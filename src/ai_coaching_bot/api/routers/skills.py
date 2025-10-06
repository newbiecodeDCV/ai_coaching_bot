"""
Skills router - Skills listing và assessment endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from ...database.models import Skill, Assessment, Course
from ..schemas import SkillResponse, AssessmentRequest, AssessmentResponse, SkillWithStats, ErrorResponse
from ..dependencies import get_db, validate_user_id
from datetime import datetime
import uuid

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/",
           response_model=List[SkillResponse],
           summary="Lấy danh sách tất cả skills",
           description="Endpoint để lấy danh sách tất cả skills có trong hệ thống.")
async def list_skills(
    category: Optional[str] = Query(None, description="Filter theo category"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên skill"),
    limit: int = Query(100, ge=1, le=500, description="Giới hạn số kết quả"),
    offset: int = Query(0, ge=0, description="Offset cho pagination"),
    db: Session = Depends(get_db)
) -> List[SkillResponse]:
    """
    Lấy danh sách tất cả skills.
    
    Args:
        category: Filter theo category
        search: Tìm kiếm theo tên
        limit: Giới hạn số kết quả
        offset: Offset cho pagination
        db: Database session
        
    Returns:
        List của SkillResponse
    """
    try:
        # Build query
        query = db.query(Skill)
        
        # Apply filters
        if category:
            query = query.filter(Skill.category == category)
        
        if search:
            query = query.filter(Skill.name.ilike(f"%{search}%"))
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        skills = query.all()
        
        return [
            SkillResponse(
                id=skill.id,
                name=skill.name,
                description=skill.description,
                category=skill.category,
                level_descriptions=skill.level_descriptions,
                created_at=skill.created_at
            )
            for skill in skills
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{skill_id}",
           response_model=SkillResponse,
           summary="Lấy thông tin chi tiết của skill",
           description="Endpoint để lấy thông tin chi tiết của skill theo skill_id.")
async def get_skill(
    skill_id: str = Path(..., description="ID của skill"),
    db: Session = Depends(get_db)
) -> SkillResponse:
    """
    Lấy thông tin chi tiết của skill.
    
    Args:
        skill_id: ID của skill
        db: Database session
        
    Returns:
        SkillResponse với thông tin chi tiết
        
    Raises:
        HTTPException: 404 nếu skill không tồn tại
    """
    try:
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        
        if not skill:
            raise HTTPException(
                status_code=404,
                detail=f"Skill {skill_id} không tồn tại"
            )
        
        return SkillResponse(
            id=skill.id,
            name=skill.name,
            description=skill.description,
            category=skill.category,
            level_descriptions=skill.level_descriptions,
            created_at=skill.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{skill_id}/stats",
           response_model=SkillWithStats,
           summary="Lấy skill với thống kê",
           description="Endpoint để lấy skill với thống kê về assessments và courses.")
async def get_skill_with_stats(
    skill_id: str = Path(..., description="ID của skill"),
    db: Session = Depends(get_db)
) -> SkillWithStats:
    """
    Lấy skill với thống kê.
    
    Args:
        skill_id: ID của skill
        db: Database session
        
    Returns:
        SkillWithStats với thống kê đầy đủ
        
    Raises:
        HTTPException: 404 nếu skill không tồn tại
    """
    try:
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        
        if not skill:
            raise HTTPException(
                status_code=404,
                detail=f"Skill {skill_id} không tồn tại"
            )
        
        # Get assessment stats
        assessments = db.query(Assessment).filter(Assessment.skill_id == skill_id).all()
        
        total_assessments = len(assessments)
        if assessments:
            average_score = round(sum(a.score for a in assessments) / len(assessments), 1)
            level_distribution = {}
            for level in range(1, 6):
                count = sum(1 for a in assessments if a.level == level)
                level_distribution[f"level_{level}"] = count
        else:
            average_score = 0
            level_distribution = {f"level_{i}": 0 for i in range(1, 6)}
        
        # Get related courses count
        related_courses = db.query(Course).filter(
            Course.skill_ids.contains([skill_id])
        ).count()
        
        stats = {
            "total_assessments": total_assessments,
            "average_score": average_score,
            "level_distribution": level_distribution,
            "related_courses": related_courses
        }
        
        return SkillWithStats(
            id=skill.id,
            name=skill.name,
            description=skill.description,
            category=skill.category,
            level_descriptions=skill.level_descriptions,
            created_at=skill.created_at,
            stats=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{skill_id}/assess",
            response_model=AssessmentResponse,
            summary="Tạo assessment mới cho skill",
            description="Endpoint để tạo assessment mới cho user với skill cụ thể.")
async def create_assessment(
    skill_id: str = Path(..., description="ID của skill"),
    request: AssessmentRequest = ...,
    db: Session = Depends(get_db)
) -> AssessmentResponse:
    """
    Tạo assessment mới cho skill.
    
    Args:
        skill_id: ID của skill
        request: AssessmentRequest với user_id và score
        db: Database session
        
    Returns:
        AssessmentResponse với thông tin assessment mới
        
    Raises:
        HTTPException: 400 cho dữ liệu không hợp lệ, 404 nếu skill không tồn tại
    """
    try:
        # Validate user_id
        user_id = validate_user_id(request.user_id)
        
        # Check skill exists
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise HTTPException(
                status_code=404,
                detail=f"Skill {skill_id} không tồn tại"
            )
        
        # Validate score
        if request.score < 0 or request.score > 100:
            raise HTTPException(
                status_code=400,
                detail="Score phải nằm trong khoảng 0-100"
            )
        
        # Calculate level based on score
        if request.score >= 90:
            level = 5
        elif request.score >= 75:
            level = 4
        elif request.score >= 60:
            level = 3
        elif request.score >= 40:
            level = 2
        else:
            level = 1
        
        # Create new assessment
        new_assessment = Assessment(
            id=str(uuid.uuid4()),
            user_id=user_id,
            skill_id=skill_id,
            score=request.score,
            level=level,
            taken_at=datetime.utcnow()
        )
        
        db.add(new_assessment)
        db.commit()
        db.refresh(new_assessment)
        
        return AssessmentResponse(
            id=new_assessment.id,
            user_id=new_assessment.user_id,
            skill_id=skill_id,
            skill_name=skill.name,
            score=new_assessment.score,
            level=new_assessment.level,
            taken_at=new_assessment.taken_at,
            success=True,
            message="Assessment được tạo thành công"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/",
           response_model=List[dict],
           summary="Lấy danh sách categories",
           description="Endpoint để lấy danh sách tất cả categories và số lượng skills.")
async def get_skill_categories(
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Lấy danh sách categories với số lượng skills.
    
    Args:
        db: Database session
        
    Returns:
        List categories với counts
    """
    try:
        # Get categories with counts
        from sqlalchemy import func
        
        categories = db.query(
            Skill.category,
            func.count(Skill.id).label('count')
        ).group_by(Skill.category).all()
        
        result = []
        for category, count in categories:
            result.append({
                "category": category,
                "skill_count": count
            })
        
        return sorted(result, key=lambda x: x['skill_count'], reverse=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/",
           response_model=List[dict],
           summary="Lấy skills của user với assessment levels",
           description="Endpoint để lấy tất cả skills với assessment levels của user.")
async def get_user_skills(
    user_id: str = Path(..., description="ID của user"),
    category: Optional[str] = Query(None, description="Filter theo category"),
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Lấy skills của user với assessment levels.
    
    Args:
        user_id: ID của user
        category: Filter theo category
        db: Database session
        
    Returns:
        List skills với assessment info
    """
    try:
        # Validate user_id
        user_id = validate_user_id(user_id)
        
        # Build base query cho tất cả skills
        skills_query = db.query(Skill)
        if category:
            skills_query = skills_query.filter(Skill.category == category)
        
        skills = skills_query.all()
        
        # Get user's latest assessments
        from sqlalchemy import func
        latest_assessments = db.query(
            Assessment.skill_id,
            func.max(Assessment.taken_at).label('latest_date')
        ).filter(Assessment.user_id == user_id).group_by(Assessment.skill_id).subquery()
        
        user_assessments = db.query(Assessment).join(
            latest_assessments,
            (Assessment.skill_id == latest_assessments.c.skill_id) &
            (Assessment.taken_at == latest_assessments.c.latest_date)
        ).filter(Assessment.user_id == user_id).all()
        
        # Create lookup dict
        assessment_lookup = {a.skill_id: a for a in user_assessments}
        
        result = []
        for skill in skills:
            assessment = assessment_lookup.get(skill.id)
            
            skill_data = {
                "skill_id": skill.id,
                "skill_name": skill.name,
                "skill_category": skill.category,
                "skill_description": skill.description,
                "current_level": assessment.level if assessment else None,
                "current_score": assessment.score if assessment else None,
                "last_assessed": assessment.taken_at.isoformat() if assessment else None,
                "has_assessment": assessment is not None
            }
            
            result.append(skill_data)
        
        # Sort by assessment status and then by name
        result.sort(key=lambda x: (not x['has_assessment'], x['skill_name']))
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))